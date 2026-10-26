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
    H=np.c_[np.eye(3),np.zeros((3,3))];R=np.eye(3)*sigma**2
    innovation=z-H@x;S=H@P@H.T+R;K=np.linalg.solve(S,H@P).T
    A=np.eye(6)-K@H
    return x+K@innovation,A@P@A.T+K@R@K.T,innovation
def estimate(initial,measurements,dt=20.):
    x=initial.copy();P=np.diag([300**2]*3+[3**2]*3);states=[];cov=[];res=[]
    for i,z in enumerate(measurements):
        if i:x,P=predict(x,P,dt)
        x,P,r=update(x,P,z);states.append(x.copy());cov.append(P.copy());res.append(r)
    return np.array(states),np.array(cov),np.array(res)
def estimate_cv(initial,measurements,dt=20.,acceleration_sigma=10.):
    x=initial.copy();P=np.diag([300**2]*3+[3**2]*3);states=[];cov=[];res=[]
    F=np.eye(6);F[:3,3:]=np.eye(3)*dt
    G=np.vstack([np.eye(3)*dt*dt/2,np.eye(3)*dt]);Q=acceleration_sigma**2*G@G.T
    for i,z in enumerate(measurements):
        if i:x=F@x;P=F@P@F.T+Q
        x,P,r=update(x,P,z);states.append(x.copy());cov.append(P.copy());res.append(r)
    return np.array(states),np.array(cov),np.array(res)
