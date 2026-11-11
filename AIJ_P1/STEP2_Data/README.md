# AIJ P1 — STEP 2 가상 선거 데이터

> **가상 선거·교육용 시뮬레이션**. 실제 선거 및 실제 유권자와 무관한 인위적 데이터입니다. 실제 데이터 출처나 OpenAPI를 사용하지 않았습니다.

## 범위
- 2026 한빛시 시장 선거(가상), 2026-11-20(가상 선거일)
- 중앙구·동부구·서부구·남부구·북부구, 후보 이몽룡·심청이·홍길동
- 선거인 500,000명 / 투표 350,000명 / 투표율 70.0%
- 2026-11-20 19:00~23:30 KST 30분 간격의 10개 개표 스냅샷
- 최종 유효 346,500표 / 무효 3,500표

## 파일
| 파일 | 용도 |
|---|---|
| `candidates.csv` | 후보 3명의 ID·기본사항·공약 |
| `regions.csv` | 5개 가상 지역의 선거인·투표자 |
| `election_results.csv` | 단계 × 지역 × 후보 = 150행 누적 개표 데이터 |
| `election_summary.json` | 10단계 전체 개표 집계 및 순위 요약 |
| `policy_documents.json` | STEP 6 RAG 검색용 내부 창작 문서 6건, 고유 문서 ID |
| `article_log.json` | STEP 7의 기사·편집 승인 로그를 담을 빈 초기 구조 |
| `data_dictionary.csv` | 필드 정의 및 계산식 |
| `generate_election_data.py` | 모든 CSV/JSON 재생성 코드(표준 라이브러리만 사용) |
| `validate_data.py` | 누적값, 합계, 비율 일치 검증 코드 |
| `validation_result.txt` | 검증 실행 결과 |

## 실행 방법 — Windows 11 / VS Code
1. 압축 파일을 해제하고 VS Code에서 이 폴더를 엽니다.
2. 메뉴 **터미널 → 새 터미널**을 엽니다.
3. `python generate_election_data.py`를 실행합니다. (`python`이 인식되지 않으면 `py -3 generate_election_data.py`)
4. `python validate_data.py`로 정확성을 확인합니다.

별도 패키지 설치는 필요하지 않습니다.

## 계산 및 읽는 법
- `votes`: 후보별, 지역별 해당 단계의 **누적 유효 득표수**
- `valid_votes`: 같은 지역·단계에서 세 후보의 누적 득표수 합
- `invalid_votes`: 같은 지역·단계에서 확인된 누적 무효표
- `counted_ballots = valid_votes + invalid_votes`
- `vote_share_pct = votes / valid_votes × 100` (퍼센트)
- `count_progress_pct = counted_ballots / total_ballots × 100` (퍼센트)
- `total_ballots`: 그 지역의 최종 투표자 수(시뮬레이션에서 이미 확정된 분모)
- `row_id`: `S단계-R지역-C후보` 형태의 기사 근거 추적용 고유 행 ID
- `source_id`: `SYNTHETIC-STEP2-v1.0` — 외부 공식 출처가 아닌 내부 합성 데이터의 출처 식별자
- `timestamp`: 각 단계의 **가상 기준시각**. 실제 생성·수집시각이 아님.

주의: `valid_votes`, `invalid_votes`, `counted_ballots`는 지역·단계별 값이 후보 행마다 반복됩니다. 전체 합계를 낼 때는 후보 하나(C01 등)의 행만 선택하거나 지역·단계별로 중복 제거해야 합니다.

## 설계 선택 및 한계
- 각 후보의 최종 지역 득표수를 먼저 정하고, 임의의 시간 가중치로 **10개 구간에 분배하여 누적값**을 만듭니다. 선거 여론조사·예측 모델을 뜻하지 않습니다.
- 개표율은 **개표된 투표지 수(유효+무효)** 기준입니다. 유효표 득표율과 분모가 다릅니다.
- 초반 이몽룡 후보가 앞서고 최종 단계에 심청이 후보가 3,000표 차이로 역전하는 창작 시나리오입니다.
- `policy_documents.json`의 내용은 사실 검증된 실제 공약이 아니라 가상의 정책 설명이며 `source_url`은 `null`입니다.
- STEP 3 분석, STEP 4~5 웹·갱신, STEP 6 RAG, STEP 7 승인, STEP 8 영상 제작에서 동일한 ID·시각을 사용합니다.
- 모든 대시보드·기사·영상에 **가상 선거·교육용 시뮬레이션** 표기를 유지하세요.
