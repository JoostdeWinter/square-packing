"""Write square poses from source CSVs or NPYs for the C++ rectangular-crop search."""
import argparse,json,struct
from pathlib import Path
import numpy as np
import pandas as pd
p=argparse.ArgumentParser(description=__doc__);p.add_argument('files',nargs='+',type=Path);args=p.parse_args()
names=[]
with open('geom.bin','wb') as dest:
 for f in args.files:
  if f.suffix=='.npy':
   parts=[(f.stem,np.load(f))]
  else:
   source=pd.read_csv(f,usecols=['n','x','y','angle'])
   parts=((f'{f.stem}:{n}',g[['x','y','angle']].to_numpy()) for n,g in source.groupby('n'))
  for key,coords in parts:
   names.append(key);dest.write(struct.pack('i',len(coords)));dest.write(np.asarray(coords,dtype='d',order='C').tobytes())
Path('source_order.json').write_text(json.dumps(names))
