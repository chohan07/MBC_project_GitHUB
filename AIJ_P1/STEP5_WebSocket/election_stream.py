
from pathlib import Path
import pandas as pd

# 프로젝트 기본 경로
BASE_DIR = Path(__file__).resolve().parent.parent

# STEP 2에서 만든 가상 선거 데이터
DATA_FILE = BASE_DIR / "STEP2_Data" / "election_results.csv"


def load_election_data():
    """가상 선거 CSV 데이터를 불러온다."""
    df = pd.read_csv(DATA_FILE)

    # 개표 단계, 지역, 후보 순으로 정렬
    df = df.sort_values(
        by=["step", "region_id", "candidate_id"]
    )

    return df


def get_step_data(step: int):
    """특정 개표 단계의 데이터를 반환한다."""
    df = load_election_data()

    # 요청한 개표 단계만 선택
    step_df = df[df["step"] == step]

    if step_df.empty:
        raise ValueError(f"개표 단계 {step}의 데이터가 없습니다.")

    # CSV 값을 JSON 전송 가능한 형태로 변환
    records = step_df.to_dict(orient="records")

    return {
        "type": "election_update",
        "mode": "교육용 가상 선거",
        "election": "2026 한빛시 시장 선거",
        "step": step,
        "total_steps": 10,
        "timestamp": str(step_df["timestamp"].iloc[0]),
        "total_rows": len(records),
        "data": records
    }


# 직접 실행했을 때 데이터 확인
if __name__ == "__main__":
    result = get_step_data(1)

    print("개표 단계:", result["step"])
    print("데이터 기준시각:", result["timestamp"])
    print("데이터 행 수:", result["total_rows"])
    print("전송 유형:", result["type"])
