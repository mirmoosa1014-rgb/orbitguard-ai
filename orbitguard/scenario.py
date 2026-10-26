import numpy as np
from .physics import circular,propagate,step
def catalog(seed=2026,count=18,horizon=1800):
    rng=np.random.default_rng(seed);times=np.arange(0,horizon+1,20.)
    family=seed//100
    primary=circular(radius=6371000.+450000.+family*18000.,inclination=.15+family*.055);states=[]
    for i in range(count):
        x=primary.copy();x[:3]+=rng.normal(0,[13000,45000,14000]);x[3:]+=rng.normal(0,[5,18,6]);states.append(x)
    truth=propagate(primary,times)
    # Deliberate future encounter: integrate a relative offset at 1200s backward.
    # Policies receive only the resulting present state, never future labels.
    encounter=truth[60].copy();encounter[:3]+=np.array([900.,300.,200.]);encounter[3:]+=np.array([2.,7.,3.])
    for _ in range(60):encounter=step(encounter,-20.)
    states[0]=encounter
    debris=np.array([propagate(x,times) for x in states])
    coarse=np.array([x[:3]+times[:,None]*x[3:] for x in states]);pcoarse=primary[:3]+times[:,None]*primary[3:]
    separation=np.linalg.norm(debris[:,:,:3]-truth[None,:,:3],axis=2)
    cd=np.linalg.norm(coarse-pcoarse[None,:,:],axis=2)
    features=np.array([[d.min()/1000,np.linalg.norm(x[3:]-primary[3:])/1000,times[d.argmin()]/horizon,.3] for x,d in zip(states,cd)])
    return times,primary,np.array(states),truth,debris,separation,cd,features
def maneuvers(times,primary,debris):
    result=[];direction=primary[3:]/np.linalg.norm(primary[3:]);nominal=propagate(primary,times)
    nominal_min=np.linalg.norm(debris[:,:,:3]-nominal[None,:,:3],axis=2).min(1)
    for ti in [0,15,30]:
      for dv in [-2.,-1.,-.5,0.,.5,1.,2.]:
        p=propagate(primary,times,(ti,dv*direction));dist=np.linalg.norm(debris[:,:,:3]-p[None,:,:3],axis=2)
        result.append(dict(time_s=float(times[ti]),delta_v_m_s=abs(dv),signed_dv_m_s=dv,min_separation_m=float(dist.min()),new_close_approaches=int(np.sum((dist.min(1)<10000)&(nominal_min>=10000)))))
    for r in result:r['pareto']=not any(s['delta_v_m_s']<=r['delta_v_m_s'] and s['min_separation_m']>=r['min_separation_m'] and (s['delta_v_m_s']<r['delta_v_m_s'] or s['min_separation_m']>r['min_separation_m']) for s in result)
    return result
