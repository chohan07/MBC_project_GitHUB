# EP32 조선시대 시간 측정 방식 — 실습 프로젝트

## 포함 파일
- `production.json`: 첨부 제작표에서 추출한 8개 장면/대본/프롬프트
- `references.csv`: 웹 자료 출처 목록(검증 상태 포함)
- `create_project.py`: 폴더·대본·프롬프트·SQLite DB 자동 생성
- `generate_tts.py`: Google Translate 기반 gTTS로 한영 전체/장면별 음성 MP3 생성
- `app.py`: FastAPI를 통한 자료 조회 API
- `requirements.txt`: 설치할 Python 라이브러리
- `joseon.db`: 실행 후 생성되는 SQLite 파일

## Windows 11 + VS Code + Python 3.14.7
1. ZIP 압축을 풀고 VS Code에서 해당 폴더를 엽니다.
2. 터미널에서 `py -3.14 -m pip install -r requirements.txt` 실행. (환경에 따라 `python -m pip ...`)
3. `py -3.14 create_project.py` 실행 → 폴더와 DB 생성 확인.
4. `py -3.14 generate_tts.py` 실행 → 인터넷 연결 시 04_VOICE에 MP3 18개 생성(전체 한·영 2 + 씬별 한·영 16).
5. `py -3.14 -m uvicorn app:app --reload` 실행 → http://127.0.0.1:8000/docs 접속.

## 처리 범위
- 자동: 프로젝트 폴더/대본/프롬프트/DB/TTS(네트워크 연결 시)
- 수동: Midjourney 이미지 렌더링, Flow 영상 생성, CapCut 편집, 사실 확인, 최종 MP4 출력
- Google TTS는 여기서 `gTTS` 라이브러리이며 **Google Cloud Text-to-Speech 공식 API와 별개**입니다. gTTS는 외부 서비스 변경 시 작동이 중단될 수 있습니다.
- MP3 합성은 이 실행 환경에서 네트워크 제약으로 수행하지 않았으므로, 실제 실행은 PC에서 확인하십시오.
- 음성 길이가 장면별 설정시간과 일치하는지는 별도 확인이 필요합니다. 타임스탬프는 목표 장면 시간입니다.
- 웹/영상 이미지 재배포 시 저작권 및 사용허가 확인이 필요합니다. 단순 URL은 Open API 연동이 아닙니다.

## 과제 제출 설명
본 MVP는 CSV 출처 데이터를 SQLite에 저장하며 FastAPI로 조회할 수 있습니다. PDF 파싱과 공식 Open API 자동호출은 **확장 설계 항목**으로 남겨두었으며, 연결·수집했다고 주장하면 안 됩니다. 제작 자료는 `production.json`을 원본 데이터로 관리합니다.
