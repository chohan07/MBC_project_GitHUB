import os
import json
from pathlib import Path
from gtts import gTTS

# 현재 스크립트 실행 위치 기준
BASE_DIR = Path(__file__).parent

# JSON 파일 위치 확인 (EP32_production.json 및 production.json 호환 지원)
JSON_FILE = BASE_DIR / "EP32_production.json"
if not JSON_FILE.exists():
    JSON_FILE = BASE_DIR / "production.json"

if not JSON_FILE.exists():
    print(f"❌ 오류: EP32_production.json (또는 production.json) 파일을 찾을 수 없습니다.")
    exit()

with open(JSON_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# 프로젝트 메타데이터 추출
project = data.get("project", {})
output = data.get("output", {})
scenes = data.get("scenes", [])
bgm = data.get("bgm", {})

episode = project.get("episode", 32)
title_kr = project.get("title_kr", "조선시대 사람들은 시간을 어떻게 알았을까?")
title_en = project.get("title_en", "How Did People in the Joseon Dynasty Tell Time?")

# 최상위 프로젝트 폴더 이름: 표준 규격 'EP00. ○○○' 적용
clean_title_kr = title_kr.replace('?', '').strip()
folder_name = f"EP{episode:02d}. {clean_title_kr}"
project_dir = BASE_DIR / folder_name
project_dir.mkdir(exist_ok=True)

# 필수 하위 작업 폴더 경로 정의 (01_SCRIPT ~ 07_FINAL 표준 7종)
folders = {
    "script": project_dir / "01_SCRIPT",
    "image": project_dir / "02_IMAGE",
    "video": project_dir / "03_VIDEO",
    "voice": project_dir / "04_VOICE",
    "bgm": project_dir / "05_BGM",
    "capcut": project_dir / "06_CAPCUT",
    "final": project_dir / "07_FINAL"
}

# 하위 폴더 일괄 자동 생성
for folder_path in folders.values():
    folder_path.mkdir(exist_ok=True)

print("=" * 65)
print(f"🚀 EP{episode:02d}. {clean_title_kr}")
print("   표준 폴더 구조, 개별/통합 TXT 파일 및 gTTS 음성(.mp3) 생성을 시작합니다.")
print("=" * 65)

# ==========================================
# 1. 01_SCRIPT 폴더 내 txt 파일 생성
# ==========================================
narration_kr_lines = []
narration_en_lines = []
subtitle_kr_lines = []
subtitle_en_lines = []

for s in scenes:
    sc_num = f"SC{s['scene']:02d}"
    if s.get("narration_kr"):
        narration_kr_lines.append(f"[{sc_num}] {s['narration_kr']}")
    if s.get("narration_en"):
        narration_en_lines.append(f"[{sc_num}] {s['narration_en']}")
    if s.get("subtitle_kr"):
        subtitle_kr_lines.append(f"[{sc_num}] {s['subtitle_kr']}")
    if s.get("subtitle_en"):
        subtitle_en_lines.append(f"[{sc_num}] {s['subtitle_en']}")

with open(folders["script"] / "narration_KR.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(narration_kr_lines))

with open(folders["script"] / "narration_EN.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(narration_en_lines))

with open(folders["script"] / "subtitle_KR.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(subtitle_kr_lines))

with open(folders["script"] / "subtitle_EN.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(subtitle_en_lines))

print("✓ 01_SCRIPT: narration_KR/EN.txt, subtitle_KR/EN.txt 생성 완료")

# ==========================================
# 2. 02_IMAGE 폴더 내 미드저니 프롬프트 txt 파일 생성
# ==========================================
image_prompt_lines = []
for s in scenes:
    sc_num = f"SC{s['scene']:02d}"
    img_prompt = s.get("image", {}).get("prompt", "")
    if img_prompt:
        image_prompt_lines.append(f"{sc_num}: {img_prompt}")
        with open(folders["image"] / f"{sc_num}_Midjourney.txt", "w", encoding="utf-8") as f:
            f.write(img_prompt)

# 통합 SC00_Midjourney.txt 생성
with open(folders["image"] / "SC00_Midjourney.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(image_prompt_lines))

print(f"✓ 02_IMAGE: SC01~SC{len(scenes):02d}_Midjourney.txt 및 통합 SC00_Midjourney.txt 생성 완료")

# ==========================================
# 3. 03_VIDEO 폴더 내 구글플로우 프롬프트 txt 파일 생성
# ==========================================
video_prompt_lines = []
for s in scenes:
    sc_num = f"SC{s['scene']:02d}"
    vid_info = s.get("video", {})
    vid_tool = vid_info.get("tool", "")
    vid_prompt = vid_info.get("prompt", "")
    
    if vid_prompt:
        tool_name = "GoogleFlow" if "Google Flow" in vid_tool else "Midjourney"
        video_prompt_lines.append(f"{sc_num}: {vid_prompt}")
        with open(folders["video"] / f"{sc_num}_{tool_name}.txt", "w", encoding="utf-8") as f:
            f.write(vid_prompt)

# 통합 SC00_GoogleFlow.txt 생성
with open(folders["video"] / "SC00_GoogleFlow.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(video_prompt_lines) if video_prompt_lines else "No Google Flow prompts specified.")

print("✓ 03_VIDEO: 개별 영상 프롬프트 txt 및 통합 SC00_GoogleFlow.txt 생성 완료")

# ==========================================
# 4. 04_VOICE 폴더 내 gTTS 음성 파일 자동 생성
# 명명 규칙: SC_kr_01.mp3, SC_en_01.mp3 (숫자가 마지막에 위치)
# ==========================================
print("🎙️ 04_VOICE: [4. 장면 구성] 대본을 기반으로 씬별 국·영문 음성 파일 자동 생성 중...")
for s in scenes:
    scene_idx = s['scene']
    
    # 한국어 나레이션 TTS 생성
    kr_text = s.get("narration_kr", "")
    if kr_text:
        tts_kr = gTTS(text=kr_text, lang='ko')
        kr_filename = f"SC_kr_{scene_idx:02d}.mp3"
        tts_kr.save(str(folders["voice"] / kr_filename))

    # 영어 나레이션 TTS 생성
    en_text = s.get("narration_en", "")
    if en_text:
        tts_en = gTTS(text=en_text, lang='en')
        en_filename = f"SC_en_{scene_idx:02d}.mp3"
        tts_en.save(str(folders["voice"] / en_filename))

print(f"✓ 04_VOICE: SC_kr_01.mp3 ~ SC_kr_{len(scenes):02d}.mp3, SC_en_01.mp3 ~ SC_en_{len(scenes):02d}.mp3 생성 완료")

# ==========================================
# 5. 05_BGM 폴더 내 추천 파일 생성
# ==========================================
with open(folders["bgm"] / "BGM_recommendation.txt", "w", encoding="utf-8") as f:
    f.write(f"Recommended BGM Mood: {bgm.get('mood', 'CURIOUS')}\n")
    f.write(f"Recommended Track: {bgm.get('recommended_track', 'CURIOUS')}\n")
    f.write(f"Volume Setting: {bgm.get('volume_percent', 25)}%\n")
    f.write("선택 이유: 시계가 없던 조선시대의 시간 측정 방식에 대한 호기심으로 시작해, 자격루의 발명과 도성의 대종 타종 구간에서 웅장하고 과학적인 역사적 카타르시스를 전달하기 위함입니다.\n")

print("✓ 05_BGM: BGM_recommendation.txt 생성 완료")

# ==========================================
# 6. 06_CAPCUT 폴더 내 편집표 txt 생성
# ==========================================
capcut_lines = []
for s in scenes:
    sc_num = f"SC{s['scene']:02d}"
    cap = s.get("capcut", {})
    capcut_lines.append(
        f"[{sc_num}] Duration: {s.get('duration_seconds')}s | "
        f"Effect: {cap.get('effect')} | "
        f"Transition: {cap.get('transition', 'None')} | "
        f"SFX: {cap.get('sfx', 'None')}"
    )

with open(folders["capcut"] / "CapCut_editing_plan.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(capcut_lines))

print("✓ 06_CAPCUT: CapCut_editing_plan.txt 생성 완료")

# ==========================================
# 7. 07_FINAL 폴더 내 유튜브 업로드용 txt 파일 생성
# ==========================================
youtube_ko = f"""1. EP 번호 : 한글 제목 : EP.{episode} : {title_kr}
2. 한국어 영상에 들어갈 추천 해시태그 : #Korea #KoreanCulture #KoreaTravel #Joseon #KoreanHistory #한국문화 #한국역사 #조선시대 #자격루 #앙부일구 #세종대왕 #장영실
3. 한국어 전체 대본 :
{data.get('narration', {}).get('korean')}"""

youtube_en = f"""1. EP 번호 : 영어 제목 : EP.{episode} : {title_en}
2. 영어 영상에 들어갈 추천 해시태그 : #Korea #KoreanCulture #KoreaTravel #JoseonDynasty #KoreanHistory #KingSejong #WaterClock #Sundial #AncientScience
3. 영어 전체 대본 :
{data.get('narration', {}).get('english')}"""

with open(folders["final"] / "YouTube_ko.txt", "w", encoding="utf-8") as f:
    f.write(youtube_ko)

with open(folders["final"] / "YouTube_en.txt", "w", encoding="utf-8") as f:
    f.write(youtube_en)

print("✓ 07_FINAL: YouTube_ko.txt, YouTube_en.txt 생성 완료")

print("=" * 65)
print(f"🎉 모든 폴더, 개별/통합 txt 파일, TTS 음성 파일 생성이 성공적으로 완료되었습니다!")
print(f"📁 생성 위치: {project_dir}")
print("=" * 65)