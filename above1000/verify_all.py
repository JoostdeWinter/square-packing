"""Verify the complete index and replay all compact geometry certificates with Python 3.9+."""
import csv
import sys
import subprocess
from fractions import Fraction as Q
from pathlib import Path
from math import floor
P=Path(__file__).resolve().parent
def read(f):
 with (P/f).open(newline='') as fp:return list(csv.DictReader(fp))
def checkfile(file,*args):
 subprocess.run([sys.executable,str(P/file)]+list(args),cwd=P,check=True)
if not __debug__:raise RuntimeError('Run with assertions enabled')
direct={int(r['n']):r for r in read('constructions.csv')}
baseline={int(r['n']):Q(r['implied']) for r in read('comparisons/generic.csv')}
direct_sources={}
for folder in ('rectangles','rectopt','multi','chains','bands'):
 for row in read(folder+'/bounds.csv'):
  n=int(row['n']);assert n not in direct_sources
  direct_sources[n]=Q(row.get('upper') or row['side_exact'])
  assert direct[n]['witness_folder']==folder and direct_sources[n]==Q(direct[n]['upper_exact'])
assert direct.keys()==direct_sources.keys()
der={}
for row in read('derived.csv'):
 n=int(row['n']);parent=int(row['source_n']);t=int(row['copies_per_axis']);j=int(row['border_layers'])
 s=direct_sources[parent]*t
 drop=int(row['squares_removed'])
 assert n not in der and t>=1 and j>=0 and drop>=0
 assert n==t*t*parent+2*j*int(s)+j*j-drop
 assert Q(row['upper_exact'])==s+j
 der[n]=s+j
idx=read('records.csv')
assert len(idx)==len({r['n'] for r in idx})==len(direct_sources.keys()|der.keys())
for row in idx:
 n=int(row['n']);s=Q(row['upper_exact']);f=Q(row['comparison_floor'])
 assert s==(der[n] if n in der else direct_sources[n])
 assert s<=Q(row['upper_up_12'])<s+Q(1,10**12)
 assert f<=baseline[n] and s+Q(1,100000)<f
 assert 0<Q(row['gain_at_least'])<=f-s
print(f'PASS: {len(idx)} distinct counts and strict reference comparisons; {len(der)} exact border/deletion recipes.',flush=True)
checkfile('bands/verify_refined.py','bands/bounds.csv')
checkfile('bands/check_patterns.py','bands/bounds.csv')
checkfile('rectangles/verify.py')
checkfile('rectangles/check_expanded.py')
checkfile('rectopt/verify.py')
checkfile('rectopt/check_expanded.py')
checkfile('multi/verify_multi.py')
checkfile('chains/verify_chains.py')
checkfile('bands/check_coordinates.py',*[str(p) for p in sorted((P/'examples').glob('*.cert'))])
