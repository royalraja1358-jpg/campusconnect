from fastapi import WebSocket
from typing import Dict, List
import json

class ConnectionManager:
    def __init__(self):
        # user_id -> list of active websockets
        self.user_connections: Dict[int, List[WebSocket]] = {}
        # group_name -> list of websockets
        self.group_connections: Dict[str, List[WebSocket]] = {}

    async def connect_user(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(websocket)

    def disconnect_user(self, websocket: WebSocket, user_id: int):
        if user_id in self.user_connections:
            self.user_connections[user_id] = [
                ws for ws in self.user_connections[user_id] if ws != websocket
            ]
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

    async def join_group(self, websocket: WebSocket, group_name: str):
        if group_name not in self.group_connections:
            self.group_connections[group_name] = []
        if websocket not in self.group_connections[group_name]:
            self.group_connections[group_name].append(websocket)

    def leave_group(self, websocket: WebSocket, group_name: str):
        if group_name in self.group_connections:
            self.group_connections[group_name] = [
                ws for ws in self.group_connections[group_name] if ws != websocket
            ]

    async def send_to_user(self, user_id: int, data: dict):
        """Send a message to all connections of a specific user."""
        sockets = self.user_connections.get(user_id, [])
        dead = []
        for ws in sockets:
            try:
                await ws.send_text(json.dumps(data))
            except Exception:
                dead.append(ws)
        for ws in dead:
            sockets.remove(ws)

    async def broadcast_to_group(self, group_name: str, data: dict, exclude: WebSocket = None):
        """Broadcast to all members of a group."""
        sockets = self.group_connections.get(group_name, [])
        dead = []
        for ws in sockets:
            if ws == exclude:
                continue
            try:
                await ws.send_text(json.dumps(data))
            except Exception:
                dead.append(ws)
        for ws in dead:
            sockets.remove(ws)

    async def broadcast_to_all(self, data: dict):
        """Broadcast to every connected client (admin announcements)."""
        for user_id, sockets in list(self.user_connections.items()):
            for ws in sockets:
                try:
                    await ws.send_text(json.dumps(data))
                except Exception:
                    pass

manager = ConnectionManager()
