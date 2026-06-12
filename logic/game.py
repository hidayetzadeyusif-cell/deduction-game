from flask import request
from flask_socketio import emit

from logic.app_state import AppState
from logic.engine import GameState, Player, Decision
from logic.engine import get_player, simulate_night
from logic.engine import assign_roles_randomly, get_valid_peek_targets, get_valid_destinations

from random import shuffle

MIN_PLAYERS = 3 # supposed to be 6, this is for testing

def register_events(app_state: AppState):
    @app_state.socketio.on("start_game")
    def on_start_game():
        sid = request.sid

        if not app_state.is_in_room(sid): return

        code = app_state.player_room[sid]
        room = app_state.rooms[code]

        if not app_state.is_host_of_room(sid): return
        if len(room["players"]) < MIN_PLAYERS:
            emit("error", {"msg": "Not enough players"})
            return
        
        room["phase"] = "game"
        room["game_state"] = GameState(
            [Player(sid, sid, None) for sid in room["players"]]
        )

        # most likely temporary
        assign_roles_randomly(room["game_state"], {
            "citizen": len(room["players"]) - 1, 
            "mafia": 1
        })

        for player_sid in room["players"]:
            emit("start_submissions", {
                "is_host": sid == player_sid,
                "role": get_player(room["game_state"], player_sid).role,
                "is_alive": get_player(room["game_state"], player_sid).alive,
                "peek_targets": get_valid_peek_targets(room["game_state"], player_sid),
                "destinations": get_valid_destinations(room["game_state"], player_sid)
            }, to=player_sid)

        app_state.broadcast_rooms()

    @app_state.socketio.on("end_game")
    def on_end_game():
        sid = request.sid
        
        if not app_state.is_in_room(sid): return
        if not app_state.is_host_of_room(sid): return

        code = app_state.player_room[sid]

        emit("game_ended", room=code)

        app_state.broadcast_rooms()

    @app_state.socketio.on("submit_decision")
    def on_submit_decision(data):
        sid = request.sid

        if not app_state.is_in_room(sid): return

        code = app_state.player_room[sid]
        room = app_state.rooms[code]

        if room["phase"] != "game":
            emit("error", {"msg": "Game not started"})
            return
        
        player = get_player(room["game_state"], sid)

        if not player.alive:
            emit("error", {"msg": "Currently dead"})
            return

        if player.decision is not None:
            emit("error", {"msg": "Already submitted"})
            return

        if data["action_mode"] not in {"peek", "travel"}:
            emit("error", {"msg": "Invalid action mode"})
            return
        
        if data["action_mode"] == "peek":
            if data["peek_target"] not in get_valid_peek_targets(room["game_state"], sid):
                emit("error", {"msg": "Invalid peek target"})
                return
        
        if data["action_mode"] == "travel":
            if data["destination"] not in get_valid_destinations(room["game_state"], sid):
                emit("error", {"msg": "Invalid travel destination"})
                return
            if data["departure"] not in {"early", "late"}:
                emit("error", {"msg": "Invalid departure time"})
                return
        
        player.decision = Decision(
            data["action_mode"], 
            destination=data["destination"], 
            departure=data["departure"], 
            peek_target=data["peek_target"]
        )

        emit("submission_accepted")

        completed = True
        for player in room["game_state"].players:
            if player.decision is None: completed = False
        
        if completed:
            submissions_completed(app_state, code)
    
    def submissions_completed(app_state: AppState, code: str):
        room = app_state.rooms[code]

        result = simulate_night(room["game_state"])

        print("Events: ", result["events"])

        deaths = [
            death.id # get_player(room["game_state"], death.id)
            for death in room["game_state"].deaths
            if death.night == room["game_state"].night
        ]

        for player_id, observations in result["intel"]:
            shuffle(observations)
            
            emit("start_simulation", {
                "deaths": deaths,
                "observations": [ob.message for ob in observations]
            }, to=player_id)
        
        print("ignoring discussion...") # TODO: DON'T ignore discussion
        
        for player in room["game_state"].players: player.decision = None

        room["game_state"].night += 1
