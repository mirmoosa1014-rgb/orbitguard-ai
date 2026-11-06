"""Small calibrated-by-validation logistic ranker; JSON weights only."""
import numpy as np
FEATURES=['coarse_miss_km','relative_speed_km_s','time_to_coarse_ca_fraction','position_sigma_km']
def train(X,y):
    X=np.asarray(X,dtype=float);y=np.asarray(y,dtype=float)
    if X.ndim!=2 or X.shape[1]!=4 or len(X)==0 or y.shape!=(len(X),):raise ValueError('nonempty four-feature rows and matching labels required')
    if not np.isfinite(X).all() or not np.isfinite(y).all():raise ValueError('training data must be finite')
    if set(np.unique(y))!={0.,1.}:raise ValueError('training labels must include both binary classes')
    mean=X.mean(0);scale=X.std(0)+1e-9;Z=(X-mean)/scale;w=np.zeros(4);b=0.
    positive=max(float(y.mean()),.01);weights=np.where(y>0,.5/positive,.5/(1-positive))
    for _ in range(1600):
        p=1/(1+np.exp(-np.clip(Z@w+b,-30,30)));e=(p-y)*weights
        w-=.08*(Z.T@e/len(y)+.005*w);b-=.08*e.mean()
    return dict(features=FEATURES,mean=mean.tolist(),scale=scale.tolist(),weights=w.tolist(),bias=float(b))
def score(model,X):
    Z=(np.asarray(X)-model['mean'])/model['scale'];v=Z@model['weights']+model['bias']
    return 1/(1+np.exp(-np.clip(v,-30,30)))

def rank_candidates(features,path):
    """Trusted bundled JSON only. Missing/invalid model falls back to distance."""
    import json
    from pathlib import Path
    try:
        model=json.loads(Path(path).read_text())
        if model['features']!=FEATURES:raise ValueError('schema mismatch')
        for key in ('mean','scale','weights'):
            values=np.asarray(model[key],float)
            if values.shape!=(4,) or not np.isfinite(values).all():raise ValueError('invalid model vector')
        if np.any(np.asarray(model['scale'])<=0) or np.ndim(model['bias'])!=0 or not np.isfinite(model['bias']):raise ValueError('invalid scale or bias')
        scores=score(model,features)
        if not np.isfinite(scores).all():raise ValueError('nonfinite scores')
        return np.argsort(-scores),'learned'
    except (OSError,ValueError,KeyError,TypeError):
        return np.argsort(np.asarray(features)[:,0]),'distance-fallback'
