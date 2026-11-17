import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import numpy as np
from scipy.sparse import coo_matrix
from scipy.optimize import linprog
from scipy.spatial import cKDTree
from scipy.optimize import OptimizeWarning
import warnings
warnings.simplefilter('ignore',OptimizeWarning)
def normalize(a):
 a=a.copy(); a[:,2]=(a[:,2]+np.pi/4)%(np.pi/2)-np.pi/4
 h=(np.cos(a[:,2])+abs(np.sin(a[:,2])))/2
 a[:,:2]-=(a[:,:2]-h[:,None]).min(0)
 return a
BOXOFF=np.zeros(2)
def side(a):
 h=(np.cos(a[:,2])+abs(np.sin(a[:,2])))/2;return ((a[:,:2]+h[:,None]).max(0)-(a[:,:2]-h[:,None]).min(0)-BOXOFF).max()
def geometry(a,p):
 i,j=p.T; dt=(a[j,2]-a[i,2]+np.pi/4)%(np.pi/2)-np.pi/4; phi=a[i,2]+dt/2
 dxy=a[j,:2]-a[i,:2]; xx=np.cos(phi); yy=np.sin(phi)
 xx0=dxy[:,0]*xx+dxy[:,1]*yy; yy0=-dxy[:,0]*yy+dxy[:,1]*xx
 # phi chose nearest axis to center vector
 w=abs(yy0)>abs(xx0); sign=np.where(np.where(w,yy0,xx0)>=0,1,-1);xx,yy=np.where(w,-yy,xx)*sign,np.where(w,xx,yy)*sign
 u=dxy[:,0]*xx+dxy[:,1]*yy; v=-dxy[:,0]*yy+dxy[:,1]*xx;c=np.cos(dt/2);s=np.sin(dt/2)
 gap=u*c+abs(v*s)-.5*(1+np.cos(dt)+abs(np.sin(dt)))
 return xx,yy,u,v,c,s,dt,gap
def quality(a):
 p=cKDTree(a[:,:2]).query_pairs(1.45,output_type='ndarray')
 gap=geometry(a,p)[-1]; return side(a),-gap.min(),sum(np.maximum(0,-gap))
def linear(a,r,lam=3,lockup=True,rng=None,rbranch=0.,mut=None):
 n=len(a);p=cKDTree(a[:,:2]).query_pairs(1.43+2*r,output_type='ndarray');g=geometry(a,p)[-1];p=p[g>-.99];p=p[g[g>-.99]<.025+4*r]
 xx,yy,u,v,c,s,dt,gap=geometry(a,p);i,j=p.T; npair=len(p)
 b=[]; cols=[]; rows=[]; vals=[]
 def add(ids,vs,bs):
  m=len(bs); rows.extend(np.repeat(np.arange(len(b),len(b)+m),len(ids)))
  cols.extend(np.array(ids).T.flatten());vals.extend(np.array(vs).T.flatten());b.extend(bs)
 for sign in [-1,1]:
  gap=u*c+abs(v)*s*sign-.5*(1+np.cos(dt)+sign*np.sin(dt))
  gdt=-.5*u*s+sign*.5*abs(v)*c+.5*np.sin(dt)-.5*sign*np.cos(dt)
  gphi=c*v-sign*s*np.sign(v)*u
  dx=xx*c - yy*sign*s*np.sign(v); dy=yy*c + xx*sign*s*np.sign(v)
  gi=.5*gphi-gdt; gj=.5*gphi+gdt
  use=(np.abs(dt)<.08+2*r)|(dt*sign>=0)
  k=np.where(use)[0]
  add([3*i[k],3*i[k]+1,3*i[k]+2,3*j[k],3*j[k]+1,3*j[k]+2,3*n+1+k],[dx[k],dy[k],-gi[k],-dx[k],-dy[k],-gj[k],-np.ones(len(k))],gap[k])
 S=side(a)
 for sign in [-1,1]:
  h=(np.cos(a[:,2])+sign*np.sin(a[:,2]))/2; hdot=(-np.sin(a[:,2])+sign*np.cos(a[:,2]))/2
  for dim in range(2):
   t=a[:,dim]
   idx=np.where(t-h<.35+2*r)[0];num=len(idx)
   add([3*idx+dim,3*idx+2],[-np.ones(num),hdot[idx]],t[idx]-h[idx])
   idx=np.where(S+BOXOFF[dim]-t-h<.35+2*r)[0];num=len(idx)
   add([3*idx+dim,3*idx+2,np.full(num,3*n)],[np.ones(num),hdot[idx],-np.ones(num)],-t[idx]-h[idx]+BOXOFF[dim])
 A=coo_matrix((vals,(rows,cols)),shape=(len(b),3*n+1+npair)).tocsc()
 d=np.full((n,3),r); d[:,2]=r*.55
 if lockup:d[np.abs(a[:,2])<.00003,2]=0
 cobj=np.r_[np.zeros(3*n),1.,np.full(npair,lam)]
 if mut is not None:cobj[:3*n]=mut.flatten()
 res=linprog(cobj,A_ub=A,b_ub=b,bounds=np.c_[np.r_[-d.flatten(),0,np.zeros(npair)],np.r_[d.flatten(),50.,np.full(npair,3)]],method='highs-ds',options={'threads':1,'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
 if not res.success: return None
 return res.x[:3*n].reshape(-1,3),res.fun
def refine(a,its=130,r=.02,lam=3,lockup=True,verb=False,mut=None):
 a=normalize(a);q=quality(a);val=q[0]+lam*q[2];best=1e9;ba=None;sig=0
 for it in range(its):
  if r<3e-9: break
  d=linear(a,r,lam,lockup,mut=mut if it<3 else None)
  if d is None:r*=.4; continue
  d,pred=d
  if verb and it%12==0: print('iter',it,val,q[1],pred,r,flush=True)
  for frac in [1,.6,.3,.12]:
   b=normalize(a+d*frac);Q=quality(b);v=Q[0]+lam*Q[2]
   if v<val-1.e-12 or (mut is not None and it<3 and Q[1]<.0005 and v<val+.001):
    a=b;val=v;q=Q;r=min(.065,r*(1.45 if frac>=.6 else .65));break
  else:r*=.45
  if q[1]<.0002:
   h=(np.cos(a[:,2])+abs(np.sin(a[:,2])))/2
   z=a.copy();z[:,:2]*=1+max(0,q[1])*1.05+2e-13;sz=side(z)
   if sz<best:
    best=sz;ba=normalize(z)
 return best,ba if ba is not None else a

if __name__=='__main__':
    from pathlib import Path
    import json,gzip
    with gzip.open(Path(__file__).with_name('starting_rectangles.json.gz'),'rt') as stream:
        seeds=json.load(stream)
    for key,block in seeds.items():
        initial=np.array(block['poses'],dtype=float)
        initial[:,:2]/=1e20
        initial[:,2]=2*np.arctan2(initial[:,2],1e12)
        BOXOFF=np.array([block['a'],block['b']])
        score,poses=refine(initial,its=100,r=.025)
        print(key,score)
