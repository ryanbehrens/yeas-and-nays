import json, re, glob, os, datetime as dt
from political import *
from laws import LAWS, RULINGS, EVENTS

RAW = os.path.join(os.path.dirname(__file__), "raw")
def csv(name, scale=1.0):
    out = {}
    for line in open(os.path.join(RAW, name)):
        y, v = line.strip().split(",")
        out[int(y)] = float(v) * scale
    return out

debt = csv("debt.csv")
deficit = csv("deficit_millions.csv", 1e6)
interest = csv("interest_millions.csv", 1e6)
gdp = csv("gdp_dollars.csv")
cpi = csv("cpi.csv")
pop = csv("population.csv")

years = list(range(1776, 2026))
econ = []
for y in years:
    d = dict(y=y, cpi=cpi.get(y))
    if y in pop: d["pop"] = int(pop[y])
    if y in debt: d["debt"] = round(debt[y])
    if y in gdp: d["gdp"] = round(gdp[y])
    if y in deficit:
        d["deficit"] = round(deficit[y]); d["deficitEst"] = False
    elif y in debt and (y - 1) in debt:
        # Before 1901: estimated from the year-over-year change in debt (surplus = debt paid down)
        d["deficit"] = round(-(debt[y] - debt[y - 1])); d["deficitEst"] = True
    if y in interest: d["interest"] = round(interest[y])
    econ.append(d)

# Congresses
def parse(txt):
    out = {}
    for l in txt.strip().splitlines():
        n, p, seats = l.split("|"); out[int(n)] = (p, seats)
    return out
H, S = parse(HOUSE), parse(SENATE)
congresses = []
for n in range(1, 120):
    if n <= 73:
        start = dt.date(1789 + 2 * (n - 1), 3, 4)
        end = dt.date(1789 + 2 * n, 3, 4) if n < 73 else dt.date(1935, 1, 3)
    else:
        start = dt.date(1935 + 2 * (n - 74), 1, 3); end = dt.date(1935 + 2 * (n - 73), 1, 3)
    congresses.append(dict(n=n, start=start.isoformat(), end=end.isoformat(), house=H[n][0], houseSeats=H[n][1], senate=S[n][0], senateSeats=S[n][1]))

def congress_for(date):
    for c in congresses:
        if c["start"] <= date < c["end"]: return c["n"]
    return congresses[-1]["n"]
def president_for(date):
    for name, party, s, e in PRESIDENTS:
        if s <= date and (e is None or date < e): return name
    return None

# Elections by state
CODE_MAP = {"Democratic":"D","Republican":"R","Progressive":"P","States' Rights":"SR","American Independent":"AI","Unpledged":"UNP","Unpledged Electors":"UNP","Independent":"AI","Democrat-Populist":"D","States' Rights Democratic":"SR"}
elections = {}
for y, parts in PRE1900.items():
    elections[y] = {st: p for p, sts in parts.items() for st in sts}
unknown = set()
for f in sorted(glob.glob(os.path.join(RAW, "package/270towin/*.js"))):
    y = int(os.path.basename(f)[:4]); t = open(f).read()
    states = json.loads(re.search(r"var states\s*=\s*(\{.*?\});", t, re.S).group(1))
    parties = json.loads(re.search(r"var parties\s*=\s*(\{.*?\});", t, re.S).group(1))
    res = {}
    for v in states.values():
        o = v["outcome"]
        if o in ("Z", "0"): continue
        pname = parties[o]["name"]
        code = CODE_MAP.get(pname)
        if y == 1960 and o == "6": code = "UNP"
        if code is None:
            unknown.add((y, pname)); code = "UNP"
        # split states: if more than one party got EVs, mark majority winner (ME/NE handled as majority)
        res[v["state_abbr"]] = code
    elections[y] = res
for y, parts in POST2012.items():
    elections[y] = {st: p for p, sts in parts.items() for st in sts}
print("unknown party names:", unknown)

def items(lst, typ):
    out = []
    for x in lst:
        x = dict(x); x.setdefault("type", typ)
        if typ != "event":
            x["congress"] = congress_for(x["date"])
        x["president"] = president_for(x["date"])
        x.setdefault("how", "Signed" if typ == "law" else None)
        out.append(x)
    return out

# State minimum wage history: Vaghul & Zipperer historical state minimum wage data (changes through 2022),
# plus U.S. DOL state table values for Jan 2023 and Jan 2024.
import warnings; warnings.filterwarnings("ignore")
import openpyxl
name2ab = {v: k for k, v in NAMES.items()}
state_mw = {}
wb = openpyxl.load_workbook(os.path.join(RAW, "zip_state.xlsx"), read_only=True)
for r in wb.active.iter_rows(min_row=2, values_only=True):
    if r[0] is None or r[5] is None: continue
    ab = FIPS.get("%02d" % int(r[0]))
    if not ab: continue
    y, m, d = int(r[2]), int(r[3]), int(r[4])
    if y > 2022 or (m == 12 and d == 31 and y == 2022): continue  # 12/31/2022 rows are end-of-data markers
    state_mw.setdefault(ab, []).append(["%04d-%02d-%02d" % (y, m, d), round(float(r[5]), 2)])
for line in open(os.path.join(RAW, "dol_2023_2024.txt")):
    n, a23, a24 = line.strip().split("|"); ab = name2ab[n]
    state_mw.setdefault(ab, []).append(["2023-01-01", float(a23)])
    state_mw.setdefault(ab, []).append(["2024-01-01", float(a24)])
for ab in state_mw:
    rows = sorted(state_mw[ab]); out = []
    for dte, v in rows:
        if out and out[-1][1] == v: continue
        out.append([dte, v])
    state_mw[ab] = out

data = dict(
    econ=econ, stateMW=state_mw,
    presidents=[dict(name=n, party=p, start=s, end=e) for n, p, s, e in PRESIDENTS],
    congresses=congresses,
    elections={str(k): v for k, v in sorted(elections.items())},
    winners={str(k): v for k, v in WINNERS.items()},
    parties=PARTIES,
    statehood=STATEHOOD, original13=ORIGINAL13, stateNames=NAMES, fips=FIPS,
    fedMinWage=[dict(date=d, rate=r) for d, r in FED_MINWAGE],
    stateMinWage=STATE_MINWAGE_2026, stateMinWageNotes=STATE_MINWAGE_NOTES,
    items=sorted(items(LAWS, "law") + items(RULINGS, "ruling") + items(EVENTS, "event"), key=lambda x: x["date"]),
)
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "app"), exist_ok=True)
atlas = json.load(open(os.path.join(RAW, "package/states-albers-10m.json")))
with open(os.path.join(os.path.dirname(__file__), "..", "app", "data.js"), "w") as f:
    f.write("window.TIMELINE_DATA=" + json.dumps(data, separators=(",", ":")) + ";\n")
    f.write("window.US_ATLAS=" + json.dumps(atlas, separators=(",", ":")) + ";\n")
print("items:", len(data["items"]), "elections:", len(elections))
for y in sorted(elections): print(y, len(elections[y]), end="; ")
