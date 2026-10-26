from pathlib import Path
import argparse,json,csv,time
import numpy as np
from .scenario import catalog,maneuvers
from .model import train,score
from .estimation import estimate,estimate_cv,predict
from .physics import propagate
ROOT=Path(__file__).resolve().parents[1]
def run(full=False):
    start=time.perf_counter();n=30 if full else 10;trainseeds=list(range(100,100+n));valseeds=list(range(400,405));testseeds=list(range(700,700+(15 if full else 5)))
    def dataset(seeds):
        X=[];y=[]
        for seed in seeds:
            *_,sep,cd,f=catalog(seed,count=18);X.extend(f);y.extend(sep.min(1)<10000)
        return np.array(X),np.array(y,float)
    X,y=dataset(trainseeds);model=train(X,y);VX,VY=dataset(valseeds)
    raw=score(model,VX);a,b=1.,0.;logit=np.log(np.clip(raw,1e-6,1-1e-6)/(1-np.clip(raw,1e-6,1-1e-6)))
    for _ in range(1000):
        p=1/(1+np.exp(-np.clip(a*logit+b,-30,30)));a-=.03*np.mean((p-VY)*logit);b-=.03*np.mean(p-VY)
    model['calibration']={'slope':float(a),'intercept':float(b)}
    cv_trials=[]
    for q in [.003,.3,3.,10.,30.]:
        loss=[]
        for seed in valseeds:
            tv,pv,sv,truthv,*_=catalog(seed);rng=np.random.default_rng(seed+9000);zv=truthv[:31,:3]+rng.normal(0,80,(31,3));iv=truthv[0].copy();iv[:3]+=rng.normal(0,300,3);iv[3:]+=rng.normal(0,3,3)
            ev,_,_=estimate_cv(iv,zv,acceleration_sigma=q);loss.append(np.mean((ev[:,:3]-truthv[:31,:3])**2))
        cv_trials.append((float(np.mean(loss)),q))
    cv_q=min(cv_trials)[1];rows=[];errors=[];cover=[];residuals=[];predictions=[]
    for seed in testseeds:
        ts,primary,states,truth,debris,sep,cd,f=catalog(seed);s=score(model,f);actual=sep.min(1)<10000;budget=5
        for policy,order in [('distance',np.argsort(f[:,0])),('learned',np.argsort(-s))]:
            selected=order[:budget];hits=int(actual[selected].sum());rows.append(dict(seed=seed,policy=policy,budget=budget,positives=int(actual.sum()),hits=hits,missed=int(actual.sum())-hits,recall=hits/max(1,int(actual.sum()))))
        rng=np.random.default_rng(seed+9000);measurements=truth[:31,:3]+rng.normal(0,80,(31,3));initial=truth[0].copy();initial[:3]+=rng.normal(0,300,3);initial[3:]+=rng.normal(0,3,3)
        est,P,res=estimate(initial,measurements);cv,cvP,cvres=estimate_cv(initial,measurements,acceleration_sigma=cv_q);e=np.linalg.norm(est[:,:3]-truth[:31,:3],axis=1);ecv=np.linalg.norm(cv[:,:3]-truth[:31,:3],axis=1)
        for i in range(31):
            mahal=float((est[i,:3]-truth[i,:3])@np.linalg.solve(P[i,:3,:3],est[i,:3]-truth[i,:3]));cover.append(mahal<=7.8147)
        predicted=propagate(est[-1],ts[30:]);cvforecast=cv[-1,:3]+(ts[30:]-ts[30])[:,None]*cv[-1,3:];cvca=abs(np.linalg.norm(debris[:,30:,:3]-cvforecast[None,:,:],axis=2).min()-sep[:,30:].min());ca_error=abs(np.linalg.norm(debris[:,30:,:3]-predicted[None,:,:3],axis=2).min()-sep[:,30:].min())
        errors.append(dict(seed=seed,ekf_rmse_m=float(np.sqrt(np.mean(e**2))),cv_rmse_m=float(np.sqrt(np.mean(ecv**2))),closest_approach_error_m=float(ca_error),cv_closest_approach_error_m=float(cvca)));residuals.extend(res.tolist())
        calibrated=1/(1+np.exp(-np.clip(a*np.log(np.clip(s,1e-6,1-1e-6)/(1-np.clip(s,1e-6,1-1e-6)))+b,-30,30)))
        predictions.extend([dict(probability=float(p),actual=int(y)) for p,y in zip(calibrated,actual)])
    ts,primary,states,truth,debris,sep,cd,f=catalog();ms=maneuvers(ts,primary,debris);scores=score(model,f)
    rng=np.random.default_rng(2026);initial=primary.copy();initial[:3]+=rng.normal(0,300,3);initial[3:]+=rng.normal(0,3,3)
    e0,c0,_=estimate(initial,(primary[:3]+rng.normal(0,80,3))[None,:]);xx,pp=e0[0],c0[0];unc=[float(np.sqrt(np.linalg.eigvalsh(pp[:3,:3]).max())*1.96/1000)]
    for dt in np.diff(ts):
        xx,pp=predict(xx,pp,float(dt));unc.append(float(np.sqrt(np.linalg.eigvalsh(pp[:3,:3]).max())*1.96/1000))
    demo=dict(seed=2026,times_s=ts.tolist(),earth_radius_km=6371,primary_km=(truth[:,:3]/1000).tolist(),objects_km=(debris[:,:,:3]/1000).tolist(),distance_km=(sep/1000).tolist(),coarse_distance_km=(cd/1000).tolist(),scores=scores.tolist(),maneuvers=ms,residuals_m=residuals[:31],uncertainty_km=unc)
    metrics=dict(cv_acceleration_sigma_m_s2=cv_q,cv_validation_trials=cv_trials,mode='full' if full else 'quick',train_seeds=trainseeds,validation_seeds=valseeds,test_seeds=testseeds,training_positive_fraction=float(y.mean()),ekf_rmse_m=float(np.mean([e['ekf_rmse_m'] for e in errors])),cv_rmse_m=float(np.mean([e['cv_rmse_m'] for e in errors])),cv_ca_error_m=float(np.mean([e['cv_closest_approach_error_m'] for e in errors])),position_95pct_coverage=float(np.mean(cover)),ca_error_m=float(np.mean([e['closest_approach_error_m'] for e in errors])),distance_recall=float(np.mean([r['recall'] for r in rows if r['policy']=='distance'])),learned_recall=float(np.mean([r['recall'] for r in rows if r['policy']=='learned'])),brier_score=float(np.mean([(p['probability']-p['actual'])**2 for p in predictions])),elapsed_s=time.perf_counter()-start)
    for d in ['results','models','frontend/public']: (ROOT/d).mkdir(parents=True,exist_ok=True)
    for name,data in [('demo',demo),('metrics',metrics),('ranking',rows),('estimation',errors),('calibration',predictions)]: (ROOT/'results'/f'{name}.json').write_text(json.dumps(data,indent=2))
    (ROOT/'models/ranker.json').write_text(json.dumps(model,indent=2));(ROOT/'frontend/public/demo.json').write_text(json.dumps(demo));(ROOT/'frontend/public/metrics.json').write_text(json.dumps(metrics))
    for name,data in [('ranking',rows),('estimation',errors),('maneuvers',ms)]:
        with (ROOT/'results'/f'{name}.csv').open('w') as fh:w=csv.DictWriter(fh,fieldnames=data[0]);w.writeheader();w.writerows(data)
    print(json.dumps(metrics,indent=2));return demo,metrics
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--full',action='store_true');run(p.parse_args().full)
