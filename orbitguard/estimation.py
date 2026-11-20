"""Position-observation EKF, constant-velocity baseline, finite-difference Jacobian."""
import numpy as np
from .physics import step
def predict(x,P,dt):
    F=np.empty((6,6))
    for j in range(6):
        h=1. if j<3 else .001; d=np.zeros(6);d[j]=h
        F[:,j]=(step(x+d,dt)-step(x-d,dt))/(2*h)
    q=.003
    G=np.vstack([np.eye(3)*dt*dt/2,np.eye(3)*dt])
    return step(x,dt), F@P@F.T+q*q*G@G.T
def update(x,P,z,sigma=80.):
    x=np.asarray(x,float);P=np.asarray(P,float);z=np.asarray(z,float)
    if x.shape!=(6,) or P.shape!=(6,6) or z.shape!=(3,) or not all(np.isfinite(v).all() for v in (x,P,z)):raise ValueError('finite state, 6x6 covariance and 3-position measurement required')
    if isinstance(sigma,(bool,np.bool_)) or not isinstance(sigma,(int,float,np.integer,np.floating)) or not np.isfinite(sigma) or sigma<=0:raise ValueError('measurement sigma must be a finite positive number')
    H=np.c_[np.eye(3),np.zeros((3,3))];R=np.eye(3)*sigma**2
    innovation=z-H@x;S=H@P@H.T+R;K=np.linalg.solve(S,H@P).T
    A=np.eye(6)-K@H
    return x+K@innovation,A@P@A.T+K@R@K.T,innovation
def estimation_inputs(initial,measurements,dt):
    if isinstance(dt,(bool,np.bool_)) or not isinstance(dt,(int,float,np.integer,np.floating)) or not np.isfinite(dt) or dt<=0:raise ValueError('measurement interval must be finite and positive')
    initial=np.asarray(initial,float);measurements=np.asarray(measurements,float)
    if initial.shape!=(6,) or measurements.ndim!=2 or measurements.shape[1]!=3 or len(measurements)==0 or not np.isfinite(initial).all() or not np.isfinite(measurements).all():raise ValueError('finite 6-state and nonempty position measurements required')
    return initial.copy(),measurements

def estimate(initial,measurements,dt=20.):
    x,measurements=estimation_inputs(initial,measurements,dt);P=np.diag([300**2]*3+[3**2]*3);states=[];cov=[];res=[]
    for i,z in enumerate(measurements):
        if i:x,P=predict(x,P,dt)
        x,P,r=update(x,P,z);states.append(x.copy());cov.append(P.copy());res.append(r)
    return np.array(states),np.array(cov),np.array(res)
def estimate_cv(initial,measurements,dt=20.,acceleration_sigma=10.):
    if isinstance(acceleration_sigma,(bool,np.bool_)) or not isinstance(acceleration_sigma,(int,float,np.integer,np.floating)) or not np.isfinite(acceleration_sigma) or acceleration_sigma<0:raise ValueError('acceleration sigma must be a finite nonnegative number')
    x,measurements=estimation_inputs(initial,measurements,dt);P=np.diag([300**2]*3+[3**2]*3);states=[];cov=[];res=[]
    F=np.eye(6);F[:3,3:]=np.eye(3)*dt
    G=np.vstack([np.eye(3)*dt*dt/2,np.eye(3)*dt]);Q=acceleration_sigma**2*G@G.T
    for i,z in enumerate(measurements):
        if i:x=F@x;P=F@P@F.T+Q
        x,P,r=update(x,P,z);states.append(x.copy());cov.append(P.copy());res.append(r)
    return np.array(states),np.array(cov),np.array(res)
