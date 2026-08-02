from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:

    def __init__(self):
        self.connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(
        self,
        user_id: str,
        websocket: WebSocket,
    ):
        await websocket.accept()
        self.connections[user_id].add(websocket)

    def disconnect(
        self,
        user_id: str,
        websocket: WebSocket,
    ):
        if user_id not in self.connections:
            return

        self.connections[user_id].discard(websocket)

        if not self.connections[user_id]:
            del self.connections[user_id]

    async def send_notification(
        self,
        user_id: str,
        payload: dict,
    ):

        sockets = self.connections.get(user_id)

        if not sockets:
            return

        dead = []

        for ws in sockets:
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)

        for ws in dead:
            self.disconnect(user_id, ws)


manager = ConnectionManager()