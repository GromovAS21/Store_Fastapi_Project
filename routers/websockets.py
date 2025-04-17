from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect

from websocket import ConnectionManager

router = APIRouter(prefix="", tags=["websockets"])

manager = ConnectionManager()

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client {client_id}: {data}")
    except WebSocketDisconnect as e:
        manager.connections.remove(websocket)
        print(f'Connection closed {e.code}')