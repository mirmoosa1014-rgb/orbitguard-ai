"""Short numerical-orbit animation; not a screen recording."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation,PillowWriter
ROOT=Path(__file__).resolve().parents[1]
def main():
 d=json.loads((ROOT/'results/demo.json').read_text());p=np.array(d['primary_km']);o=np.array(d['objects_km'])[0];dist=np.array(d['distance_km'])[0];times=np.array(d['times_s'])/60
 plt.rcParams.update({'figure.facecolor':'#071E36','axes.facecolor':'#071E36','text.color':'#E5F6FF','axes.labelcolor':'#8FB4C9','xtick.color':'#8FB4C9','ytick.color':'#8FB4C9'})
 fig,(a,b)=plt.subplots(1,2,figsize=(9,4));fig.subplots_adjust(left=.09,right=.97,bottom=.16,top=.82,wspace=.32)
 # Relative 3D state projected into current ECI xy plane; numeric relative path.
 relative=o-p;a.plot(relative[:,0],relative[:,1],c='#E5F6FF',lw=1);point,=a.plot([],[],'o',c='#7FDBFF');a.set(xlabel='Relative x / km',ylabel='Relative y / km',title='Numerical encounter / ECI xy')
 b.plot(times,dist,c='#7FDBFF');cursor=b.axvline(0,c='#F2C14E');b.set(xlabel='Time / min',ylabel='Separation / km',title='Refined separation');label=fig.suptitle('ORBITGUARD / SYNTHETIC NUMERICAL REPLAY',fontsize=13)
 def update(i):
  point.set_data([relative[i,0]],[relative[i,1]]);cursor.set_xdata([times[i],times[i]]);label.set_text(f'ORBITGUARD / SYNTHETIC REPLAY / T + {times[i]:.1f} min');return point,cursor,label
 FuncAnimation(fig,update,frames=range(0,len(times),3),interval=100).save(ROOT/'docs/images/encounter.gif',writer=PillowWriter(fps=10),dpi=90);plt.close(fig)
if __name__=='__main__':main()
