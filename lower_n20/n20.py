#!/usr/bin/env python3
"""Rebuild a certificate that twenty unit squares cannot fit in side 99/20.

Research direction: Joost de Winter. AI author of this n=20 work: GPT6.2 Astra.
Geometry kernel: Mira Cult's n=18 project. Marks: Wolfram Bentz, Fig. 3.
Run with Python 3.10+ from a directory in which to save the proof archive.
The first run builds the case tree. Later runs can pass --cases and reuse it.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction as F
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path
from urllib.request import Request, urlopen
from zipfile import ZIP_DEFLATED, ZipFile

PIN = "78bec6aacebf304d942a9225e16c2f18165778ff"
URL = f"https://raw.githubusercontent.com/Mira-Cult/math/{PIN}/notes/geometry/unit-square-packing-18/replay/"
BLOBS = {
    "adaptive_angles.py": "44f0dfe4248bc86855eb9aeb7b1b1e3ddeeeb4f6",
    "angle_split_variant.py": "e3a503d27f167bbfacf2c52c1bea6c6748ddf62a",
    "arc_pair_variant.py": "ebb64ae8009e1b694b8879280427abdbe662d22f",
    "check_stabs.py": "917281b7e47f0feac7dc3037314d25e486972819",
    "check_wall.py": "6773a2f7e716d6e7c7520d149719b0168e4616d1",
    "edgeclip.py": "9c32df6578c37b81dc889e153a622d980f029746",
    "export_lattice.py": "57a28a0d5e490f582d0f22236c605cba471ce169",
    "export_native.py": "2f1e99878c72881b9d081a372b05b0dc0fcfc686",
    "lattice_kernel.cpp": "ca71fde2d725b3b12d6036d5d7d2526f51b44571",
    "nearest_init.py": "7d4b9f1bcc72fce729063409676bd3c9fe6b9283",
    "nearest_rack.py": "b8150bb2a008f1944ded967d65f472806cc32329",
    "pair_variant.py": "20a40fb3a46595441d4a837ce0516b39d8813a40",
    "rack_lattice_input.py": "9fcb3358425fb02bb475fd097c38fbd4b028ab07",
    "ragged_half_angles.inc": "013bd20ebab238f24d412ac457db69ddb27ac8e8",
    "short_facets.py": "6d14e14dbf85a8cb61da4a3538dc13146f408f44",
    "split_variant.py": "d878eb7c229fe3ff76d42ba2a14bba260083a2e3",
    "verify_arc_lower.py": "348e679e7e0187457c85c17a4867ca9895d7dab6",
    "verify_exit_lower.py": "dafd9efbceb81a3943c9d3029b2e582b959431db",
    "verify_nearest_lower.py": "1b43a0ca8ecc615ddc5680b8e0592ffb158ff51b",
    "verify_rack_angle.py": "fb33b935fbfb7a0a15fad0b97a7f7c65de372301"
}
SIDE = F(99, 20)
SPEC = dict(cap="4.95", scale=50,
            orbits=[[10,9],[20,9],[5,17],[15,17],[25,17],[10,25],[20,25]],
            marks=22, erosion="1/100000", depth=18, symmetry="D2")
SIZE = 22
N = 20

def marks(spec):
    side, den = F(spec["cap"]), spec["scale"]
    return sorted({(side*F(i, den), side*F(j, den))
                   for a, b in spec["orbits"]
                   for i in (a, den-a) for j in (b, den-b)})

def owners(mask):
    return [i for i in range(SIZE) if mask >> i & 1]

def classes():
    points = marks(SPEC)
    assert len(points) == SIZE
    perm = [[points.index((SIDE-x if rx else x, SIDE-y if ry else y))
             for x, y in points] for rx, ry in product(range(2), repeat=2)]
    assert len({tuple(g) for g in perm}) == 4
    unassigned = set(combinations(range(SIZE), 2))
    result, complete = [], set()
    for pair in sorted(unassigned):
        if pair in complete:
            continue
        orbit = {tuple(sorted(g[i] for i in pair)) for g in perm}
        assert not (orbit & complete)
        complete.update(orbit)
        result.append((1 << SIZE)-1-sum(1 << i for i in pair))
    assert complete == unassigned and len(complete) == 231 and len(result) == 67
    return sorted(result)

def checked_sources(target, offline):
    def copy(item):
        name, expected = item
        if offline:
            data = (offline/name).read_bytes()
        else:
            request = Request(URL+name, headers={"User-Agent": "n20-proof-replay"})
            with urlopen(request, timeout=90) as response:
                data = response.read()
        blob = b"blob " + str(len(data)).encode("ascii") + b"\0" + data
        if hashlib.sha1(blob).hexdigest() != expected:
            raise ValueError("Source differs from the pinned Git blob: " + name)
        (target/name).write_bytes(data)
    with ThreadPoolExecutor(5) as pool:
        list(pool.map(copy, BLOBS.items()))

def candidates(state, base_bins):
    fine_grid, boxes = state
    ranked = []
    for tile, rows in boxes.items():
        for axis, (low, high) in enumerate(((1,2),(3,4),(0,0))):
            lower = min(r[low] for r in rows)
            upper = max(r[high] for r in rows)
            if axis == 2:
                lower = lower*base_bins//fine_grid
                upper = ((upper+1)*base_bins+fine_grid-1)//fine_grid
                midpoint = (lower+upper)//2
                if not lower < midpoint < upper:
                    continue
                rank = min((upper-lower)/base_bins, .55)*.6
            else:
                if upper-lower < 1000:
                    continue
                midpoint = (lower+upper)//2
                rank = (upper-lower)/1_000_000
            ranked.append((rank, (tile, 2*axis, midpoint)))
    return [cut for _,cut in sorted(ranked, reverse=True)]

def diagnostic_program(native):
    # Read-only instrumentation exports outer boxes only to choose candidate cuts.
    # The final proof always invokes the original executable without this patch.
    source = (native/"r.cc").read_text()
    before = "int main(int ac,char**av)"
    report = r"""
void n20_boxes(const Engine &e, const vector<int> &O) {
  cout << "BOX " << e.rows[0].gi << " " << O.size() << '\n';
  for(int j:O) {
    cout << j;
    for(int k=0;k<e.B;k++) if(!e.init[k][j].empty()) {
      auto a=bbox(e.init[k][j]);
      cout << " " << e.rows[k].ki << " " << a.l << " " << a.r << " " << a.b << " " << a.t;
    }
    cout << '\n';
  }
}
"""
    changes = [(before,report+before),
               ("if(!fine(e,O,F,L)){cout","if(!fine(e,O,F,L)){n20_boxes(e,O);cout"),
               ('cout<<(rc?"F":"OPEN")','if(!rc)n20_boxes(e,O);cout<<(rc?"F":"OPEN")')]
    for old,new in changes:
        assert source.count(old) == 1
        source = source.replace(old,new)
    path = native/"n20_report.cc"
    path.write_text(source)
    subprocess.run(["g++","-O3","-std=c++17",str(path),"-o",str(native/"report")],check=True)

def parse_boxes(lines):
    tag, grid, count = lines[0].split()
    assert tag == "BOX" and len(lines) == int(count)+1
    result = {}
    for line in lines[1:]:
        i,*values = map(int,line.split())
        assert len(values) and len(values)%5 == 0
        result[i] = [values[p:p+5] for p in range(0,len(values),5)]
    return int(grid), result

def input_line(mask, settings, path):
    return " ".join(map(str,[*settings,N,*owners(mask),*[j for cut in path for j in cut]]))+"\n"

def run_native(program, table, mask, settings, path=(), report=False):
    lines = subprocess.check_output([str(program),str(table)],
        input=input_line(mask,settings,path),text=True).splitlines()
    stage, reason, who, step, bins = lines[-1].split()
    if stage == "OPEN":
        assert reason == "0"
        return None, parse_boxes(lines[:-1]) if report else None
    assert stage in ("C","F") and reason in ("1","2") and int(who) in owners(mask)
    assert 0 <= int(step) < (settings[0] if stage == "C" else settings[3])
    return (stage,int(reason),int(who),int(step),int(bins)), None

PHASES = [(32,(12,2,16,1),0), (48,(32,3,32,5),0),
          (64,(90,6,128,36),1), (96,(170,8,512,70),1)]

def search_case(mask, native, tables):
    for bins,settings,mode in PHASES:
        answer,_ = run_native(native/f"verify{mode}",tables[bins],mask,settings)
        if answer:
            return {"tree":{"end":[bins,settings,mode]}}
    bins, settings = 64, (70,4,128,24)
    leaf = {"end":[bins,settings,1]}
    @lru_cache(maxsize=512)
    def diagnose(path):
        return run_native(native/"report",tables[bins],mask,settings,path,True)
    def find(path, depth):
        answer, state = diagnose(path)
        if answer:
            return leaf
        if depth >= 8:
            slow = (170,8,512,75)
            answer,_ = run_native(native/"verify1",tables[bins],mask,slow,path)
            return {"end":[bins,slow,1]} if answer else None
        options = candidates(state,bins)[:36]
        def probe(cut):
            tile,axis,value = cut
            choices, severity, remaining = [], 0.0, 0
            for direction in (axis,axis+1):
                branch = path+((tile,direction,value),)
                verdict, box = diagnose(branch)
                choices.append((branch,verdict))
                if verdict is None:
                    remaining += 1
                    severity += sum(len(r) for r in box[1].values())/box[0]+len(candidates(box,bins))/100
            return (remaining,severity),cut,choices
        trials=[]
        for start in range(0,len(options),4):
            trials.extend(probe(cut) for cut in options[start:start+4])
            score = min(row[0][0] for row in trials)
            if score == 0 or (score == 1 and start>=8):
                break
        for _, cut, choices in sorted(trials,key=lambda entry:entry[0]):
            children = []
            for branch,verdict in choices:
                tree = leaf if verdict else find(branch,depth+1)
                if tree is None:
                    break
                children.append(tree)
            if len(children) == 2:
                return {"cut":cut,"children":children}
        return None
    tree = find((),0)
    if tree is None:
        raise ValueError(f"Unresolved class {mask:x}")
    return {"tree":tree, "angle_grid":bins}

def orient(t):
    den=1+t*t
    return (1-t*t)/den, 2*t/den

def crop(poly, y, above):
    result=[]
    for left,right in zip(poly,poly[1:]+poly[:1]):
        a=left[1]>=y if above else left[1]<=y
        b=right[1]>=y if above else right[1]<=y
        if a:
            result.append(left)
        if a!=b:
            portion=(y-left[1])/(right[1]-left[1])
            result.append((left[0]+portion*(right[0]-left[0]),y))
    return result

def covers_angle_strip(lo, hi):
    c,s=orient((lo+hi)/2)
    ends=[orient(lo),orient(hi)]
    agreement=[(c*u+s*v,abs(c*v-s*u)) for u,v in ends]
    assert all(dot>cross for dot,cross in agreement)
    half=(1-F(SPEC["erosion"]))/(2*max(dot+cross for dot,cross in agreement))
    inset=min(u+v for u,v in ends)/2
    right=SIDE-inset
    def rotate(x,y):
        return c*x+s*y,c*y-s*x
    rect=[rotate(x,y) for x,y in ((inset,inset),(right,inset),(right,right),(inset,right))]
    sites=[rotate(x,y) for x,y in marks(SPEC)]
    ymin=min(y for x,y in rect)
    ymax=max(y for x,y in rect)
    events=sorted({ymin,ymax}|{y+d for x,y in sites for d in (-half,half) if ymin<y+d<ymax})
    for low,high in zip(events,events[1:]):
        section=crop(crop(rect,low,True),high,False)
        if not section:
            continue
        xleft=min(x for x,y in section)
        xright=max(x for x,y in section)
        ranges=sorted((x-half,x+half) for x,y in sites if y-half<=low and high<=y+half)
        for left,right in ranges:
            if left>xleft:
                break
            xleft=max(xleft,right)
            if xleft>=xright:
                break
        if xleft<xright:
            return False
    return True

def horizontal_cover():
    # The tangent of the half-angle parameterizes every orientation.
    # Reflection reduces the angle to [0,pi/4]. The endpoint below exceeds tan(pi/8).
    end=F(5,12)
    assert (1+end)**2>2
    done=[]
    def visit(lo,hi,depth):
        if covers_angle_strip(lo,hi):
            done.append((lo,hi))
            return
        if depth==22:
            raise ValueError("Uncovered continuous range of tile orientations")
        mid=(lo+hi)/2
        visit(lo,mid,depth+1)
        visit(mid,hi,depth+1)
    for i in range(3):
        visit(i*end/3,(i+1)*end/3,0)
    assert done[0][0]==0 and done[-1][1]==end
    assert all(a[1]==b[0] for a,b in zip(done,done[1:]))
    return [(str(lo),str(hi)) for lo,hi in done]

def tree_leaves(mask, entry):
    grid = entry.get("angle_grid")
    valid_bins = {32,48,64,96}
    def walk(tree, path):
        assert isinstance(tree,dict)
        if set(tree) == {"end"}:
            b,settings,mode = tree["end"]
            assert type(b) is int and b in valid_bins and mode in (0,1)
            assert grid is None or grid == b
            assert len(settings) == 4 and all(type(i) is int for i in settings)
            nr,f,limit,fr = settings
            assert 1<=nr<=1000 and 2<=f<=64 and 4<=limit<=1024 and 1<=fr<=1000
            yield (b,settings,mode,path)
            return
        assert set(tree) == {"cut","children"} and len(tree["children"]) == 2 and len(path)<32
        tile,axis,v = tree["cut"]
        assert all(type(i) is int for i in (tile,axis,v))
        assert tile in owners(mask) and axis in (0,2,4)
        if axis == 4:
            assert grid in valid_bins and 0<v<grid
        else:
            assert 0<=v<=SIDE*1_000_000
        for bit,child in enumerate(tree["children"]):
            yield from walk(child,path+((tile,axis+bit,v),))
    assert set(entry) in ({"tree"},{"tree","angle_grid"})
    yield from walk(entry["tree"],())

def feasible_control():
    points = marks(SPEC)
    chosen = []
    for i,j in product(range(4),repeat=2):
        x,y = F(7,10)+i*F(21,20), F(73,100)+j*F(21,20)
        assert min(x,y)>=F(1,2) and max(x,y)+F(1,2)<SIDE
        ds = [max(abs(a-x),abs(b-y)) for a,b in points]
        assert min(ds)<F(1,2)
        chosen.append(ds.index(min(ds)))
    assert len(set(chosen))==16
    return sorted(chosen)

def replay(cases, native, tables, jobs):
    reps = classes()
    assert set(cases) == {format(m,"x") for m in reps}
    leaves = [(m,b,pars,mode,path) for m in reps
              for b,pars,mode,path in tree_leaves(m,cases[f"{m:x}"])]
    def check(job):
        m,b,pars,mode,path = job
        answer,_ = run_native(native/f"verify{mode}",tables[b],m,pars,path)
        assert answer, ("Unresolved",hex(m),path)
        stage,rc,tile,iteration,reported_bins = answer
        assert (reported_bins == b if stage=="C" else 2<=reported_bins<=pars[2])
        return [format(m,"x"),[list(cut) for cut in path],stage,rc,tile,iteration,reported_bins]
    with ThreadPoolExecutor(jobs) as pool:
        traces = sorted(pool.map(check,leaves))
    positive = feasible_control()
    for b,mode in sorted({(b,mode) for _,b,_,mode,_ in leaves}):
        query = " ".join(map(str,[24,2,2*b,12,len(positive),*positive]))+"\n"
        response = subprocess.check_output([native/f"verify{mode}",tables[b]],input=query,text=True)
        assert response.startswith("OPEN "), ("Feasible control excluded",b,mode)
    counts = Counter(row[2]+str(row[3]) for row in traces)
    outcome = hashlib.sha256(json.dumps(traces,separators=(",",":")).encode()).hexdigest()
    return dict(theorem="s(20) > 99/20",marks=22,vacancy_pairs=231,classes=67,
                terminal_regions=len(traces),verdicts=dict(sorted(counts.items())),
                feasible_control=16,verdict_sha256=outcome,upstream_commit=PIN), traces

def unique(pairs):
    result = {}
    for k,v in pairs:
        if k in result:
            raise ValueError("Duplicate JSON key "+k)
        result[k] = v
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream",type=Path,help="Pinned Mira Cult replay directory for offline use")
    parser.add_argument("--cases",type=Path,help="Replay an existing n20 certificate without search")
    parser.add_argument("--out",type=Path,default=Path("n20-replay"),help="Output directory")
    parser.add_argument("--jobs",type=int,default=4)
    args=parser.parse_args()
    if not __debug__ or not 1<=args.jobs<=32:
        parser.error("Use normal Python with assertions enabled and 1 to 32 jobs")
    source_file=Path(__file__).resolve()
    output=args.out.resolve()
    output.mkdir(parents=True,exist_ok=True)
    offline=args.upstream.resolve() if args.upstream else None
    arc_cover=horizontal_cover()
    print("Independent exact angle cover:",len(arc_cover),"intervals",flush=True)
    existing=json.loads(args.cases.read_bytes(),object_pairs_hook=unique) if args.cases else None
    old=Path.cwd()
    with tempfile.TemporaryDirectory() as tmp:
        tmp=Path(tmp)
        sources,native=tmp/"source",tmp/"native"
        sources.mkdir()
        native.mkdir()
        checked_sources(sources,offline)
        sys.path.insert(0,str(sources))
        os.chdir(sources)
        try:
            import check_stabs, nearest_rack, rack_lattice_input
            from verify_arc_lower import build, certified_init
            for module in (check_stabs,nearest_rack,rack_lattice_input):
                module.marks=marks
            result=check_stabs.check(SPEC)
            assert result["status"]=="STRICT_STABBING" and result["marks"]==22
            print("Pinned rational angle cover:",result,flush=True)
            build(native)
            tables={}
            for b,_,_ in PHASES:
                tables[b]=tmp/f"initial-{b}"
                certified_init(SPEC,b,tables[b])
            if existing is None:
                diagnostic_program(native)
                reps=classes()
                def job(mask):
                    data=search_case(mask,native,tables)
                    print("Excluded class",format(mask,"x"),flush=True)
                    return format(mask,"x"),data
                with ThreadPoolExecutor(args.jobs) as pool:
                    cases=dict(pool.map(job,reps))
            else:
                assert existing["n"]==20 and existing["rack"]==SPEC
                cases=existing["cases"]
            receipt,traces=replay(cases,native,tables,args.jobs)
            receipt["pinned_cover_intervals"]=result["rows"]
            receipt["independent_cover_intervals"]=len(arc_cover)
        finally:
            os.chdir(old)
    cert={"n":20,"rack":SPEC,"cases":cases}
    files={"n20_orientation_intervals.json":json.dumps(arc_cover,indent=1)+"\n",
           "n20_certificate.json":json.dumps(cert,indent=1)+"\n",
           "n20_verdicts.json":json.dumps(traces,indent=1)+"\n",
           "n20_receipt.json":json.dumps(receipt,indent=2)+"\n"}
    for name,content in files.items():
        (output/name).write_text(content)
    zip_path=output/"n20_marked_point_proof.zip"
    with ZipFile(zip_path,"w",compression=ZIP_DEFLATED) as bundle:
        bundle.write(source_file,"n20.py")
        for name,content in files.items():
            bundle.writestr(name,content)
        bundle.writestr("README.txt",
            "Joost de Winter, research direction. GPT6.2 Astra, AI author.\n"
            "Twenty independently movable and rotatable unit squares cannot fit in a closed square of side 99/20.\n"
            "The minimum exists by compactness, so s(20) > 99/20. The grid gives s(20) <= 5.\n"
            "Replay: python3 n20.py --cases n20_certificate.json\n"
            "The script downloads the pinned Mira Cult geometry sources. For offline use add --upstream /path/to/replay.\n"
            "The original mark pattern is the red set in Figure 3 of Wolfram Bentz, arXiv:1606.03746.\n")
    print(json.dumps(receipt,indent=2))
    print("Saved verified certificate and archive in",output)

if __name__=="__main__":
    main()

