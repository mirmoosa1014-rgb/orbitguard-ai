"""Small calibrated-by-validation logistic ranker; JSON weights only."""
import numpy as np
FEATURES=['coarse_miss_km','relative_speed_km_s','time_to_coarse_ca_fraction','position_sigma_km']
def train(X,y):
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
        scores=score(model,features)
        if not np.isfinite(scores).all():raise ValueError('nonfinite scores')
        return np.argsort(-scores),'learned'
    except (OSError,ValueError,KeyError,TypeError):
        return np.argsort(np.asarray(features)[:,0]),'distance-fallback'
