from pathlib import Path
import json
from fastapi import FastAPI,Query
from fastapi.middleware.cors import CORSMiddleware
from .scenario import catalog,maneuvers
app=FastAPI(title='OrbitGuard AI',version='1.0.0')
app.add_middleware(CORSMiddleware,allow_origins=['http://127.0.0.1:5102','http://localhost:5102'],allow_methods=['GET'])
ROOT=Path(__file__).resolve().parents[1]
@app.get('/api/health')
def health():return {'status':'ok','mode':'synthetic educational simulation'}
@app.get('/api/demo')
def demo():return json.loads((ROOT/'results/demo.json').read_text())
@app.get('/api/metrics')
def metrics():return json.loads((ROOT/'results/metrics.json').read_text())
@app.get('/api/scenario')
def scenario(seed:int=Query(2026,ge=0,le=100000)):
    t,p,s,tr,d,sep,cd,f=catalog(seed,count=12)
    return {'seed':seed,'times_s':t.tolist(),'primary_km':(tr[:,:3]/1000).tolist(),'objects_km':(d[:,:,:3]/1000).tolist(),'distance_km':(sep/1000).tolist(),'maneuvers':maneuvers(t,p,d)}
