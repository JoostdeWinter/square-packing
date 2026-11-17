"""Tighten the angles of any two-band certificate while preserving the integer pattern.
Run python polish.py INPUT.csv OUTPUT.csv. Inputs and outputs use the refined-table schema.
"""
from fractions import Fraction
import csv,sys,math
from pathlib import Path
from scipy.optimize import minimize_scalar
def pattern(text):
 r,a,b=text.split(':')
 return int(r),[int(x) for x in a.split(',') if x],[int(x) for x in b.split(',') if x]
def terms(b,t,shape):
 c=(1-t*t)/(1+t*t);s=2*t/(1+t*t);w=b*c+s
 rows,near,far=shape
 if max([0]+near+far)>w:return w,math.inf
 def support(layer):
  return max([0]+[i+1-b*s+m*s/c for i,m in enumerate(layer)])
 return w,(rows-1)/c+b*s+c+support(near)+support(far)
def search(r):
 Q=Fraction
 old=Q(r['side_exact'])
 k,bv,bh=map(int,(r['K'],r['bV'],r['bH']))
 gv,gh=k-bv,k-bh
 vh=pattern(r['H']);vv=pattern(r['V'])
 u=Q(r['tH']); v=Q(r['tV'])
 def hash_t(x):return Q(round(x*10**13),10**13)
 # Follow the feasible interval from the incumbent in both directions.
 hs=[u]
 for end in (max(.00001,float(u)-.12),min(.65,float(u)+.12)):
  low=float(u); high=end
  for _ in range(44):
   mid=(low+high)/2
   if terms(bh,mid,vh)[1]<=gv:low=mid
   else:high=mid
  for x in [low,low+(float(u)-low)*1e-10,low+(float(u)-low)*1e-8]:
   q=hash_t(x)
   if terms(bh,q,vh)[1]<=gv:hs.append(q)
 u=min(hs,key=lambda x:terms(bh,x,vh)[0]);w2=terms(bh,u,vh)[0]
 def obj(t):
  w,h=terms(bv,t,vv);return max(gv+w,gh+float(w2),h)
 left=max(.00001,float(v)-.06);right=min(.7,float(v)+.09)
 res=minimize_scalar(obj,bounds=(left,right),method='bounded',options=dict(xatol=1e-14))
 vs=[v,hash_t(res.x)]
 side=old;ans=dict(r)
 for t in vs:
  w,h=terms(bv,t,vv)
  trial=max(gv+w,h,gh+w2)
  if trial<side:
   side=trial
   rounded=math.ceil(side*10**12);ans.update(tV=str(t),tH=str(u),side_exact=str(side),side_up=f'{rounded//10**12}.{rounded%10**12:012d}')
 return ans
if __name__=='__main__':
 with open(sys.argv[1],newline='') as f,open(sys.argv[2],'w',newline='') as dest:
  rows=csv.DictReader(f);w=csv.DictWriter(dest,fieldnames=rows.fieldnames);w.writeheader()
  for r in rows:w.writerow(search(r))
