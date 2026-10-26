"""Deterministic SI-unit two-body RK4 propagator; no J2 in this release."""
import numpy as np
MU=3.986004418e14
R_EARTH=6371000.
def acceleration(r):
    n=np.linalg.norm(r)
    if n<R_EARTH: raise ValueError('state intersects Earth')
    return -MU*r/n**3
def derivative(x): return np.r_[x[3:],acceleration(x[:3])]
def step(x,dt):
    a=derivative(x);b=derivative(x+dt*a/2);c=derivative(x+dt*b/2);d=derivative(x+dt*c)
    return x+dt*(a+2*b+2*c+d)/6
def propagate(x,times,impulse=None):
    times=np.asarray(times,float)
    if len(times)<2 or np.any(np.diff(times)<=0):raise ValueError('strictly increasing times required')
    x=np.asarray(x,float).copy()
    if x.shape!=(6,) or not np.isfinite(x).all():raise ValueError('finite 6-state required')
    if impulse is not None:
        index,dv=impulse
        if index<0 or index>=len(times)-1 or np.linalg.norm(dv)>2.00001:raise ValueError('invalid impulse; maximum 2 m/s')
    out=[x.copy()]
    for i,dt in enumerate(np.diff(times),1):
        if impulse is not None and i-1==impulse[0]: x[3:]+=impulse[1]
        n=max(1,int(np.ceil(dt/20)))
        for _ in range(n):x=step(x,dt/n)
        out.append(x.copy())
    return np.array(out)
def circular(radius=R_EARTH+550000.,phase=0.,inclination=0.):
    c,s=np.cos(phase),np.sin(phase); ci,si=np.cos(inclination),np.sin(inclination)
    speed=np.sqrt(MU/radius)
    return np.array([radius*c,radius*s*ci,radius*s*si,-speed*s,speed*c*ci,speed*c*si])
