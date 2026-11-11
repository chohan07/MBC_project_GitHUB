"""2026 한빛시 시장 선거: 100% 교육용 합성 데이터 생성 (표준 라이브러리만 사용)."""
from pathlib import Path
import csv, json
from datetime import datetime, timedelta

ROOT = Path(__file__).resolve().parent
NOTICE = '가상 선거·교육용 시뮬레이션'
SOURCE = 'SYNTHETIC-STEP2-v1.0'
CANDIDATES = [
    dict(candidate_id='C01', name='이몽룡', age=52, party='한빛미래당', primary_policy='광역교통망 확충', policy_focus='교통·도시개발', color='#2563EB'),
    dict(candidate_id='C02', name='심청이', age=47, party='시민혁신당', primary_policy='청년 주거 지원', policy_focus='주거·복지', color='#DC2626'),
    dict(candidate_id='C03', name='홍길동', age=44, party='무소속', primary_policy='소상공인 지원', policy_focus='지역경제·일자리', color='#16A34A'),
]
REGIONS = [
    dict(region_id='R01', region='중앙구', electorate=110000, voters=77000, invalid_final=800, C01=27000, C02=30000, C03=19200),
    dict(region_id='R02', region='동부구', electorate=100000, voters=70000, invalid_final=700, C01=29000, C02=24000, C03=16300),
    dict(region_id='R03', region='서부구', electorate=95000, voters=66500, invalid_final=650, C01=22000, C02=26000, C03=17850),
    dict(region_id='R04', region='남부구', electorate=105000, voters=73500, invalid_final=700, C01=25000, C02=31000, C03=16800),
    dict(region_id='R05', region='북부구', electorate=90000, voters=63000, invalid_final=650, C01=25000, C02=20000, C03=17350),
]

def split_integer(total, weights):
    """Largest-remainder allocation: integer bins sum to total exactly."""
    vals = [total * w / sum(weights) for w in weights]
    base = [int(v) for v in vals]
    extras = total - sum(base)
    for i in sorted(range(len(vals)), key=lambda k: (-(vals[k]-base[k]), k))[:extras]:
        base[i] += 1
    return base

def save_csv(filename, rows, columns):
    with (ROOT / filename).open('w', encoding='utf-8-sig', newline='') as f:
        wr = csv.DictWriter(f, fieldnames=columns)
        wr.writeheader(); wr.writerows(rows)

def save_json(filename, value):
    (ROOT / filename).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def main():
    save_csv('candidates.csv', CANDIDATES, list(CANDIDATES[0]))
    regions_public = [{k:v for k,v in r.items() if k in ('region_id','region','electorate','voters')} | {'turnout_rate': round(r['voters']/r['electorate']*100, 2)} for r in REGIONS]
    save_csv('regions.csv', regions_public, ['region_id','region','electorate','voters','turnout_rate'])
    start = datetime(2026,11,20,19,0)
    # Early batches favor C01, later batches C02; not a projection or real-world trend.
    weights = {'C01':[1.65,1.5,1.35,1.2,1.1,0.95,0.8,0.65,0.5,0.3],
               'C02':[0.35,0.5,0.65,0.8,0.9,1.05,1.2,1.35,1.5,1.7],
               'C03':[1]*10, 'invalid':[1]*10}
    all_rows = []
    buckets = {}
    for r in REGIONS:
        buckets[r['region_id']] = {cid:split_integer(r[cid], weights[cid]) for cid in ('C01','C02','C03')}
        buckets[r['region_id']]['invalid'] = split_integer(r['invalid_final'], weights['invalid'])
    for step in range(1,11):
        timestamp = (start + timedelta(minutes=30*(step-1))).isoformat(timespec='minutes') + '+09:00'
        for r in REGIONS:
            bins=buckets[r['region_id']]
            invalid = sum(bins['invalid'][:step]); valid = sum(sum(bins[cid][:step]) for cid in ('C01','C02','C03'))
            counted=valid+invalid
            for candidate in CANDIDATES:
                cid=candidate['candidate_id']; votes=sum(bins[cid][:step])
                all_rows.append(dict(row_id=f'S{step:02d}-{r["region_id"]}-{cid}',step=step,
                    timestamp=timestamp,region_id=r['region_id'],region=r['region'],
                    candidate_id=cid,candidate_name=candidate['name'],votes=votes,
                    valid_votes=valid,invalid_votes=invalid,counted_ballots=counted,
                    total_ballots=r['voters'],vote_share_pct=round(100*votes/valid,4) if valid else 0,
                    count_progress_pct=round(100*counted/r['voters'],4),source_id=SOURCE,
                    is_synthetic=True))
    save_csv('election_results.csv',all_rows,list(all_rows[0]))
    steps=[]
    for step in range(1,11):
        rows=[r for r in all_rows if r['step']==step]
        keyed={cid:sum(r['votes'] for r in rows if r['candidate_id']==cid) for cid in ('C01','C02','C03')}
        counted=sum(r['counted_ballots'] for r in rows if r['candidate_id']=='C01')
        valid=sum(r['valid_votes'] for r in rows if r['candidate_id']=='C01')
        invalid=sum(r['invalid_votes'] for r in rows if r['candidate_id']=='C01')
        ranking=sorted(CANDIDATES,key=lambda c:(-keyed[c['candidate_id']],c['candidate_id']))
        steps.append(dict(step=step,timestamp=rows[0]['timestamp'],counted_ballots=counted,
            valid_votes=valid,invalid_votes=invalid,count_progress_pct=round(counted/350000*100,4),
            candidate_results=[dict(candidate_id=c['candidate_id'],name=c['name'],votes=keyed[c['candidate_id']],
                                    vote_share_pct=round(100*keyed[c['candidate_id']]/valid,4),rank=i+1)
                               for i,c in enumerate(ranking)],
            leader_id=ranking[0]['candidate_id'],leader_name=ranking[0]['name'],
            margin_votes=keyed[ranking[0]['candidate_id']]-keyed[ranking[1]['candidate_id']],
            margin_percentage_points=round(100*(keyed[ranking[0]['candidate_id']]-keyed[ranking[1]['candidate_id']])/valid,4)))
    summary=dict(disclaimer=NOTICE,is_synthetic=True,source_id=SOURCE,
        election='2026 한빛시 시장 선거',election_date='2026-11-20',timezone='Asia/Seoul',
        electorate=500000,total_ballots=350000,turnout_rate_pct=70.0,
        regions=5,candidates=3,stages=10,steps=steps)
    save_json('election_summary.json',summary)
    docs=[]
    def add(docid, title, typ, contents, candidate_id=None):
        docs.append(dict(document_id=docid,title=title,document_type=typ,publisher='한빛시 가상선거 교육자료 제작팀',
                        published_at='2026-11-11',source_id=SOURCE,source_url=None,
                        citation_label='내부 교육용 창작 자료 (외부 원문 URL 없음)',candidate_id=candidate_id,
                        disclaimer=NOTICE,text=contents))
    add('DOC-001','한빛시 가상 선거 기본 설정','election_background',
        '한빛시는 교육 실습을 위한 가상 도시다. 선거는 2026년 11월 20일로 설정되었으며 중앙구, 동부구, 서부구, 남부구, 북부구 5개 지역으로 구성된다. 선거인은 500,000명, 투표자는 350,000명이다.')
    add('DOC-002','이몽룡 후보 정책 소개','candidate_policy','이몽룡 후보는 가상 정당 한빛미래당 소속이며 광역교통망 확충을 주요 공약으로 제시한다. 정책 영역은 교통·도시개발이다.','C01')
    add('DOC-003','심청이 후보 정책 소개','candidate_policy','심청이 후보는 가상 정당 시민혁신당 소속이며 청년 주거 지원을 주요 공약으로 제시한다. 정책 영역은 주거·복지다.','C02')
    add('DOC-004','홍길동 후보 정책 소개','candidate_policy','홍길동 후보는 무소속이며 소상공인 지원을 주요 공약으로 제시한다. 정책 영역은 지역경제·일자리다.','C03')
    add('DOC-005','개표 데이터 해석 기준','methodology',
        '각 단계는 지역별 누적 개표값이며 단계가 진행될수록 누적 개표수는 감소하지 않는다. 득표율은 후보 득표수/해당 범위 유효투표수×100이다. 개표율은 개표된 투표지 수/최종 투표자 수×100이며 무효표는 득표율의 분모에서 제외한다. 초반 선두와 최종 결과는 다를 수 있다. 모든 수치는 가상이다.')
    add('DOC-006','중립 보도·검증 운영 원칙','editorial_policy',
        '정당·후보에 대한 지지·비방 표현을 피하고, 단계별 기준시각과 데이터 행 ID를 기사에 기재한다. 수치 불일치나 근거 누락이 있으면 사람 승인 전까지 기사 상태는 검토 필요다. 가상 선거·교육용 시뮬레이션 표시를 모든 화면에 유지한다.')
    save_json('policy_documents.json',docs)
    save_json('article_log.json',dict(disclaimer=NOTICE,articles=[],approval_events=[],note='STEP 7에서 기사 및 승인 이력을 추가합니다.'))
    return summary,all_rows

if __name__=='__main__':
    summary,rows=main()
    print(f'완료: {len(rows)}개 개표 행 / 10단계 / 5지역 / 3후보')
    print('최종:',[(x['name'],x['votes']) for x in summary['steps'][-1]['candidate_results']])
    print('단계별 선두:',[(s['step'],s['leader_name']) for s in summary['steps']])
