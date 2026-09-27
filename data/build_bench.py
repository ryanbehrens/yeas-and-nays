"""Builds The Bench: bench.html (Supreme Court justices and landmark rulings).
Run from the project root:  python3 data/build_bench.py
Also writes data/court_items.json, which data/build.py adds to the Ledger's timeline.
"""
import os, json, datetime as dt, statistics as st, sys, html
sys.path.insert(0, os.path.dirname(__file__))
from court import EXTRA, EXTRA_SERVICE, RULINGS, TOPICS, VOTE_FIX, LEAN_NAMES, mq_label
from political import PRESIDENTS as ALL_PRES
from build_presidents import head, FOOT, PORTRAIT_SLUG, side

ROOT = os.path.join(os.path.dirname(__file__), "..")
RAW = os.path.join(os.path.dirname(__file__), "raw", "court")
e = lambda s: html.escape(str(s), quote=True)
TODAY = "2026-09-26"

J = json.load(open(os.path.join(RAW, "justices.json")))
MQ = json.load(open(os.path.join(RAW, "martin_quinn.json")))
CASES = json.load(open(os.path.join(RAW, "cases.json")))

PRES_FIX = {"Ulysses Grant": "Ulysses S. Grant", "William H. Taft": "William Howard Taft"}
PRES_PARTY = {n: p for n, p, *_ in ALL_PRES}
def pres_party(name):
    p = PRES_PARTY.get(name, "")
    short = ("Republican" if p.startswith("Republican") else "Democratic" if ("Democrat" in p and not p.startswith("Democratic-Republican"))
             else "Democratic-Republican" if p.startswith("Democratic-Republican") else "Federalist" if p.startswith("Federalist")
             else "Whig" if p.startswith("Whig") and "expelled" not in p else "No party")
    return short
PARTY_ABBR = {"Republican": "R", "Democratic": "D", "Democratic-Republican": "DR", "Federalist": "F", "Whig": "W", "Whig (expelled)": "W*", "No party": "—"}

# ---------- service records ----------
recs = []
for x in J:
    ap = PRES_FIX.get(x["appointed_by"], x["appointed_by"])
    recs.append(dict(name=x["name"], scdb=x["scdb"], position=x["position"], appointed_by=ap, oath=x["oath"], ended=x["ended"],
                     end_reason=x["end_reason"], conf=x["conf"], born=x["born"]))
for x in EXTRA_SERVICE:
    base = next(r for r in recs if r["name"] == x["name"])
    recs.append(dict(base, position=x["position"], appointed_by=x["appointed_by"], oath=x["oath"], ended=x["ended"],
                     end_reason=x["end_reason"], conf=x.get("conf")))
for r in recs:
    r["party"] = pres_party(r["appointed_by"])
    r["pvar"] = side(r["party"] if r["party"] != "No party" else "unaffiliated")

# ---------- one entry per person ----------
people = {}
for r in sorted(recs, key=lambda r: r["oath"]):
    p = people.setdefault(r["name"], dict(name=r["name"], scdb=r["scdb"], born=r["born"], stints=[]))
    p["stints"].append({k: r[k] for k in ("position", "appointed_by", "party", "pvar", "oath", "ended", "end_reason", "conf")})
for p in people.values():
    ex = EXTRA.get(p["name"], {})
    first = p["stints"][0]["oath"][:4]; last = max((s["ended"] or TODAY) for s in p["stints"])
    series = {int(k): v for k, v in MQ.get(p["scdb"], {}).items()}
    terms_served = max(1, int(last[:4]) - int(first))
    p["mq"] = series
    if series and len(series) >= terms_served / 2:
        avg = st.mean(series.values()); p["lean"] = mq_label(avg); p["method"] = "score"; p["mq_avg"] = round(avg, 2)
        firstv, lastv = series[min(series)], series[max(series)]
        if abs(lastv - firstv) >= 1.5:
            p["drift"] = f"Moved {'left' if lastv < firstv else 'right'} over time: {firstv:+.2f} in {min(series)} to {lastv:+.2f} in {max(series)}."
    elif ex.get("lean"):
        p["lean"] = ex["lean"]; p["method"] = "history"; p["basis"] = ex.get("basis", "")
    else:
        p["lean"] = "nr"; p["method"] = "none"
    p["known"] = ex.get("known", "")
    p["current"] = any(s["ended"] is None for s in p["stints"])
    p["chief"] = any(s["position"] == "chief" for s in p["stints"])
    p["id"] = p["name"].lower().replace(".", "").replace(",", "").replace("'", "").replace(" ", "-")
    p["first"] = p["stints"][0]["oath"]; p["last"] = None if p["current"] else last

# ---------- who sat on the Court on a given date ----------
def seated(iso):
    out = []
    for r in recs:
        if r["oath"] <= iso and (r["ended"] is None or r["ended"] > iso):
            out.append(r)
    return out

# yearly snapshots (July 1) for the balance chart
years = list(range(1790, 2027))
balance = []
for y in years:
    iso = f"{y}-07-01" if y < 2026 else TODAY
    row = dict(y=y, lean={}, party={})
    for r in seated(iso):
        p = people[r["name"]]; row["lean"][p["lean"]] = row["lean"].get(p["lean"], 0) + 1
        ab = PARTY_ABBR[r["party"]]; row["party"][ab] = row["party"].get(ab, 0) + 1
    balance.append(row)

# ---------- rulings ----------
US_FIX = {"bostock": "590 U.S. 644", "dobbs": "597 U.S. 215", "bruen": "597 U.S. 1", "loperbright": "603 U.S. 369", "trumpus": "603 U.S. 593"}
TOPIC_TO_CAT = {"rights": "rights", "speech": "speech", "justice": "justice", "privacy": "privacy", "power": "power", "elections": "elections", "economy": "money"}
rulings = []
for r in RULINGS:
    c = CASES[r["id"]]; maj, dis = list(c["maj"]), list(c["dis"]); note = ""
    fx = VOTE_FIX.get(r["id"])
    if fx:
        if "maj" in fx: maj, dis = list(fx["maj"]), list(fx["dis"])
        for n in fx.get("drop", []): maj = [m for m in maj if m != n]; dis = [m for m in dis if m != n]
        for n in fx.get("move_to_dis", []): maj = [m for m in maj if m != n]; dis.append(n)
        note = fx.get("note", "")
    date = c["decided"]
    def tag(names):
        out = []
        for n in names:
            rec = next((x for x in recs if x["name"] == n and x["oath"] <= date and (x["ended"] is None or x["ended"] >= date)), None) \
                  or next((x for x in recs if x["name"] == n), None)
            out.append(dict(n=n, id=people[n]["id"] if n in people else "", party=PARTY_ABBR[rec["party"]] if rec else "—", pvar=rec["pvar"] if rec else "var(--mix)",
                            lean=people[n]["lean"] if n in people else "nr"))
        return out
    us = (c.get("cite") or {}).get("us") or US_FIX.get(r["id"])
    link = f"https://supreme.justia.com/cases/federal/us/{us.split()[0]}/{us.split()[-1]}/" if us else ""
    split = f"{len(maj)}–{len(dis)}"
    rulings.append(dict(r, date=date, split=split, author=c["author"] or "Unsigned (per curiam) or plurality", maj=tag(maj), dis=tag(dis),
                        cite=us or "", link=link, vote_note=note, legacy=date < "1946-01-01"))

# Items for the Ledger timeline (data/build.py merges these with its own rulings)
json.dump([dict(id=r["id"], title=r["title"], date=r["date"], split=r["split"], author=r["author"], bucket=r["bucket"],
                cat=TOPIC_TO_CAT[r["topic"]], metrics=[], summary=r["summary"], impact=r["impact"], bench=True) for r in rulings],
          open(os.path.join(os.path.dirname(__file__), "court_items.json"), "w"), indent=1)

# ---------- page ----------
def portrait_url(name):
    return None

PAGE = dict(people=sorted(people.values(), key=lambda p: p["first"]), balance=balance, rulings=rulings, topics=TOPICS, leans=LEAN_NAMES, today=TODAY)

import seo
BDESC = "All 116 Supreme Court justices: who appointed them, Republican or Democrat, and how they voted, plus 77 landmark rulings from Marbury v. Madison to Dobbs, sorted by what they did."
t = [head("The Supreme Court: every justice and landmark ruling | Yeas and Nays", BDESC, "", current="bench", path="/bench", image="/assets/og/bench.jpg",
          jsonld=[{"@context": "https://schema.org", "@type": "CollectionPage", "name": "The Bench: the Supreme Court", "url": seo.url("/bench"), "description": BDESC,
                   "about": {"@type": "GovernmentOrganization", "name": "Supreme Court of the United States"}},
                  seo.breadcrumbs(("Yeas and Nays", "/"), ("The Bench", "/bench"))])]
t.append("""  <nav class="crumbs">The Bench</nav>
  <section class="hero" style="grid-template-columns:1fr;padding-bottom:6px">
    <div><div class="eyebrow">The Supreme Court</div><h1>The Bench</h1>
    <p class="sum">All 116 justices: who appointed them, whether that president was a Republican or a Democrat, and how each one actually voted. Plus the landmark rulings that shaped the country, sorted by what they did.</p></div>
  </section>
  <nav class="jump" aria-label="Jump to section"><a href="#court">The Court on a date</a><a href="#balance">Balance over time</a><a href="#justices">Every justice</a><a href="#rulings">Landmark rulings</a><a href="#method">How this works</a></nav>

  <section id="court" class="block" style="border-top:0">
    <h2 id="courtTitle">The Court today</h2>
    <p class="lede" id="courtSum"></p>
    <div class="yearpick"><input type="range" id="yearRange" min="1790" max="2026" value="2026" aria-label="Year"><output id="yearOut">2026</output><button type="button" class="pbtn" id="yearNow">Today</button></div>
    <div class="seats" id="seats"></div>
  </section>

  <section id="balance" class="block">
    <h2>The Court's balance over time</h2>
    <p class="lede">Each column is one year: how many seated justices leaned which way, and which party's president appointed them. Tap a year to see that Court above.</p>
    <div class="card"><h3>How the justices leaned</h3><div class="chart" id="chLean"></div><div class="legend" id="legLean"></div>
      <p class="note">From 1937 on, lean comes from Martin-Quinn voting scores; before that it is a labeled historians' assessment, and before 1865 most justices are not rated.</p></div>
    <div class="card" style="margin-top:14px"><h3>Who appointed them</h3><div class="chart" id="chParty"></div><div class="legend" id="legParty"></div></div>
  </section>

  <section id="justices" class="block">
    <h2>Every justice</h2>
    <p class="lede">Tap a justice for how their lean was decided, what they're known for and, since 1937, how their voting changed year by year.</p>
    <div class="filters" id="jFilters"></div>
    <div class="jgrid" id="jGrid"></div>
  </section>

  <section id="rulings" class="block">
    <h2>Landmark rulings</h2>
    <p class="lede">Sorted by what the ruling did, not who decided it. Tap one for the vote, who wrote it, and which party's presidents appointed the majority and the dissenters.</p>
    <div class="filters" id="rFilters"></div>
    <div class="list" id="rList"></div>
  </section>

  <section id="method" class="block">
    <div class="method"><b>How this works.</b>
      <p><b>Appointed by.</b> Every justice shows the president who appointed them and that president's party: Republican, Democratic, or for the early Court, Federalist, Democratic-Republican or Whig. Washington belonged to no party.</p>
      <p><b>Lean, 1937 on.</b> Political scientists Andrew Martin and Kevin Quinn score every justice every term from their actual votes. Below zero is liberal, above zero conservative. A justice's lean here is the average of their yearly scores: Liberal (−1 or lower), Leans liberal (−1 to −0.5), Moderate (−0.5 to 0.5), Leans conservative (0.5 to 1), Conservative (1 or higher). Justices who moved a lot are flagged.</p>
      <p><b>Lean, 1865–1936.</b> No voting scores exist, so these are labeled as a historians' assessment, with the reason given. Justices whose record is thin or mixed are left "Not rated."</p>
      <p><b>Before 1865.</b> Today's left and right don't fit the early Court's main fights, over federal versus state power and slavery, so these justices are not rated; each card says what they're known for instead.</p>
      <p><b>Rulings.</b> <span style="color:var(--dem)">Liberal-leaning</span> means the outcome liberals generally sought: wider civil rights and liberties, more protection for people accused of crimes, or more room for government to regulate the economy. <span style="color:var(--rep)">Conservative-leaning</span> is the reverse, including gun rights and limits on federal agencies. <span style="color:var(--mix)">Mixed</span> covers rulings about how government is structured and split decisions.</p>
      <p><b>Sources.</b> Justices, votes and dates: the Supreme Court Database (Spaeth, Epstein, Martin, Segal, Ruger &amp; Benesh), via the <a href="https://github.com/KaraZajac/JUDGMENT" target="_blank" rel="noopener">JUDGMENT</a> project, and the Federal Judicial Center. Voting scores: <a href="https://mqscores.wustl.edu/" target="_blank" rel="noopener">Martin-Quinn scores</a>. Vote lists before 1946 come from the database's older files and a few have been corrected where participation is well documented. Full opinions link to Justia.</p>
    </div>
  </section>
""")
t.append(FOOT)
t.append(f'<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>\n<script>window.BENCH={json.dumps(PAGE, separators=(",", ":"))};</script>\n<script src="assets/bench.js"></script>\n</body>\n</html>\n')
open(os.path.join(ROOT, "bench.html"), "w").write("".join(t))
print(f"built bench.html: {len(people)} justices, {len(rulings)} rulings")
