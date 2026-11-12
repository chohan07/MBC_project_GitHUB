
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