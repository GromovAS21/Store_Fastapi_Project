from typing import List

from starlette.websockets import WebSocket


class ConnectionManager:
    """
    Класс для работы с вебсокетами.
    """

    def __init__(self):
        self.connections: List[WebSocket] = []
        print("Creating a list to active connections", self.connections)

    async def connect(self, websocket:WebSocket):
        """
        Метод для подключения вебсокета.
        """
        await websocket.accept()
        self.connections.append(websocket)
        print("New Active connections are ", self.connections)

    async def broadcast(self, data: str):
        """
        Метод для отправки сообщений всем активным вебсокетам.
        """
        for connection in self.connections:
            await connection.send_text(data)
            print("In broadcast: sent msg to ", connection)