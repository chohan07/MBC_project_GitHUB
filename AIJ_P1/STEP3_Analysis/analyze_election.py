
from pathlib import Path
import pandas as pd

# STEP 2 데이터 폴더
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "STEP2_Data"

# CSV 불러오기
candidates = pd.read_csv(DATA_DIR / "candidates.csv")
regions = pd.read_csv(DATA_DIR / "regions.csv")
results = pd.read_csv(DATA_DIR / "election_results.csv")

# 데이터 확인
print("=== 후보 데이터 ===")
print(candidates.head())

print("\n=== 지역 데이터 ===")
print(regions.head())

print("\n=== 개표 데이터 ===")
print(results.head())

print("\n=== 데이터 크기 ===")
print("후보:", candidates.shape)
print("지역:", regions.shape)
print("개표:", results.shape)

print("\n=== 개표 데이터 열 이름 ===")
print(results.columns.tolist())


# STEP 3-2. 데이터 기본 검증

print("\n=== STEP 3-2 데이터 검증 ===")

# 1. 누락된 데이터 검사
print("\n[1] 결측값 검사")
print(results.isnull().sum())

# 2. 중복 행 ID 검사
print("\n[2] 중복 row_id 검사")
print("중복 건수:", results["row_id"].duplicated().sum())

# 3. 후보 및 지역 ID 검사
print("\n[3] 후보 및 지역 ID 검사")
candidate_ids = set(candidates["candidate_id"])
region_ids = set(regions["region_id"])

invalid_candidates = ~results["candidate_id"].isin(candidate_ids)
invalid_regions = ~results["region_id"].isin(region_ids)

print("잘못된 후보 ID:", invalid_candidates.sum())
print("잘못된 지역 ID:", invalid_regions.sum())

# 4. 음수 득표수 검사
print("\n[4] 음수 득표수 검사")
print("음수 득표 행:", (results["votes"] < 0).sum())

# 5. 개표 단계 확인
print("\n[5] 개표 단계 검사")
print("개표 단계:", sorted(results["step"].unique()))
print("단계별 데이터 수:")
print(results.groupby("step").size())


# STEP 3-3. 후보별 최종 득표 분석

print("\n=== STEP 3-3 후보별 최종 득표 분석 ===")

# 마지막 개표 단계만 선택
final_step = results["step"].max()
final_data = results[results["step"] == final_step]

# 후보별 득표수 합계
candidate_votes = (
    final_data.groupby("candidate_name")["votes"]
    .sum()
    .sort_values(ascending=False)
)

# 전체 유효투표수
total_valid_votes = candidate_votes.sum()

# 후보별 득표율 계산
vote_rates = candidate_votes / total_valid_votes * 100

# 분석 결과표 생성
summary = pd.DataFrame({
    "득표수": candidate_votes,
    "득표율(%)": vote_rates.round(2)
})

# 순위 추가
summary.insert(0, "순위", range(1, len(summary) + 1))

print("\n[최종 개표 결과]")
print(summary)

print("\n전체 유효투표수:", total_valid_votes)

# 1위와 2위 격차
first = summary.iloc[0]
second = summary.iloc[1]

print("\n[1위와 2위 격차]")
print("득표수 차이:", int(first["득표수"] - second["득표수"]))
print("득표율 차이(%p):",
      round(first["득표율(%)"] - second["득표율(%)"], 2))


# STEP 3-4. 지역별 득표 분석

print("\n=== STEP 3-4 지역별 득표 분석 ===")

# 최종 개표 단계의 지역별 후보 득표수
regional_votes = final_data.pivot_table(
    index="region",
    columns="candidate_name",
    values="votes",
    aggfunc="sum",
    fill_value=0
)

# 지역별 유효투표수
regional_totals = regional_votes.sum(axis=1)

# 지역별 후보 득표율
regional_rates = (
    regional_votes.div(regional_totals, axis=0) * 100
).round(2)

# 각 지역의 1위 후보
regional_winners = regional_votes.idxmax(axis=1)

print("\n[1] 지역별 후보 득표수")
print(regional_votes)

print("\n[2] 지역별 후보 득표율(%)")
print(regional_rates)

print("\n[3] 지역별 1위 후보")
print(regional_winners)

print("\n[4] 후보별 지역 1위 횟수")
print(regional_winners.value_counts())

# 전체 유효투표수와 비교
print("\n[5] 지역별 득표 합계 검증")
print("지역별 합계:", regional_totals.sum())
print("전체 유효투표수:", total_valid_votes)

if regional_totals.sum() == total_valid_votes:
    print("검증 성공: 득표수 합계 일치")
else:
    print("검증 실패: 득표수 합계 불일치")


# STEP 3-5. 개표 단계별 순위 변화 분석

print("\n=== STEP 3-5 개표 단계별 순위 분석 ===")

# 단계별 후보 누적 득표수
step_votes = results.pivot_table(
    index="step",
    columns="candidate_name",
    values="votes",
    aggfunc="sum",
    fill_value=0
).sort_index()

# 각 단계별 전체 유효투표수
step_totals = step_votes.sum(axis=1)

# 단계별 후보 득표율
step_rates = (
    step_votes.div(step_totals, axis=0) * 100
).round(2)

# 단계별 1위 후보
step_leaders = step_votes.idxmax(axis=1)

print("\n[1] 단계별 후보 득표율(%)")
print(step_rates)

print("\n[2] 단계별 1위 후보")
print(step_leaders)

# 선두 후보 변경 여부
leader_changes = step_leaders.ne(step_leaders.shift())
leader_changes.iloc[0] = False

print("\n[3] 선두 변경 단계")
if leader_changes.any():
    for step in step_leaders.index[leader_changes]:
        print(f"{step}단계: {step_leaders.loc[step]} 후보 선두")
else:
    print("선두 변경 없음")

# 마지막 단계 득표수 검증
print("\n[4] 최종 득표수 검증")

if step_votes.iloc[-1].sum() == total_valid_votes:
    print("검증 성공: 최종 유효투표수 일치")
else:
    print("검증 실패: 최종 유효투표수 불일치")


# STEP 3-6. 개표 추이 그래프 제작

import matplotlib.pyplot as plt

print("\n=== STEP 3-6 그래프 제작 ===")

# 그래프 저장 폴더
OUTPUT_DIR = BASE_DIR / "STEP3_Analysis" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Windows 한글 폰트 설정
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

# 후보별 색상
candidate_colors = {
    "이몽룡": "#2563EB",
    "심청이": "#DC2626",
    "홍길동": "#16A34A"
}

# 그래프 생성
plt.figure(figsize=(12, 6))

for candidate in step_rates.columns:
    plt.plot(
        step_rates.index,
        step_rates[candidate],
        marker="o",
        linewidth=2.5,
        label=candidate,
        color=candidate_colors[candidate]
    )

plt.title(
    "2026 한빛시 시장선거 - 개표 단계별 득표율",
    fontsize=16
)
plt.xlabel("개표 단계")
plt.ylabel("득표율 (%)")
plt.xticks(range(1, 11))
plt.ylim(0, 70)
plt.grid(True, alpha=0.3)
plt.legend()
plt.figtext(
    0.5, 0.01,
    "가상 선거 · 교육용 시뮬레이션",
    ha="center",
    fontsize=10
)

plt.tight_layout(rect=[0, 0.04, 1, 1])

# PNG 저장
output_file = OUTPUT_DIR / "vote_trend.png"
plt.savefig(output_file, dpi=200)

print("그래프 저장 완료:", output_file)

plt.show()


# STEP 3-7. 분석 결과 파일 저장

print("\n=== STEP 3-7 분석 결과 저장 ===")

# 1. 후보별 최종 결과
summary.to_csv(
    OUTPUT_DIR / "candidate_summary.csv",
    encoding="utf-8-sig"
)

# 2. 지역별 후보 득표수
regional_votes.to_csv(
    OUTPUT_DIR / "regional_summary.csv",
    encoding="utf-8-sig"
)

# 3. 단계별 후보 득표율
step_rates.to_csv(
    OUTPUT_DIR / "step_trend.csv",
    encoding="utf-8-sig"
)

# 4. 최종 분석 결과 JSON
import json

analysis_result = {
    "project": "AIJ_P1",
    "election": "2026 한빛시 시장선거",
    "data_type": "synthetic",
    "final_step": int(final_step),
    "total_valid_votes": int(total_valid_votes),
    "winner": str(summary.index[0]),
    "winner_votes": int(summary.iloc[0]["득표수"]),
    "winner_vote_rate": float(
        summary.iloc[0]["득표율(%)"]
    ),
    "vote_margin": int(
        first["득표수"] - second["득표수"]
    ),
    "leader_change_steps": [
        int(step)
        for step in step_leaders.index[leader_changes]
    ]
}

with open(
    OUTPUT_DIR / "analysis_result.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        analysis_result,
        f,
        ensure_ascii=False,
        indent=4
    )

print("저장 완료!")
print("저장 폴더:", OUTPUT_DIR)

for filename in [
    "candidate_summary.csv",
    "regional_summary.csv",
    "step_trend.csv",
    "analysis_result.json"
]:
    print(" -", filename)


# STEP 3-8. 뉴스 보도용 분석 보고서 생성

print("\n=== STEP 3-8 뉴스 분석 보고서 ===")

# 지역별 1위 후보 정리
region_lines = "\n".join(
    f"- {region}: {winner}"
    for region, winner in regional_winners.items()
)

# 개표 단계별 선두 변화 정리
change_steps = [
    int(step)
    for step in step_leaders.index[leader_changes]
]

change_text = (
    ", ".join(map(str, change_steps)) + "단계"
    if change_steps else "선두 변경 없음"
)

report = f"""2026 한빛시 시장선거 분석 보고서
================================

[자료 성격]
가상 선거 · 교육용 시뮬레이션
프로젝트: AIJ_P1
실제 선거 결과가 아님

[최종 개표 결과]
1위: {summary.index[0]} - {int(summary.iloc[0]['득표수']):,}표
2위: {summary.index[1]} - {int(summary.iloc[1]['득표수']):,}표
3위: {summary.index[2]} - {int(summary.iloc[2]['득표수']):,}표

전체 유효투표수: {total_valid_votes:,}표
1위와 2위 표 차이: {int(first['득표수'] - second['득표수']):,}표

[지역별 1위 후보]
{region_lines}

[개표 흐름]
개표 단계: {len(step_votes)}단계
초기 선두: {step_leaders.iloc[0]}
최종 선두: {step_leaders.iloc[-1]}
선두 변경: {change_text}

[핵심 보도 내용]
1. 최종 개표 결과와 후보별 득표율
2. 1위와 2위의 득표 격차
3. 5개 지역의 후보별 득표 차이
4. 개표 진행에 따른 선두 변경
5. 최종 결과 및 교육용 데이터 고지

[보도 유의사항]
- 모든 데이터는 가상으로 생성됨
- 실제 선거 및 실제 정치인과 무관
- 후보별 득표수와 기준시각 검증 필요
- AI 생성 기사는 사람의 최종 승인 필요
"""

# UTF-8 보고서 저장
report_file = OUTPUT_DIR / "election_analysis_report.txt"

with open(report_file, "w", encoding="utf-8") as f:
    f.write(report)

print(report)
print("\n보고서 저장 완료:", report_file)
