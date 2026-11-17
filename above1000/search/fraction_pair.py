'''Universal pairwise glue; inputs need only counts and square bounds.'''
import sys,math,ast
import pandas as pd,numpy as np
from numba import njit
from spacers import apply
@njit(cache=True)
def pairs(kk,ee,ff,nn,up):
 lim=100; out=np.ones((100,201));ids=np.zeros((100,201,3),np.int32)
 for u in range(len(kk)):
  for v in range(u,len(kk)):
   K=kk[u]+kk[v]; r=ee[u]+ee[v]
   if K>=100:break
   for c in range(5):
    if r<=c:continue
    dd=(0.,.49999999,.687319, .79289320,1.)[c]
    f=max(ff[u],ff[v],ff[u]+ff[v]-dd)
    if c==1 and (up[u] or up[v]):f=max(ff[u],ff[v]);
    if f<out[K,r-c]-1e-11:out[K,r-c]=f;ids[K,r-c]=np.array((nn[u],nn[v],c))
 return out,ids
if __name__=='__main__':
 z=pd.read_csv('generic.csv',index_col='n');B=z.implied.to_dict(); recipes={}; up=set()
 for n,t in z.construction.dropna().items():
  row=ast.literal_eval(t)
  if (row[0]=='L' and row[3]>0) or (isinstance(row[0],int) and len(row)>=2):up.add(int(n))
 for it in range(6):
  # Pareto prune when extending the smaller dimension and deleting excess squares dominates.
  rows=[]; tab=np.ones((100,201));tabup=tab.copy()
  for n,s in B.items():
   a=math.floor(s+1e-12);e=n-a*a
   if a<100 and e>0 and 1e-10<s-a<.99999999:tab[a,e]=s-a
   if n in up and a<100 and e>0 and 1e-10<s-a<.99999999:tabup[a,e]=s-a
  for flag,t in [(True,tabup),(False,tab)]:
   for a in range(1,100):
    for e in range(199,0,-1):
     if t[a,e]<1 and t[a,e]<min(t[a-1,e],t[a,e+1])-1e-10: rows.append((a,e,t[a,e],a*a+e,flag));
     t[a,e]=min(t[a,e],t[a-1,e],t[a,e+1]);
  rows.sort();a,e,f,n,flag=map(np.array,zip(*rows));fv,pr=pairs(a,e,f,n,flag);new=0
  for k,r in zip(*np.where(fv<1)):
   v=k*k+r;s=k+fv[k,r]
   if v in B and s<B[v]-1e-10: B[v]=s; recipes[v]=list(map(int,pr[k,r]));up.add(v);new+=1
  for v,(s,w) in apply(B).items():B[v]=s;recipes[v]=['spacer']+w;up.add(v); new+=1
  for _ in range(2):
   for v in range(1,10001):
    s=B[v];k=math.floor(s+1e-12)
    for a in range(1,math.isqrt(10000//v)+1):
     m=v*a*a;b=s*a;h=math.floor(b+1e-12)
     for j in range(101):
      w=m+2*j*h+j*j
      if w>10000:break
      if b+j<B[w]-1e-10:B[w]=b+j;recipes[w]=['L',v,a,j];new+=1
      else:continue
      if j or v in up:up.add(w)
   for v in range(9999,0,-1):
    if B[v+1]<B[v]-1e-10:B[v]=B[v+1];recipes[v]=['D',v+1];new+=1
    else:continue
    if v+1 in up:up.add(v)
  print('iter',it,len(rows),new,flush=True)
  pd.DataFrame({'n':list(B),'implied':list(B.values()),'construction':[str(recipes[n]) if n in recipes else z.loc[n,'construction'] for n in B]}).to_csv('generic_full.csv',index=False)
  if not new:break
