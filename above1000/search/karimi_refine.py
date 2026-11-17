"""Optimize angles and end lifts while preserving the integer layout of a Karimi V2.0 row.
The input is the author's 5134-row filled_records.csv (Zenodo 23819397).
The independent exact certificate is the two regular bands and the axis grid."""
from fractions import Fraction as F
import csv, math, sys, os
from scipy.optimize import minimize_scalar
def terms(b,t):
 c=(1-t*t)/(1+t*t);s=2*t/(1+t*t)
 return c,s,b*c+s
def at_original(b,t,L,y):
 c,s,w=terms(b,t); R=math.floor((L-b*s-c)*c)+1
 free=L-b*s-c-(R-1)/c;levels=[]
 for lift in (y,free-y):
  mseq=[]
  for i in range(1000):
   m=math.floor(w-max(0,s+(i+1-lift)*c/s))
   if m<=0:break
   mseq.append(m)
  levels.append(tuple(mseq))
 return R,*levels

def dimensions(b,t,shape):
 c,s,w=terms(b,t); R,near,far=shape
 if w<max([0]+list(near)+list(far)):return w,math.inf
 def lift(end):
  return max([0]+[i+1-b*s+m*s/c for i,m in enumerate(end)])
 return w,(R-1)/c+b*s+c+lift(near)+lift(far)
def to_string(shape):
 return ':'.join([str(shape[0]),','.join(map(str,shape[1])),','.join(map(str,shape[2]))])
def optimize(row):
 n,K,bv,bh=map(int,[row['n'],row['K'],row['bV'],row['bH']])
 tv,th=F(row['tV']),F(row['tH'])
 orig=F(row['side_exact'])
 V=at_original(bv,tv,orig,F(row['yV']));H=at_original(bh,th,F(K-bv),F(row['yH']))
 # Each endpoint fill fixes a minimum lift as a maximum of smooth functions.
 # Search upwards from the original rational tangent to reduce horizontal width.
 a=float(th);hi=a+.10
 def feasible(t):return dimensions(bh,t,H)[1]<=K-bv
 if feasible(hi):
  while hi<.6 and feasible(hi):hi+=.03
 lo=a
 for _ in range(42):
  md=(lo+hi)/2
  if feasible(md):lo=md
  else:hi=md
 candidates=[th]
 for denom in (10**10,10**14):
  for step in (0,2,30):
   h=F(math.floor(lo*denom)-step,denom)
   if dimensions(bh,h,H)[1]<=K-bv:candidates.append(h)
 th2=min(candidates,key=lambda h:terms(bh,h)[2]); WH=terms(bh,th2)[2]
 def obj(t):
  w,l=dimensions(bv,t,V)
  return max(K-bv+w,l,K-bh+float(WH))
 t=max(.0001,float(tv));res=minimize_scalar(obj,bounds=(max(.0001,t-.03), t+.06),method='bounded',options={'xatol':1e-14})
 choices=[tv,F(round(res.x*10**13),10**13)]
 best=orig;bt=tv
 for v in choices:
  w,l=dimensions(bv,v,V)
  S=max(K-bv+w,l,K-bh+WH)
  if S<best:best=S;bt=v
 if best>=orig: return None
 N=(K-bv)*(K-bh)+bv*V[0]+sum(V[1])+sum(V[2])+bh*H[0]+sum(H[1])+sum(H[2])
 assert N>=n
 return dict(n=n,K=K,side_exact=str(best),side_up=math.ceil(best*10**12)/10**12,karimi_side=str(orig),bV=bv,tV=str(bt),V=to_string(V),bH=bh,tH=str(th2),H=to_string(H),capacity=N)
def main():
 import argparse
 import hashlib
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('original',help='Original filled_records.csv from Zenodo 23819397')
 parser.add_argument('output',help='New output CSV path')
 args=parser.parse_args()
 with open(args.original,'rb') as stream:
  digest=hashlib.sha256(stream.read()).hexdigest()
 if digest!='1cbfecf886a2000bd9d5f54304813d7422f785a2fb9a15655f2119a33f8c48f5':
  raise ValueError('Unexpected source digest')
 with open(args.original,newline='') as stream:
  rows=list(csv.DictReader(stream))
 with open(args.output,'w',newline='') as stream:
  writer=None
  count=0
  for row in rows:
   refined=optimize(row)
   if refined is None:continue
   if writer is None:
    writer=csv.DictWriter(stream,refined)
    writer.writeheader()
   writer.writerow(refined)
   count+=1
 print(f'{count} strict improvements from {len(rows)} source rows.')
if __name__=='__main__':main()
