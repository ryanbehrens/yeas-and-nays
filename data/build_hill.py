"""Builds The Hill: hill.html (Congress: seats, control, Speakers, polarization and landmark laws).
Run from the project root after data/build.py:  python3 data/build_hill.py
"""
import os, json, sys, html
sys.path.insert(0, os.path.dirname(__file__))
from congress_meta import SPEAKERS, SENATE_LEADERS, PENDING_LEADERS
from political import PRESIDENTS as ALL_PRES
from build_presidents import head, FOOT, PORTRAIT_SLUG
import seo

ROOT = os.path.join(os.path.dirname(__file__), "..")
RAW = os.path.join(os.path.dirname(__file__), "raw", "congress")
e = lambda s: html.escape(str(s), quote=True)

DIV = json.load(open(os.path.join(RAW, "divisions.json")))
POL_PATH = os.path.join(RAW, "polarization.json")
POL = json.load(open(POL_PATH)) if os.path.exists(POL_PATH) else None
_txt = open(os.path.join(ROOT, "app", "data.js")).read()
D = json.JSONDecoder().raw_decode(_txt[_txt.index("{"):])[0]
SITE_CONG = {c["n"]: c for c in D["congresses"]}

def family(name):
    """Party family code for a chamber-control or president party label."""
    if not name: return None
    n = name.lower()
    if n.startswith(("unaffiliated", "whig (expelled")): return None
    if n.startswith(("pro-administration", "federalist")): return "F"
    if n.startswith(("anti-administration", "democratic-republican", "jackson & crawford")): return "DR"
    if n.startswith(("adams", "anti-jackson", "national republican")): return "NR"
    if n.startswith("whig"): return "W"
    if n.startswith(("republican", "opposition")): return "R"
    if n.startswith(("jacksonian", "democratic")) or "democrat" in n: return "D"
    return None
PRES_FAMILY_FIX = {"John Quincy Adams": "NR", "Andrew Johnson": "D"}

def presidents_during(start, end):
    return [dict(name=n, party=p, fam=PRES_FAMILY_FIX.get(n, family(p))) for n, p, s, en in ALL_PRES if s < end and (en or "9999") > start]

congresses = []
for c in DIV:
    n = c["n"]; ctl = c.get("control", {})
    # A Congress elected but not yet seated isn't in the Ledger's data; label it from its own division data
    sc = SITE_CONG.get(n) or dict(house={"D": "Democratic", "R": "Republican"}[ctl["house"]], senate={"D": "Democratic", "R": "Republican"}[ctl["senate"]])
    hf = ctl.get("house") or family(sc["house"])
    sf = ctl.get("senate") or ("shared" if sc["senate"].startswith("Shifted") else family(sc["senate"]))
    FAMLABEL = {"D": "Democratic", "R": "Republican"}
    hl, sl = sc["house"], sc["senate"]
    if ctl.get("house") in FAMLABEL and family(hl) != ctl["house"]: hl = FAMLABEL[ctl["house"]] + " (organized the House)"
    if ctl.get("senate") in FAMLABEL and family(sl) != ctl["senate"]: sl = FAMLABEL[ctl["senate"]] + " (organized the Senate)"
    prs = presidents_during(c["start"], c["end"])
    # the president once the Congress is underway (Congresses since 1935 begin Jan 3, before Inauguration Day)
    import datetime as _dt
    probe = (_dt.date.fromisoformat(c["start"]) + _dt.timedelta(days=30)).isoformat()
    cur = [x for x, (nm, p, s, en) in zip(prs, [r for r in ALL_PRES if r[2] < c["end"] and (r[3] or "9999") > c["start"]]) if s <= probe]
    pf = (cur[-1] if cur else prs[0])["fam"] if prs else None
    kind = ("none" if pf is None else "unified" if pf == hf == sf else "divided")
    congresses.append(dict(n=n, start=c["start"], end=c["end"], house=c["house"], senate=c["senate"], senate_vacant=c.get("senate_vacant", 0),
        house_ctl=hf, senate_ctl=sf, house_label=hl, senate_label=sl, note=ctl.get("note", ""),
        speakers=[dict(name=a, party=b) for a, b in SPEAKERS.get(n, [])], leaders=[dict(name=a, party=b) for a, b in SENATE_LEADERS.get(n, [])],
        presidents=prs, gov=kind, gov_fam=pf if kind == "unified" else None, elect=c.get("elect"), pending=PENDING_LEADERS.get(n)))
SEATED = [c for c in congresses if not c["elect"]]
ELECT = next((c for c in congresses if c["elect"]), None)

# Landmark laws (the Ledger's list), with who held each chamber
laws = []
for it in D["items"]:
    if it["type"] not in ("law", "amendment"): continue
    laws.append({k: it.get(k) for k in ("id", "title", "date", "type", "bucket", "cat", "summary", "impact", "congress", "president", "how", "vote", "pattern")})

ORD = lambda n: f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"
PAGE = dict(congresses=congresses, laws=laws, pol=POL, pslug=PORTRAIT_SLUG)

HDESC = ("Every Congress from 1789 to today: House and Senate seats by party, who held the majority, Speakers and Senate leaders, "
         "unified and divided government, how far apart the parties vote, and the landmark laws each Congress passed.")
t = [head("Congress: every House and Senate since 1789 | Yeas and Nays", HDESC, "", current="hill", path="/hill", image="/assets/og/hill.jpg",
          jsonld=[{"@context": "https://schema.org", "@type": "CollectionPage", "name": "The Hill: Congress", "url": seo.url("/hill"), "description": HDESC,
                   "about": {"@type": "GovernmentOrganization", "name": "United States Congress"}},
                  seo.breadcrumbs(("Yeas and Nays", "/"), ("The Hill", "/hill"))])]
t.append(f"""  <nav class="crumbs">The Hill</nav>
  <section class="hero" style="grid-template-columns:1fr;padding-bottom:6px">
    <div><div class="eyebrow">Congress</div><h1>The Hill</h1>
    <p class="sum">All {len(SEATED)} Congresses from 1789 to today{f", plus the {ORD(ELECT['n'])}, elected in November {int(ELECT['start'][:4]) - 1}" if ELECT else ""}: who held the seats, who ran each chamber, when one party controlled everything, how far apart the parties vote, and the landmark laws they passed.</p></div>
  </section>
  <nav class="jump" aria-label="Jump to section"><a href="#congress">A Congress</a><a href="#balance">Seats over time</a><a href="#size">Size</a><a href="#control">Who ran Washington</a><a href="#polar">Polarization</a><a href="#laws">Landmark laws</a><a href="#every">Every Congress</a><a href="#method">How this works</a></nav>

  <section id="congress" class="block" style="border-top:0">
    <div class="elect-banner" id="electBanner" hidden></div>
    <h2 id="cTitle">The {ORD(SEATED[-1]["n"])} Congress</h2>
    <p class="lede" id="cSub"></p>
    <div class="yearpick"><input type="range" id="cRange" min="1" max="{len(congresses)}" value="{len(congresses)}" aria-label="Congress"><output id="cOut"></output><button type="button" class="pbtn" id="cNow">Today</button>{'<button type="button" class="pbtn" id="cElect">Just elected</button>' if ELECT else ""}</div>
    <div class="viewbar"><div class="vseg" role="group" aria-label="Show Congress as"><button type="button" data-v="seats" aria-pressed="true">Seat charts</button><button type="button" data-v="map" aria-pressed="false">Map</button></div>
      <div class="vseg" id="chSeg" role="group" aria-label="Chamber" hidden><button type="button" data-c="S" aria-pressed="true">Senate</button><button type="button" data-c="H" aria-pressed="false">House</button></div></div>
    <div class="card mapcard" id="mapCard" hidden><h3 id="mapH">Senate</h3><p class="cap" id="mapCap"></p><div class="mapwrap"><svg id="cMap" viewBox="0 0 975 610" role="img" aria-label="Map of the states"></svg></div>
      <div class="legend" id="mapLeg"></div><details class="statelist"><summary>Every state</summary><div id="mapTable"></div></details><p class="note" id="mapNote"></p></div>
    <div class="chambers" id="seatCharts"><div class="card"><h3>House of Representatives</h3><div class="hemi" id="hemiH"></div><div class="legend" id="legH"></div></div>
      <div class="card"><h3>Senate</h3><div class="hemi" id="hemiS"></div><div class="legend" id="legS"></div></div></div>
    <div class="cfacts" id="cFacts"></div>
    <div id="cLaws"></div>
  </section>

  <section id="balance" class="block">
    <h2>Seats over time</h2>
    <p class="lede">Each column is one Congress: the share of seats each party held when it began. Tap a column to see that Congress above.</p>
    <div class="card"><h3>House</h3><div class="chart" id="chBalH"></div></div>
    <div class="card" style="margin-top:14px"><h3>Senate</h3><div class="chart" id="chBalS"></div></div>
    <div class="legend" id="legBal" style="margin-top:8px"></div>
  </section>

  <section id="size" class="block">
    <h2>How big Congress got</h2>
    <p class="lede">Members seated at the start of each Congress. The House grew with the population until it was capped at 435 in 1913 (briefly 437 when Alaska and Hawaii joined); the Senate grows by two with each new state. The dips in the 1860s are the seats left empty by the states that seceded.</p>
    <div class="card"><div class="chart" id="chSize"></div><div class="legend"><span><i class="sw" style="background:var(--accent)"></i>House</span><span><i class="sw" style="background:var(--int)"></i>Senate</span></div></div>
  </section>

  <section id="control" class="block">
    <h2>Who ran Washington</h2>
    <p class="lede">Unified government means one party held the White House, the House and the Senate at the start of a Congress; divided means power was split. Tap a Congress for details.</p>
    <div class="card"><div class="govband" id="govBand"></div><div class="legend" id="legGov"></div><p class="lede" id="govSum" style="margin-top:10px"></p></div>
  </section>

  <section id="polar" class="block">
    <h2>How far apart the parties vote</h2>
    <p class="lede" id="polSum">Political scientists score every member of Congress from their roll-call votes, from −1 (most liberal) to +1 (most conservative). The gap between the two parties' typical members is the standard measure of polarization.</p>
    <div class="card"><div class="chart" id="chPol"></div><div class="legend" id="legPol"></div><p class="note" id="polNote"></p></div>
  </section>

  <section id="laws" class="block">
    <h2>Landmark laws</h2>
    <p class="lede">The laws on the home timeline, with the Congress that passed them and who held each chamber.</p>
    <div class="filters" id="lFilters"></div>
    <div class="list" id="lList"></div>
  </section>

  <section id="every" class="block">
    <h2>Every Congress</h2>
    <p class="lede">Each Congress lasts two years. Tap one for its seats, leaders, president and landmark laws.</p>
    <div class="list" id="eList"></div>
  </section>

  <section id="method" class="block">
    <div class="method"><b>How this works.</b>
      <p><b>Seats.</b> Party divisions at the start of each Congress, from the Office of the House Historian and the Senate Historical Office. Early parties are shown in their own colors: Federalists and the pro-administration side in gold, Democratic-Republicans and the anti-administration side in teal, Adams and anti-Jackson supporters in orange, Whigs in amber. Smaller parties (Know-Nothings, Free Soilers, Populists, Progressives, independents and others) are gray.</p>
      <p><b>Who ran each chamber.</b> Usually the party with the most seats. Where that differs, as in 1917 and 1931 in the House or 50–50 Senates, the Congress notes who actually organized the chamber. Independents who caucus with a party are listed as independents.</p>
      <p><b>Unified or divided.</b> Based on the controlling party of each chamber when the Congress began and the president a month in, so a president inaugurated that January counts. Washington and John Tyler had no party. Before 1830 the early parties are compared as they were: Federalists, Democratic-Republicans and the Adams faction.</p>
      <p><b>Polarization.</b> DW-NOMINATE scores from Voteview (Jeffrey B. Lewis, Keith Poole, Howard Rosenthal and others, UCLA), the standard measure political scientists use, built from every recorded roll-call vote. The chart shows each party's median member on the main left–right dimension.</p>
      <p><b>The newly elected Congress.</b> Before it is sworn in, the newest Congress shows the seats won in the last election as called by news organizations (including the Associated Press), with races not yet called shown as open seats and listed with their status. Numbers will change as the last races are called; leaders are shown once chosen. The current Congress keeps serving, in its lame-duck session, until then.</p>
      <p><b>The map.</b> Each state's senators and House members seated when the Congress began, from Voteview's member file (Jeffrey B. Lewis, Keith Poole, Howard Rosenthal and others, UCLA), drawn on the state borders of that date (Newberry Library, <i>Atlas of Historical County Boundaries</i>). A state with senators from two parties is striped in both colors; a House delegation is striped in proportion to its seats. Members who took office later in the Congress are left out, and in the earliest Congresses the totals can differ by a few seats from the historians' counts above. From 1959 on, the House map also draws today's county lines (U.S. Census Bureau, via Mike Bostock's us-atlas). For the current Congress and the newly elected one, each county is colored by the party of the member whose district covers it, striped by share of land where districts of different parties split a county, using the Census Bureau's district-to-county relationship file; states that drew new districts for 2026 are colored by state. Earlier Congresses are colored by state, because district maps for every Congress aren't available in a form this page can use. For the newly elected Congress, results by state come from Wikipedia's tallies of the AP's race calls (see the sources under the map).</p>
      <p><b>Speakers and Senate leaders</b> come from the House and Senate historians. The Senate had no formal majority leader until the 1910s.</p>
    </div>
  </section>
""")
t.append(FOOT)
t.append(f'<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>\n<script>window.HILL={json.dumps(PAGE, separators=(",", ":"))};</script>\n<script src="assets/hill.js"></script>\n</body>\n</html>\n')
open(os.path.join(ROOT, "hill.html"), "w").write("".join(t))
print(f"built hill.html: {len(SEATED)} seated Congresses{' + ' + ORD(ELECT['n']) + ' elect' if ELECT else ''}, {len(laws)} laws, polarization {'yes' if POL else 'pending'}")
