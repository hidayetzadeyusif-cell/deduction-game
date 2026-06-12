from flask import request
from flask_socketio import join_room, emit

from random import choice
from string import ascii_uppercase

from logic.app_state import AppState

def register_events(app_state: AppState):
    def generate_room_code():
        while True:
            code = "".join(choice(ascii_uppercase) for _ in range(6))

            if code not in app_state.rooms:
                return code
    
    @app_state.socketio.on("create_room")
    def on_create_room():
        sid = request.sid

        code = generate_room_code()
        app_state.rooms[code] = {
            "host": sid,
            "players": [],
            "phase": "waiting_room",
            "game_state": None
        }

        app_state.join_player_to_room(sid, code)

        emit("joined_room", {
            "code": code, 
            "is_host": True
        })
        
        app_state.broadcast_rooms()


    @app_state.socketio.on("join_room")
    def on_join_room(data):
        sid = request.sid
        code = data["code"]

        if code not in app_state.rooms:
            emit("error", {"msg": "Room doesn't exist"})
            return

        app_state.join_player_to_room(sid, code)

        emit("joined_room", {
            "code": code, 
            "is_host": app_state.rooms[code]["host"] == sid
        })

        app_state.broadcast_rooms()

    @app_state.socketio.on("leave_room")
    def on_leave_room():
        sid = request.sid

        app_state.remove_player_from_room(sid)

        join_room("lobby")

        emit("left_room", room="lobby")

        app_state.broadcast_rooms()
