"""Builds assets/hill-map.js: each Congress's senators and House delegation by state, for The Hill's maps.
Run from the project root:  python3 data/build_hill_map.py   (then python3 data/build_hill.py)

Sources: data/raw/congress/members.csv (Voteview member file, trimmed; see SOURCES.txt there) for the 1st-119th Congresses,
data/congress_2026.py for the newly elected 120th.
Members are those seated when the Congress began (Voteview "occupancy" 0 or 1), so later replacements are left out.
"""
import os, sys, csv, json, collections
sys.path.insert(0, os.path.dirname(__file__))
import congress_2026 as C26

ROOT = os.path.join(os.path.dirname(__file__), "..")
RAW = os.path.join(os.path.dirname(__file__), "raw", "congress")

from parties import PARTY, party, nice

rows = list(csv.DictReader(open(os.path.join(RAW, "members.csv"))))
by = collections.defaultdict(list)
for r in rows: by[(int(r["congress"]), r["chamber"], r["state"])].append(r)
occ = lambda r: int(r["occupancy"]) if r["occupancy"] else 0
votes = lambda r: int(r["votes"] or 0)
icpsr = lambda r: int(r["icpsr"])
NONSTATE = {"USA", "DC", "PR", "GU", "VI", "AS", "MP"}  # delegates and the resident commissioner have no vote on the floor

OUT = {}
for (n, ch, st), ms in by.items():
    if st in NONSTATE or len(st) != 2: continue
    c = OUT.setdefault(n, {"S": {}, "H": {}})
    start = [m for m in ms if occ(m) <= 1]
    if ch == "S":
        start = sorted(ms, key=lambda m: (m["occupancy"] not in ("0", "1"), icpsr(m)))[:2]
        c["S"][st] = [[nice(m["name"])] + list(party(int(m["party"]))) for m in start]
    else:
        seats = collections.defaultdict(list)
        for m in ms: seats[int(m["district"])].append(m)
        held = []
        for d, sm in seats.items():
            # Voteview occupancy: 0 = held the seat all Congress, 1 = first of several. Multi-member districts and general-ticket
            # states have several such members. Recent Congresses leave it blank: then the earliest member (lowest ICPSR id) is the one seated first.
            coded = [m for m in sm if m["occupancy"] in ("0", "1")]
            if n >= 28 and d not in (98, 99):   # single-member districts since 1843; the coding sometimes marks a replacement "0" too
                held += sorted(coded or sm, key=icpsr)[:1]
            else:
                held += coded or (sm if d in (0, 98, 99) else sorted(sm, key=icpsr)[:1])   # statewide seats: everyone listed
        cnt = collections.Counter(party(int(m["party"])) for m in held)
        c["H"][st] = [[p, f, k] for (p, f), k in cnt.most_common()]

# The newly elected 120th
FAM = {"D": ("Democratic", "D"), "R": ("Republican", "R"), "I": ("Independent", "O")}
c = OUT[120] = {"S": {}, "H": {}, "elect": True}
for st, ss in C26.SENATE_120.items():
    c["S"][st] = [[nm, *FAM[p], status] for nm, p, status in ss]
for st, h in C26.HOUSE_120.items():
    c["H"][st] = [x for x in [["Democratic", "D", h["D"]], ["Republican", "R", h["R"]], ["Not yet called", "U", h["U"]]] if x[2]]

OUT[120]["newmaps"] = C26.NEW_MAPS_2026

data = dict(congresses={str(k): v for k, v in sorted(OUT.items())}, as_of_120=C26.AS_OF, sources_120=C26.SOURCES)
open(os.path.join(ROOT, "assets", "hill-map.js"), "w").write("window.HILLMAP=" + json.dumps(data, separators=(",", ":"), ensure_ascii=False) + ";\n")
# sanity check against the start-of-Congress divisions The Hill shows
DIV = {c["n"]: c for c in json.load(open(os.path.join(RAW, "divisions.json")))}
worst = []
for n, c in OUT.items():
    h = sum(k for v in c["H"].values() for _, f, k in v if f != "U"); s = sum(len(v) for v in c["S"].values())
    dh = sum(p["n"] for p in DIV[n]["house"]); ds = sum(p["n"] for p in DIV[n]["senate"])
    worst.append((abs(h - dh) + abs(s - ds), n, h, dh, s, ds))
worst.sort(reverse=True)
print("wrote assets/hill-map.js", os.path.getsize(os.path.join(ROOT, "assets", "hill-map.js")) // 1024, "KB; largest seat-count gaps vs divisions (n, house map/div, senate map/div):",
      [(n, f"{h}/{dh}", f"{s}/{ds}") for _, n, h, dh, s, ds in worst[:6]])
