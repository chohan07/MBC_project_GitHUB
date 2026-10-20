"""FastAPI 최소 기능: 프로젝트/장면/자료 조회."""
import sqlite3
from pathlib import Path
from fastapi import FastAPI, HTTPException
from create_project import ROOT, initialize

app=FastAPI(title='Joseon Time Shorts API',version='1.0')

def fetch(sql,params=()):
    with sqlite3.connect(ROOT/'joseon.db') as con:
        con.row_factory=sqlite3.Row
        return [dict(r) for r in con.execute(sql,params).fetchall()]

@app.on_event('startup')
def startup():
    initialize()

@app.get('/')
def home():
    return {'message':'EP32 제작 관리 API','docs':'/docs'}

@app.get('/projects')
def projects():
    return fetch('SELECT * FROM projects')

@app.get('/scenes')
def scenes():
    return fetch('SELECT * FROM scenes ORDER BY scene_no')

@app.get('/scenes/{scene_no}')
def scene(scene_no:int):
    rows=fetch('SELECT * FROM scenes WHERE scene_no=?',(scene_no,))
    if not rows: raise HTTPException(404,'장면을 찾을 수 없습니다.')
    return rows[0]

@app.get('/sources')
def sources():
    return fetch('SELECT * FROM sources ORDER BY source_id')
