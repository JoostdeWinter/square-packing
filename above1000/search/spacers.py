'''Compute scalar-implied packing bounds by gluing arbitrary square packings.
An initial block of integer base side a contains a*a+e squares. A gluing
with a unit upright strip added in either x or y preserves the sum of excesses;
a gluing on a corner with an upright available costs one square instead.
'''
from pathlib import Path
import csv,math
import numpy as np
import pandas as pd
from numba import njit

@njit(cache=True)
def closure_side(nlist,fs,Ks,es):
 MAX=99;cap=2*MAX+1; EMAX=2*MAX+2; inf=100000
 # DP over total cost and number of q=1 items (capped at 2). q=1 items
 # can be first component or contribute one spacer, q=0 can remove an
 # existing upright corner. The first two components carry q=1.
 V=np.full((cap+1,3),-9999,dtype=np.int32);V[0,0]=0
 witness=np.zeros((cap+1,3,64),np.int32); length=np.zeros((cap+1,3),np.int32)
 levels=np.ones((MAX+1,EMAX)); hist=np.zeros((MAX+1,EMAX,64),np.int32);hilen=np.zeros((MAX+1,EMAX),np.int32)
 max_e=np.zeros(MAX+1,np.int32)
 for u in range(len(fs)):
  n=nlist[u];a=Ks[u];e=es[u];f=fs[u]
  if e<=0 or f>.99999999:continue
  for q in (1,0):
   c=2*a+q;g=e-1+q
   if g<=0:continue
   for j in range(c,cap+1):
    for z in (0,1,2):
     zz=min(2,z+q)
     if V[j-c,z]+g<=V[j,zz] or V[j-c,z]<0:continue
     W=length[j-c,z]
     if W>=64:continue
     V[j,zz]=V[j-c,z]+g;length[j,zz]=W+1;witness[j,zz,:W]=witness[j-c,z,:W];witness[j,zz,W]=n if q else -n
  best=-100;jb=zb=-1
  for j in range(1,cap+1):
   for z in (0,1,2):
    if length[j,z]<=0:continue
    if z==2: val=V[j,z]
    elif z==1 and length[j,z]==1:val=V[j,z]
    elif z==0 and length[j,z]>=2:
     # No spacer at the first seam. Replacing the first two -1 choices
     # by removal of at most C squares (C=4 generally, C=2 for small f).
     # A q=0 layout needs spatial budget j rather than j-1.
     if j%2!=0:continue
     C=1 if f<.49999999 else (2 if f<.68731 else 4);val=V[j,z]+2-C
    else: continue
    if val>best:best,jb,zb=val,j,z
   if j%2==0:continue
   K=j//2
   if K<1 or best<=max_e[K]:continue
   end=min(best,EMAX-1);W=length[jb,zb]
   for r in range(max_e[K]+1,end+1):
    levels[K,r]=f;hist[K,r,:W]=witness[jb,zb,:W];hilen[K,r]=W
   max_e[K]=end
 return levels,hist,hilen

def apply(B):
 rows=[]
 for n,s in sorted(B.items()):
  a=math.floor(s+1e-12);e=n-a*a
  if e>0 and a<=97 and s>a+1e-10:rows.append((s-a,n,a,e))
 rows.sort();F,N,A,E=map(np.array,zip(*rows)); levels,history,sizes=closure_side(N,F,A,E)
 out={}
 for K,r in zip(*np.where(levels<1)):
  n=K*K+r
  if n not in B or r<=0:continue
  if K+levels[K,r]<B[n]-1e-9:
   out[n]=(K+levels[K,r],list(map(int,history[K,r,:sizes[K,r]])))
 return out
if __name__=='__main__':
 x=pd.read_csv('../comparisons/closure.csv',index_col='n').closure.to_dict();files={}
 for it in range(5):
  res=apply(x);print('iter',it,len(res),flush=True)
  if not res:break
  for n,(b,w) in res.items(): files[n]=(b,w);x[n]=b
  # Include deletion, packing replication, and regular L-border closures.
  for _ in range(3):
   for n in range(1,10001):
    s=x[n];k=math.floor(s+1e-12);maxA=math.isqrt(10000//n)
    for a in range(1,maxA+1):
     m=n*a*a;b=s*a;h=math.floor(b+1e-12)
     for j in range(101):
      v=m+2*j*h+j*j
      if v>10000:break
      if b+j<x[v]-1e-10:x[v]=b+j;files[v]=(b+j,['L',n,a,j])
   for n in range(9999,0,-1):
    if x[n+1]<x[n]-1e-10:x[n]=x[n+1];files[n]=(x[n+1],['D',n+1])
  pd.DataFrame({'n':list(x),'implied':list(x.values()),'construction':[str(files.get(n,('',''))[1]) for n in x]}).to_csv('generic.csv',index=False)
