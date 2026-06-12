from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room

from logic.app_state import AppState
from logic.rooms import register_events as register_room_events
from logic.game import register_events as register_game_events

app = Flask(__name__)
socketio = SocketIO(app)

app_state = AppState(app, socketio)


@app_state.app.route("/")
def index():
    return render_template("index.html")



@app_state.socketio.on("connect")
def on_connect():
    sid = request.sid
    print(f"Connected: {sid}")
    join_room("lobby")
    app_state.broadcast_rooms()

@app_state.socketio.on("disconnect")
def on_disconnect():
    app_state.remove_player_from_room(request.sid)
    app_state.broadcast_rooms()
    print(f"Disconnected: {request.sid}")

    
register_room_events(app_state)
register_game_events(app_state)


if __name__ == "__main__":
    app_state.socketio.run(app_state.app, debug=True)

'''
TODO:

ALSO SEE:
- Host reassignment when host leaves
- EXPLICITLY support leaving while in game
- Think about decision selection (should there be a timer?)
'''