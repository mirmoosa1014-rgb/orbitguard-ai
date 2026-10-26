import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def main():
    d=json.loads((ROOT/'results/demo.json').read_text());m=json.loads((ROOT/'results/metrics.json').read_text());cal=json.loads((ROOT/'results/calibration.json').read_text());est=json.loads((ROOT/'results/estimation.json').read_text())
    plt.rcParams.update({'figure.facecolor':'#07111c','axes.facecolor':'#0d1c2b','text.color':'#dce8ee','axes.labelcolor':'#9bb3c2','xtick.color':'#849eae','ytick.color':'#849eae','axes.edgecolor':'#294155','font.family':'DejaVu Sans','font.size':9,'savefig.facecolor':'#07111c'})
    fig=plt.figure(figsize=(15,9));fig.subplots_adjust(left=.06,right=.98,bottom=.09,top=.88,wspace=.38,hspace=.42);gs=fig.add_gridspec(2,3);ax=fig.add_subplot(gs[:,0],projection='3d');u=np.linspace(0,2*np.pi,48);v=np.linspace(0,np.pi,24);ax.plot_surface(6371*np.outer(np.cos(u),np.sin(v)),6371*np.outer(np.sin(u),np.sin(v)),6371*np.outer(np.ones_like(u),np.cos(v)),color='#19455f',alpha=.12,linewidth=0)
    for i,p in enumerate([d['primary_km']]+d['objects_km']):
        p=np.array(p);ax.plot(*p.T,color='#6df4d1' if i==0 else '#b79bff',alpha=1 if i==0 else .55,lw=3 if i==0 else 1)
    p=np.array(d['primary_km']);ax.text(*p[30], ' Protected',color='#6df4d1',fontsize=9)
    ax.set(title='Synthetic orbital theater',xlabel='x / km',ylabel='y / km',zlabel='z / km');ax.set_box_aspect((1,1,1));ax.view_init(25,45)
    for axis in [ax.xaxis,ax.yaxis,ax.zaxis]:axis.set_pane_color((.04,.09,.14,1))
    ax=fig.add_subplot(gs[0,1]);dist=np.array(d['distance_km']);idx=0;t=np.array(d['times_s'])/60;ax.plot(t,dist[idx],c='#6df4d1',label='RK4 numerical');ax.plot(t,d['coarse_distance_km'][idx],c='#b79bff',ls='--',label='Straight-line coarse');ax.set(title=f'Future encounter • OG-{idx+2:02}',xlabel='Time / min',ylabel='Separation / km');ax.legend(fontsize=8)
    ax=fig.add_subplot(gs[0,2]);man=d['maneuvers'];ax.scatter([x['delta_v_m_s'] for x in man],[x['min_separation_m']/1000 for x in man],c=['#ffc375' if x['pareto'] else '#6df4d1' for x in man],s=[55 if x['pareto'] else 20 for x in man]);ax.set(title='Bounded maneuver trade space',xlabel='Impulse magnitude / m/s',ylabel='Minimum catalog separation / km')
    ax=fig.add_subplot(gs[1,1]);ax.boxplot([[x['ekf_rmse_m'] for x in est],[x['cv_rmse_m'] for x in est]],tick_labels=['Two-body EKF','Tuned CV Kalman'],patch_artist=True,boxprops={'facecolor':'#24546a'},medianprops={'color':'#6df4d1'});ax.set(title='Same-observation comparison',ylabel='Position RMSE / m')
    ax=fig.add_subplot(gs[1,2]);ps=np.array([x['probability'] for x in cal]);ys=np.array([x['actual'] for x in cal]);xx=[];yy=[];sizes=[]
    for lo in np.arange(0,1,.2):
        mask=(ps>=lo)&(ps<lo+.2)
        if mask.any():xx.append(ps[mask].mean());yy.append(ys[mask].mean());sizes.append(mask.sum())
    ax.plot([0,1],[0,1],c='#587284',ls='--');ax.scatter(xx,yy,s=np.array(sizes)*2,c='#ffc375');ax.set(title=f'Calibration • Brier {m["brier_score"]:.3f}',xlabel='Validation-calibrated probability',ylabel='Observed positive fraction',xlim=(0,1),ylim=(0,1))
    fig.suptitle('ORBITGUARD AI  /  Synthetic conjunction laboratory',fontsize=18,x=.04,y=.97,ha='left');fig.savefig(ROOT/'docs/images/hero.png',dpi=150);plt.close(fig)
if __name__=='__main__':main()
