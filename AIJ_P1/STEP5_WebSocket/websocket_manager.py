
from fastapi import WebSocket


class ConnectionManager:
    """WebSocket 연결을 관리하는 클래스"""

    def __init__(self):
        # 현재 연결된 웹브라우저 목록
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        # WebSocket 연결 요청 수락
        await websocket.accept()

        # 연결된 브라우저를 목록에 추가
        self.active_connections.append(websocket)

        print("WebSocket 연결 성공")

    def disconnect(self, websocket: WebSocket):
        # 연결이 끊어진 브라우저 제거
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

        print("WebSocket 연결 종료")

    async def broadcast(self, data: dict):
        # 연결된 모든 브라우저에 데이터 전송
        for connection in self.active_connections.copy():
            try:
                await connection.send_json(data)
            except Exception:
                self.disconnect(connection)


# WebSocket 연결 관리자 생성
manager = ConnectionManager()
