"""Search setup and geometry utilities for the two-band computation."""
import csv
import math
from fractions import Fraction as F
from pathlib import Path
HERE = Path(__file__).resolve().parent

def terms(b,t):
    c=(1-t*t)/(1+t*t)
    s=2*t/(1+t*t)
    return c,s,b*c+s

def dimensions(b,t,shape):
    c,s,w=terms(b,t)
    R,near,far=shape
    if w<max([0]+list(near)+list(far)):
        return w,math.inf
    def lift(end):
        return max([0]+[i+1-b*s+m*s/c for i,m in enumerate(end)])
    return w,(R-1)/c+b*s+c+lift(near)+lift(far)

def to_string(shape):
    return ':'.join([str(shape[0]),','.join(map(str,shape[1])),','.join(map(str,shape[2]))])
