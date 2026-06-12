from flask import Flask
from flask_socketio import SocketIO, join_room, leave_room, emit

class AppState:
    def __init__(self, app: Flask, socketio: SocketIO):
        self.app = app
        self.socketio = socketio

        self.rooms = {}
        self.player_room = {}

    def remove_player_from_room(self, sid):
        room_code = self.player_room.get(sid)

        if not room_code:
            return

        if room_code in self.rooms:
            if sid in self.rooms[room_code]["players"]:
                self.rooms[room_code]["players"].remove(sid)

            if not self.rooms[room_code]["players"]:
                del self.rooms[room_code]

        leave_room(room_code)
        self.player_room.pop(sid, None)

    def join_player_to_room(self, sid, code):
        self.remove_player_from_room(sid)

        self.rooms[code]["players"].append(sid)
        self.player_room[sid] = code

        join_room(code)

    def broadcast_rooms(self):
        data = {
            code: {
                "players": len(room["players"]),
                "host": room["host"]
            }
            for code, room in self.rooms.items()
            if room["phase"] == "waiting_room"
        }

        self.socketio.emit("rooms_list", data, room="lobby")

    def is_in_room(self, sid):
        if sid not in self.player_room:
            emit("error", {"msg": "Not in any room"})
            return False
        return True

    def is_host_of_room(self, sid):
        if self.rooms[self.player_room[sid]]["host"] != sid:
            emit("error", {"msg": "Not host of the room"})
            return False
        return True
