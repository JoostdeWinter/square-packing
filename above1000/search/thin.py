import numpy as np
from pathlib import Path
from collections import defaultdict
root=Path(__file__).parent
files=['blocks.txt'] if not (root/'interior.txt').exists() else ['blocks.txt','interior.txt']
raw=np.concatenate([np.loadtxt(root/f) for f in files])
raw=sorted(raw,key=lambda t:(t[4],-t[0],t[1]+t[2]))
kept=[];seen=np.ones((2,34,34,50))
for row in raw:
 z,a,b,e=map(int,row[:4]);f=row[4]
 if seen[z,a,b,e]<=f+1e-9:continue
 kept.append(row)
 for u,v in ((a,b),(b,a)):
  seen[:z+1,u:,v:,:e+1]=np.minimum(seen[:z+1,u:,v:,:e+1],f)
np.savetxt(root/'thin.txt',kept,fmt='%i %i %i %i %.14f %i %i %i %i');print(len(kept))
