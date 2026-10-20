"""gTTS로 전체 및 장면별 한국어/영어 MP3 저장 (인터넷 필요)."""
import json
from pathlib import Path
from gtts import gTTS
from create_project import PROJECT_DIR, DATA, initialize


def main():
    initialize()
    out = PROJECT_DIR/'04_VOICE'
    tasks=[]
    for lang,key in [('ko','korean'),('en','english')]:
        tasks.append((DATA['narration'][key],lang,out/f'full_{lang}.mp3'))
        for sc in DATA['scenes']:
            tasks.append((sc['narration_kr' if lang=='ko' else 'narration_en'],lang,out/f'SC{sc["scene"]:02d}_{lang}.mp3'))
    for i,(message,lang,path) in enumerate(tasks,1):
        if path.exists() and path.stat().st_size > 0:
            print(f'[{i}/{len(tasks)}] 기존 음성 유지: {path.name}')
            continue
        try:
            gTTS(text=message,lang=lang,slow=False).save(str(path))
            print(f'[{i}/{len(tasks)}] 생성: {path.name}')
        except Exception as exc:
            print(f'[{i}/{len(tasks)}] 실패 {path.name}: {exc}')
    print('완료. 음성을 들어보고 길이·발음·장면 싱크를 검수하세요.')

if __name__=='__main__':
    main()
