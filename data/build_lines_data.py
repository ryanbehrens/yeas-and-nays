"""Builds assets/lines-data.js for The Lines (the gerrymandering page): by state and Congress, seats by party and district compactness;
by state and election, House votes vs. seats and the efficiency gap (1976 on, when the MIT Election Lab file is present).
Run from the project root after data/build_districts.py:  python3 data/build_lines_data.py

Votes: MIT Election Data and Science Lab, "U.S. House 1976-2024" (Harvard Dataverse, doi:10.7910/DVN/IG0UN2, CC0).
Saved as plain CSV in data/raw/elections/house_1976_2024.csv (see data/raw/congress/SOURCES.txt).
"""
import os, sys, csv, json, glob, statistics, collections
sys.path.insert(0, os.path.dirname(__file__))
from political import NAMES, STATEHOOD

ROOT = os.path.join(os.path.dirname(__file__), "..")
DDIR = os.path.join(ROOT, "assets", "districts")
VOTES = os.path.join(os.path.dirname(__file__), "raw", "elections", "house_1976_2024.csv")
med = lambda xs: round(statistics.median(xs), 3) if xs else None

# ---------- compactness and seats, every Congress ----------
cong, national = {}, {}
for f in sorted(glob.glob(os.path.join(DDIR, "*.json"))):
    n = int(os.path.basename(f)[:3])
    G = [g["properties"] for g in json.load(open(f))["objects"]["d"]["geometries"]]
    by = collections.defaultdict(list)
    for p in G: by[p["s"]].append(p)
    allpp = [p["pp"] for p in G if p.get("pp")]
    national[n] = dict(pp=med(allpp), districts=len(allpp))
    for st, ps in by.items():
        pp = [p["pp"] for p in ps if p.get("pp")]
        fam = collections.Counter(m[2] for p in ps for m in p.get("m", []))
        cong.setdefault(st, {})[n] = dict(seats=sum(len(p.get("m", [])) for p in ps), pp=med(pp), ppmin=min(pp) if pp else None,
                                         parties=dict(fam), drawn=len(pp), lines=not any(p.get("x") for p in ps))

# the 120th in states with new 2026 maps (no boundaries yet): seats and parties from the 2026 results
import congress_2026 as C26
for st, h in C26.HOUSE_120.items():
    if 120 not in cong.get(st, {}):
        cong.setdefault(st, {})[120] = dict(seats=h["seats"], pp=None, ppmin=None, parties={k: h[k] for k in ("D", "R", "U") if h[k]}, drawn=0, lines=False)

# ---------- votes vs. seats, 1976 on ----------
votes = {}
if os.path.exists(VOTES):
    rows = list(csv.DictReader(open(VOTES, encoding="utf-8", errors="replace"), delimiter="\t" if open(VOTES).readline().count("\t") > 3 else ","))
    DEM = {"DEMOCRAT", "DEMOCRATIC", "DEMOCRATIC-FARM-LABOR", "DEMOCRATIC-FARMER-LABOR", "DEMOCRATIC-NONPARTISAN LEAGUE", "DEMOCRATIC-NPL"}
    PARTY = lambda p: "D" if p in DEM else "R" if p.startswith("REPUBLICAN") else "O"
    NOTVOTE = ("BLANK", "VOID", "UNDERVOTE", "UNDER VOTE", "OVERVOTE", "OVER VOTE", "SCATTERING", "EXHAUSTED")
    races = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.Counter()))
    runoff = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.Counter()))
    for r in rows:
        if r.get("stage", "GEN") != "GEN" or r.get("special", "FALSE").upper() == "TRUE": continue
        if r["state_po"] not in NAMES or r["state_po"] == "DC": continue   # DC's delegate has no floor vote
        if r.get("mode", "TOTAL") not in ("TOTAL", ""): continue
        if (r.get("party") or "NA") in ("NA", "") and r["candidate"].upper().startswith(NOTVOTE): continue   # blank, void and undervotes
        try: v = int(float(r["candidatevotes"] or 0))
        except ValueError: continue
        key = (int(r["year"]), r["state_po"], int(float(r["district"] or 0)))
        # fusion tickets (New York): add each candidate's lines together, keeping the major-party label
        (runoff if r.get("runoff", "FALSE").upper() == "TRUE" else races)[key][r["candidate"]][PARTY((r.get("party") or "").upper())] += v
    agg = collections.defaultdict(lambda: dict(D=0, R=0, O=0, sD=0, sR=0, sO=0, wD=0, wR=0, two=0, unc=0, n=0))
    for (yr, st, d), cands in races.items():
        a = agg[(yr, st)]; a["n"] += 1
        tot = {c: sum(pc.values()) for c, pc in cands.items()}
        lab = {c: max(pc, key=lambda k: (k != "O", pc[k])) for c, pc in cands.items()}
        for c, v in tot.items(): a[lab[c]] += v
        win = max(tot, key=tot.get); wl = lab[win]
        if (yr, st, d) in runoff:   # decided in a runoff (Louisiana, Georgia): the seat goes to the runoff winner
            ro = runoff[(yr, st, d)]; rt = {c: sum(pc.values()) for c, pc in ro.items()}; rw = max(rt, key=rt.get)
            wl = max(ro[rw], key=lambda k: (k != "O", ro[rw][k]))
        a["s" + wl] += 1
        dv = sum(v for c, v in tot.items() if lab[c] == "D"); rv = sum(v for c, v in tot.items() if lab[c] == "R")
        if not dv or not rv: a["unc"] += 1; continue      # uncontested by one major party: left out of the efficiency gap
        T = dv + rv; need = T / 2
        if dv > rv: a["wD"] += dv - need; a["wR"] += rv
        else: a["wR"] += rv - need; a["wD"] += dv
        a["two"] += T
    for (yr, st), a in agg.items():
        tp = a["D"] + a["R"]
        votes.setdefault(st, {})[yr] = dict(dv=round(a["D"] / tp, 4) if tp else None, sD=a["sD"], sR=a["sR"], sO=a["sO"], seats=a["n"], unc=a["unc"],
            eg=round((a["wD"] - a["wR"]) / a["two"], 4) if a["two"] and a["n"] >= 2 else None)   # >0: Democratic votes wasted more, map tilts Republican

data = dict(states={st: dict(name=NAMES[st], since=STATEHOOD.get(st)) for st in NAMES if st != "DC"}, congress=cong, national=national, votes=votes,
            votes_years=sorted({y for v in votes.values() for y in v}))
open(os.path.join(ROOT, "assets", "lines-data.js"), "w").write("window.LINES=" + json.dumps(data, separators=(",", ":")) + ";\n")
print("wrote assets/lines-data.js", os.path.getsize(os.path.join(ROOT, "assets", "lines-data.js")) // 1024, "KB; vote data:", "yes" if votes else "not yet (save the MIT Election Lab file first)")
