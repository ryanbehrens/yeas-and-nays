"""Builds assets/districts/NNN.json: every House district for each Congress, with the member(s) seated when it began, for The Hill's House map.
Run from the project root:  python3 data/build_districts.py <simplified-geojson-dir> <mapshaper-bin>

Boundaries: Jeffrey B. Lewis, Brandon DeVine, Lincoln Pitcher and Kenneth C. Martis, "Digital Boundary Definitions of United States
Congressional Districts, 1789-2012" (UCLA), kept current through the 119th Congress at
https://github.com/JeffreyBLewis/congressional-district-boundaries (MIT License). Download the GeoJson folder, simplify it
(see SOURCES.txt), then run this script. Members: data/raw/congress/members.csv (Voteview). 120th: data/congress_2026.py.
"""
import os, sys, csv, json, glob, subprocess, collections, tempfile
sys.path.insert(0, os.path.dirname(__file__))
from political import NAMES
from parties import PARTY, nice
import congress_2026 as C26

SRC, MAPSHAPER = sys.argv[1], sys.argv[2]
ROOT = os.path.join(os.path.dirname(__file__), "..")
OUTDIR = os.path.join(ROOT, "assets", "districts"); os.makedirs(OUTDIR, exist_ok=True)
AB = {v: k for k, v in NAMES.items()}
party = lambda code: PARTY.get(code, ("Other", "O"))

# members seated at the start of each Congress, by (congress, state, district code)
rows = list(csv.DictReader(open(os.path.join(os.path.dirname(__file__), "raw", "congress", "members.csv"))))
seat = collections.defaultdict(list)
for r in rows:
    if r["chamber"] == "H": seat[(int(r["congress"]), r["state"], int(r["district"]))].append(r)
def seated(n, st, d):
    ms = seat.get((n, st, d), [])
    coded = [m for m in ms if m["occupancy"] in ("0", "1")]
    if n >= 28 and d not in (0, 98, 99): return sorted(coded or ms, key=lambda m: int(m["icpsr"]))[:1]
    return coded or (ms if d in (0, 98, 99) else sorted(ms, key=lambda m: int(m["icpsr"]))[:1])   # statewide seats: everyone listed
def members(n, st, d):
    """Members for a mapped district. Lewis numbers at-large/general-ticket seats 0; Voteview uses 0, 98, 99, or 1 for a lone seat."""
    if d == 0:
        ms = []
        for code in (0, 98, 99): ms += seated(n, st, code)
        if not ms: ms = seated(n, st, 1)
    else: ms = seated(n, st, d)
    return [[nice(m["name"]), *party(int(m["party"]))] for m in ms]

# simplified boundary files, one per state and range of Congresses
FEATS = collections.defaultdict(list)
for f in sorted(glob.glob(os.path.join(SRC, "*.geojson"))):
    for ft in json.load(open(f))["features"]:
        p = ft["properties"]; d = int(p["district"] or 0)
        if d < 0 or not ft.get("geometry"): continue   # -1: land not in any district (unorganized territory)
        st = AB.get(p["statename"].replace("_", " "))
        if not st: continue
        for n in range(int(p["startcong"]), int(p["endcong"]) + 1): FEATS[n].append((st, d, ft["geometry"]))

# each state's latest statewide (at-large) shape, for filling gaps
ATLARGE = {}
for n in sorted(FEATS):
    for st, d, g in FEATS[n]:
        if d == 0: ATLARGE[st] = g

def write(n, feats):
    tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    json.dump({"type": "FeatureCollection", "features": [{"type": "Feature", "properties": props, "geometry": g} for props, g in feats]}, tmp); tmp.close()
    out = os.path.join(OUTDIR, f"{n:03d}.json")
    subprocess.run([MAPSHAPER, "-i", tmp.name, "name=d", "-simplify", "interval=2000", "keep-shapes", "-o", out, "format=topojson", "quantization=10000"], check=True, capture_output=True)
    os.unlink(tmp.name)

stats = []
for n in range(1, 120):
    feats, nseats, nmembers = [], collections.Counter(), 0
    have = {(st, d) for st, d, _ in FEATS[n]}
    for st, d, g in FEATS[n]:
        # a statewide at-large shape drawn alongside numbered districts would cover them; those members are listed with the state instead
        if d == 0 and any(s == st and dd > 0 for s, dd in have): continue
        ms = members(n, st, d)
        numbered = sorted({k[2] for k in seat if k[0] == n and k[1] == st and 0 < k[2] < 98})
        if d == 0 and len(numbered) > 1:
            # the boundary data has only a statewide outline, but the state elected members by district: no district lines to color
            ms = []
            for code in sorted({k[2] for k in seat if k[0] == n and k[1] == st}): ms += members(n, st, code) if code else []
            feats.append(({"s": st, "d": 0, "m": ms, "x": 1}, g)); nmembers += len(ms); continue
        nmembers += len(ms)
        feats.append(({"s": st, "d": d, "m": ms}, g))
    # a state with members but no shape this Congress (the source lacks the Dakotas' at-large seat after 1913): use its at-large outline
    drawn = {st for st, _, _ in FEATS[n]}
    for st in sorted({k[1] for k in seat if k[0] == n} - drawn):
        g = ATLARGE.get(st)
        if g is None or st not in NAMES: continue
        ms = []
        for code in sorted({k[2] for k in seat if k[0] == n and k[1] == st}): ms += members(n, st, code) if code else []
        if ms: feats.append(({"s": st, "d": 0, "m": ms}, g)); nmembers += len(ms)
    write(n, feats); stats.append((n, len(feats), nmembers))
    if n == 119: last = feats

# the newly elected 120th: 2025 districts where the state kept them, 2026 winners
feats = []
for props, g in last:
    st, d = props["s"], props["d"]
    if st in C26.NEW_MAPS_2026: continue
    w = C26.HOUSE_120_DISTRICTS.get(f"{st}-{'AL' if d == 0 else d}")
    if w is None: continue
    nm, p = w if isinstance(w, list) else (None, w)
    feats.append(({"s": st, "d": d, "m": [[nm or "", {"D": "Democratic", "R": "Republican", "U": "Not yet called"}.get(p, p), {"U": "U"}.get(p, p)]], "e": 1}, g))
write(120, feats); stats.append((120, len(feats), len(feats)))
print("districts per Congress (n, shapes, members):", stats[:3], "...", stats[-4:])
