from fastapi.testclient import TestClient
from orbitguard.api import app
client=TestClient(app)
def test_api():
    assert client.get('/api/health').status_code==200
    d=client.get('/api/demo').json();assert len(d['primary_km'])==len(d['times_s'])
    assert client.get('/api/scenario?seed=-1').status_code==422
