import numpy as np
import pytest
from orbitguard.physics import MU,circular,propagate,step
from orbitguard.estimation import update,estimate,estimate_cv
from orbitguard.scenario import catalog,maneuvers
from orbitguard.model import train,score

def test_circular_period_and_conservation():
    x=circular();period=2*np.pi*np.sqrt(np.linalg.norm(x[:3])**3/MU);t=np.linspace(0,period,400);y=propagate(x,t)
    energy=(y[:,3:]**2).sum(1)/2-MU/np.linalg.norm(y[:,:3],axis=1);h=np.cross(y[:,:3],y[:,3:])
    assert np.linalg.norm(y[-1,:3]-x[:3])<1
    assert np.ptp(energy)/abs(energy[0])<1e-7
    assert np.max(np.linalg.norm(h-h[0],axis=1))/np.linalg.norm(h[0])<1e-7

def test_convergence():
    x=circular();a=step(x,20);b=step(step(x,10),10);ref=x.copy()
    for _ in range(20):ref=step(ref,1)
    assert np.linalg.norm(b-ref)<np.linalg.norm(a-ref)/10

def test_update_covariance():
    x=np.zeros(6);P=np.eye(6)*100;z=np.ones(3);a,C,r=update(x,P,z,sigma=10)
    assert np.allclose(a[:3],.5);assert np.allclose(C,C.T);assert np.linalg.eigvalsh(C).min()>0

def test_causal_prefix():
    t,p,s,tr,*_=catalog(701);obs=tr[:8,:3]
    for method in [estimate,estimate_cv]:
        a,C,_=method(p,obs);b,_,_=method(p,obs[:5]);assert np.allclose(a[:5],b);assert np.linalg.eigvalsh(C).min()>0

def test_bad_times_and_impulses():
    x=circular()
    for times in [[0,0],[0,-1]]:
        with pytest.raises(ValueError):propagate(x,times)
    with pytest.raises(ValueError):propagate(x,[0,20],(0,np.array([3.,0,0])))
    with pytest.raises(ValueError):propagate(x,[0,20],(1,np.zeros(3)))

def test_deterministic_catalog_and_split():
    a=catalog(100);b=catalog(100);assert np.array_equal(a[3],b[3]);assert not np.array_equal(a[1],catalog(700)[1])

def test_model_and_budgets():
    X=np.array([[0,0,0,0],[1,2,0,0],[2,4,0,0],[3,6,0,0]],float);m=train(X,np.array([0,0,1,1]));p=score(m,X);assert np.isfinite(p).all();assert p[-1]>p[0]

def test_maneuver_bounds_and_catalog():
    t,p,s,tr,d,*_=catalog(2026,count=3);original=d.copy();out=maneuvers(t,p,d)
    assert len(out)==21;assert max(x['delta_v_m_s'] for x in out)<=2;assert np.array_equal(d,original);assert any(x['pareto'] for x in out)
    assert max(x['min_separation_m'] for x in out)-min(x['min_separation_m'] for x in out)>100

def test_missing_model_fallback(tmp_path):
    from orbitguard.model import rank_candidates
    X=np.array([[3,1,0,.3],[1,1,0,.3],[2,1,0,.3]])
    order,policy=rank_candidates(X,tmp_path/'missing.json')
    assert policy=='distance-fallback';assert order.tolist()==[1,2,0]
