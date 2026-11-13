
from fastapi import FastAPI

# FastAPI 웹 서버 생성
app = FastAPI(
    title="AIJ_P1 가상 선거 개표 대시보드",
    description="2026 한빛시 시장 선거 교육용 시뮬레이션",
    version="1.0.0"
)

# 기본 접속 화면
@app.get("/")
def home():
    return {
        "project": "AIJ_P1",
        "title": "2026 한빛시 시장 선거",
        "message": "FastAPI 서버 정상 작동",
        "mode": "교육용 가상 선거",
        "status": "success"
    }


from pathlib import Path
import pandas as pd

# STEP 2 데이터 파일 위치
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "STEP2_Data" / "election_results.csv"


# 가상 선거 데이터 조회 API
@app.get("/api/election-results")
def get_election_results():
    df = pd.read_csv(DATA_FILE)

    return {
        "election": "2026 한빛시 시장 선거",
        "mode": "교육용 가상 선거",
        "total_rows": len(df),
        "data": df.to_dict(orient="records")
    }


from fastapi.responses import HTMLResponse

# HTML 대시보드 화면
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    html_file = Path(__file__).resolve().parent / "templates" / "index.html"

    return HTMLResponse(
        content=html_file.read_text(encoding="utf-8")
    )

from fastapi.staticfiles import StaticFiles

# CSS, JavaScript 등 정적 파일 연결
STATIC_DIR = Path(__file__).resolve().parent / "static"

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)


# ============================================
# STEP 5 - WebSocket 연결 기능
# ============================================

import sys

from fastapi import WebSocket, WebSocketDisconnect

# STEP5_WebSocket 폴더의 모듈을 불러오기 위한 경로 설정
sys.path.insert(0, str(BASE_DIR))

from STEP5_WebSocket.websocket_manager import manager



# STEP 5-13: 실제 개표 데이터 전송
from STEP5_WebSocket.election_stream import get_step_data



# STEP 5-15: 10단계 자동 개표 데이터 전송

import asyncio

from STEP5_WebSocket.election_stream import get_step_data



# STEP 5-17: WebSocket 재생 제어 기능

import asyncio
from contextlib import suppress

from STEP5_WebSocket.election_stream import get_step_data


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    current_step = 0
    is_paused = False
    playback_task = None
    playback_lock = asyncio.Lock()

    async def play_election():
        nonlocal current_step, is_paused

        try:
            while current_step < 10:
                if is_paused:
                    await asyncio.sleep(0.1)
                    continue

                async with playback_lock:
                    if is_paused:
                        continue

                    next_step = current_step + 1
                    result = get_step_data(next_step)

                    await websocket.send_json(result)
                    current_step = next_step

                    print(f"개표 {current_step}/10 단계 전송 완료")

                if current_step < 10:
                    await asyncio.sleep(2)

            if current_step == 10:
                await websocket.send_json({
                    "type": "election_complete",
                    "message": "가상 선거 개표 완료",
                    "mode": "교육용 가상 선거"
                })

        except asyncio.CancelledError:
            raise

    async def stop_playback():
        nonlocal playback_task

        if playback_task and not playback_task.done():
            playback_task.cancel()
            with suppress(asyncio.CancelledError):
                await playback_task

        playback_task = None

    try:
        while True:
            command = await websocket.receive_text()
            command = command.strip().lower()

            if command == "start":
                await stop_playback()

                async with playback_lock:
                    current_step = 0
                    is_paused = False

                playback_task = asyncio.create_task(play_election())

            elif command == "pause":
                is_paused = True

                await websocket.send_json({
                    "type": "playback_status",
                    "status": "paused",
                    "step": current_step
                })

            elif command == "resume":
                is_paused = False

                if playback_task is None or playback_task.done():
                    if current_step < 10:
                        playback_task = asyncio.create_task(
                            play_election()
                        )

                await websocket.send_json({
                    "type": "playback_status",
                    "status": "playing",
                    "step": current_step
                })

            elif command == "reset":
                await stop_playback()

                async with playback_lock:
                    current_step = 0
                    is_paused = False

                await websocket.send_json({
                    "type": "playback_status",
                    "status": "reset",
                    "step": 0
                })

            else:
                await websocket.send_json({
                    "type": "error",
                    "message": "지원하지 않는 명령입니다.",
                    "mode": "교육용 가상 선거"
                })

    except WebSocketDisconnect:
        print("WebSocket 연결 종료")

    finally:
        await stop_playback()
        manager.disconnect(websocket)
