"""STEP 2 교육용 선거 데이터 일관성 점검."""
import csv,json
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parent
with (ROOT/'election_results.csv').open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
summary=json.loads((ROOT/'election_summary.json').read_text(encoding='utf-8'))
assert len(rows)==150 and len(summary['steps'])==10
prev={}
for stage in range(1,11):
    subset=[r for r in rows if int(r['step'])==stage]
    assert len(subset)==15
    for rid in ['R01','R02','R03','R04','R05']:
        rs=[r for r in subset if r['region_id']==rid]
        assert len(rs)==3
        assert len({r['timestamp'] for r in rs})==1
        assert len({r['counted_ballots'] for r in rs})==1
        valid=int(rs[0]['valid_votes']);invalid=int(rs[0]['invalid_votes']);counted=int(rs[0]['counted_ballots']); ballots=int(rs[0]['total_ballots'])
        assert sum(int(r['votes']) for r in rs)==valid
        assert valid+invalid==counted<=ballots
        assert all(abs(float(r['vote_share_pct'])-100*int(r['votes'])/valid)<0.000051 for r in rs)
        assert abs(float(rs[0]['count_progress_pct'])-100*counted/ballots)<0.000051
        for r in rs:
            key=(rid,r['candidate_id'])
            assert int(r['votes'])>=prev.get(key,0)
            prev[key]=int(r['votes'])
        assert counted>=prev.get((rid,'ballots'),0)
        prev[(rid,'ballots')]=counted
        if stage==10: assert counted==ballots
    s=summary['steps'][stage-1]
    assert s['counted_ballots']==sum(int(r['counted_ballots']) for r in subset if r['candidate_id']=='C01')
    assert s['valid_votes']==sum(int(r['valid_votes']) for r in subset if r['candidate_id']=='C01')
    assert s['invalid_votes']==sum(int(r['invalid_votes']) for r in subset if r['candidate_id']=='C01')
    assert s['valid_votes']+s['invalid_votes']==s['counted_ballots']
assert summary['steps'][-1]['counted_ballots']==350000
assert summary['steps'][-1]['valid_votes']==346500
assert summary['steps'][-1]['invalid_votes']==3500
assert summary['steps'][0]['leader_id']=='C01'
assert summary['steps'][-1]['leader_id']=='C02'
print('PASS: 150행, 10단계, 5개 구, 3명 후보')
print('PASS: 단계별 누적값 단조 증가 / 득표율 / 개표율 / 유효·무효·전체 투표수 일치')
print('PASS: 개표 초기 C01 선두, 마지막 C02 선두')
print('PASS: 최종 전체 350000, 유효 346500, 무효 3500')
