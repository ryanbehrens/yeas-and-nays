"""Builds the Presidents section: presidents/index.html and one page per president in PRESIDENTS.
Run from the project root:  python3 data/build_presidents.py
"""
import os, json, html, datetime as dt, sys
sys.path.insert(0, os.path.dirname(__file__))
from presidents_data import PRESIDENTS
from political import PRESIDENTS as ALL_PRES, FED_MINWAGE

ROOT = os.path.join(os.path.dirname(__file__), "..")
RAW = os.path.join(os.path.dirname(__file__), "raw")
e = lambda s: html.escape(str(s), quote=True)
TODAY = dt.date(2026, 9, 26)

def csv(name, scale=1.0):
    out = {}
    for line in open(os.path.join(RAW, name)):
        y, v = line.strip().split(","); out[int(y)] = float(v) * scale
    return out
debt = csv("debt.csv"); deficit = csv("deficit_millions.csv", 1e6); gdp = csv("gdp_dollars.csv")
cpi = csv("cpi.csv"); unemp = csv("unemployment_annual.csv")
LAST = 2025

def frac(iso):
    d = dt.date.fromisoformat(iso); return d.year + (d.timetuple().tm_yday - 1) / 365.25
def minwage(iso):
    r = None
    for d, v in FED_MINWAGE:
        if d <= iso: r = v
    return r
def money(v, digits=2):
    a = abs(v); s = "−" if v < 0 else ""
    for div, w in ((1e12, "trillion"), (1e9, "billion"), (1e6, "million")):
        if a >= div: return f"{s}${a/div:.{digits}f} {w}"
    return f"{s}${a:,.0f}"
def money_parts(v, digits=2):
    a = abs(v); s = "−" if v < 0 else "+"
    for div, w in ((1e12, "trillion"), (1e9, "billion"), (1e6, "million")):
        if a >= div: return f"{s}${a/div:.{digits}f}", w
    return f"{s}${a:,.0f}", ""
def fmt_date(iso):
    d = dt.date.fromisoformat(iso); return d.strftime("%B %-d, %Y")

ICON = open(os.path.join(ROOT, "assets", "icon-inline.svg")).read()
FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Libre+Caslon+Display&family=Libre+Caslon+Text:ital,wght@0,400;0,700;1,400&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&family=Merriweather:ital,wght@0,900;1,700&display=swap">'

def head(title, desc, up):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#0d1311">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="icon" type="image/svg+xml" href="{up}assets/yeas-nays-icon.svg">
{FONTS}
<link rel="stylesheet" href="{up}assets/site.css">
</head>
<body>
<div class="wrap">
  <header class="masthead">
    <a class="logo" href="{up}index.html" aria-label="Yeas and Nays home">{ICON}<span class="wm">Yeas<em>and</em>Nays</span></a>
    <nav class="sections" aria-label="Sections">
      <a href="{up}index.html">The Ledger</a>
      <a href="{up}presidents.html" aria-current="page">Presidents</a>
      <span title="Coming soon: the Supreme Court">The Bench <i>Soon</i></span>
      <span title="Coming soon: discussion and posts">The Floor <i>Soon</i></span>
    </nav>
  </header>
"""
FOOT = """  <footer class="pagefoot"><span>Yeas and Nays · How America got here, one vote at a time.</span><span>Every figure and claim links to its source. Spot an error? It will be corrected.</span></footer>
</div>
"""

# One file name per president: assets/presidents/<slug>.jpg (also used for future deep-dive pages)
PORTRAIT_SLUG = {"George Washington":"washington","John Adams":"jadams","Thomas Jefferson":"jefferson","James Madison":"madison",
  "James Monroe":"monroe","John Quincy Adams":"jqadams","Andrew Jackson":"jackson","Martin Van Buren":"vanburen",
  "William Henry Harrison":"whharrison","John Tyler":"tyler","James K. Polk":"polk","Zachary Taylor":"taylor",
  "Millard Fillmore":"fillmore","Franklin Pierce":"pierce","James Buchanan":"buchanan","Abraham Lincoln":"lincoln",
  "Andrew Johnson":"ajohnson","Ulysses S. Grant":"grant","Rutherford B. Hayes":"hayes","James A. Garfield":"garfield",
  "Chester A. Arthur":"arthur","Grover Cleveland":"cleveland","Benjamin Harrison":"bharrison","William McKinley":"mckinley",
  "Theodore Roosevelt":"troosevelt","William Howard Taft":"taft","Woodrow Wilson":"wilson","Warren G. Harding":"harding",
  "Calvin Coolidge":"coolidge","Herbert Hoover":"hoover","Franklin D. Roosevelt":"fdr","Harry S. Truman":"truman",
  "Dwight D. Eisenhower":"eisenhower","John F. Kennedy":"jfk","Lyndon B. Johnson":"lbj","Richard Nixon":"nixon",
  "Gerald Ford":"ford","Jimmy Carter":"carter","Ronald Reagan":"reagan","George H. W. Bush":"ghwbush",
  "Bill Clinton":"clinton","George W. Bush":"gwbush","Barack Obama":"obama","Donald Trump":"trump","Joe Biden":"biden"}

PARTY_HEX = {"F": "#c9a227", "DR": "#2f9e8f", "NR": "#d4803a", "W": "#e0a33a"}
def side(party):
    """True party color in every era: Democrats blue, Republicans red, earlier parties their own colors, gray for none."""
    l = party.lower()
    if l.startswith(("unaffiliated", "no party", "whig (expelled")): return "var(--mix)"
    if l.startswith("democratic-republican"): return PARTY_HEX["DR"]
    if l.startswith("federalist"): return PARTY_HEX["F"]
    if l.startswith("whig"): return PARTY_HEX["W"]
    if l.startswith("republican"): return "var(--rep)"
    if "democrat" in l: return "var(--dem)"
    return "var(--mix)"

def slug_for(name):
    for k, v in PRESIDENTS.items():
        if v["name"] == name: return k
    return None

def portrait(slug, name, cls="portrait", placeholder=True, up="../"):
    initials = "".join(w[0] for w in name.replace(".", "").split() if w[0].isupper())[:2]
    mono = f'<span class="mono">{e(initials)}</span>' + ('<span class="ph">Portrait coming</span>' if placeholder else "")
    if slug in PRESIDENTS or slug in PORTRAIT_SLUG.values():
        # Shows assets/presidents/<slug>.jpg if it exists; otherwise the image removes itself and the initials show.
        return mono + f'<img src="{up}assets/presidents/{slug}.jpg" alt="Official portrait of {e(name)}" loading="lazy" onerror="this.remove()">'
    return mono

LABEL = {"proven": "Proven", "charged": "Charged", "alleged": "Alleged", "disputed": "Disputed"}
STATUS = {"yes": "Yes", "partial": "Partly", "no": "No"}

def page(slug, p):
    terms = [(s, en or TODAY.isoformat()) for s, en in p["terms"]]
    tf = [(frac(s), frac(en)) for s, en in terms]
    y0 = max(1790, int(tf[0][0]) - 4); y1 = min(LAST, int(tf[-1][1]) + 3)
    econ = []
    for y in range(y0, y1 + 1):
        r = dict(y=y)
        if y in debt: r["debt"] = debt[y]
        if y in debt and y in gdp: r["ratio"] = round(debt[y] / gdp[y] * 100, 2)
        if y in deficit: r["bal"] = deficit[y]
        if y in unemp: r["unemp"] = unemp[y]
        if y in cpi and (y - 1) in cpi: r["infl"] = round((cpi[y] / cpi[y - 1] - 1) * 100, 2)
        econ.append(r)

    # --- headline numbers
    D, U = p["debt"], p["unemployment"]
    parts = [(D["start"], D["end"], D["start_label"], D["end_label"])]
    if "start2" in D: parts.append((D["start2"], D["end2"], D["start2_label"], D["end2_label"]))
    added = sum(b - a for a, b, *_ in parts)
    def fy_bounds(s, en):
        sd = dt.date.fromisoformat(s); sy = sd.year if sd.month >= 7 else sd.year - 1
        if sd.year <= 1842: sy = sd.year  # budget year = calendar year until 1842; Treasury figures are dated January 1
        ed = dt.date.fromisoformat(en); ey = ed.year - 1 if ed.month < 7 else ed.year
        if ed.year <= 1842: ey = ed.year  # January 1 figures
        sy = max(sy, 1790); ey = max(ey, sy)
        return sy, min(ey, LAST)
    ratio_txt = []; infl_txt = []; cost = []
    for i, (s, en) in enumerate(p["terms"]):
        sy, ey = fy_bounds(s, en or TODAY.isoformat())
        r0 = debt[sy] / gdp[sy] * 100; r1 = debt[ey] / gdp[ey] * 100
        ratio_txt.append((sy, ey, r0, r1))
        if ey > sy:
            avg = ((cpi[ey] / cpi[sy]) ** (1 / (ey - sy)) - 1) * 100
            infl_txt.append((sy, ey, avg, cpi[ey] / cpi[sy] * 100))
    eo_years = p["eo_by_year"]; eo_total = sum(eo_years.values()) if eo_years else p["eo_total"]
    yrs_in_office = sum((b - a) for a, b in tf)
    pard, comm = p["clem_total"] or (0, 0)
    groups = [g for gl in p.get("clem_group", {}).values() for g in gl]
    group_n = sum(n for _, n in groups)
    legal = {x["k"]: x for x in p["legal"]}
    party_var = side(p["party"])
    transition = "1896" <= p["terms"][0][0] < "1933"
    flipnote_t = ('<p class="flipnote">This presidency falls in the realignment era (1896–1932), when the two parties were trading positions and both had progressive and conservative wings.</p>' if transition else "")
    flipnote = ""
    term_txt = " and ".join(f'{s[:4]}–{(en or "")[:4] if en else "present"}' for s, en in p["terms"])

    t = [head(f'{p["name"]} · Yeas and Nays', f'{p["name"]}: the economy, executive orders, pardons, legal record and controversies, with sources.', "../")]
    t.append(f'  <nav class="crumbs"><a href="../presidents.html">Presidents</a> / {e(p["name"])}</nav>\n')
    t.append(f"""  <section class="hero">
    <div class="portrait">{portrait(slug, p["name"])}</div>
    <div>
      <div class="eyebrow">{e(p["number"])} president of the United States · {e(term_txt)}</div>
      <h1>{e(p["name"])}</h1>
      <div class="meta"><span class="chip"><span class="dot" style="background:{party_var}"></span>{e(p["party"])}</span><span class="chip">Vice president: {e(p["vp"])}</span><span class="chip">{e(p["left"])}</span></div>{flipnote}{flipnote_t}
      <p class="sum">{e(p["summary"])}</p>
    </div>
  </section>
  <nav class="jump" aria-label="Jump to section"><a href="#numbers">At a glance</a><a href="#economy">Economy</a><a href="#orders">Executive orders</a><a href="#pardons">Pardons</a><a href="#legal">Legal record</a><a href="#controversies">Controversies</a><a href="#quotes">In their words</a></nav>
""")
    # --- tiles
    sg = lambda v: "+" if v >= 0 else "−"
    debt_sub = " · ".join(f'{"1st term" if i == 0 and len(parts) > 1 else ("2nd term" if p["terms"][-1][1] else "2nd term so far") if i else "Start"}: {money(b - a)} ({sg(b - a)}{abs(b / a - 1) * 100:.0f}%)' if len(parts) > 1 else f'{money(a)} → {money(b)} ({sg(b - a)}{abs(b / a - 1) * 100:.0f}%)' for i, (a, b, *_) in enumerate(parts))
    a_num, a_unit = money_parts(abs(added)); a_num = ("+" if added >= 0 else "−") + a_num.lstrip("+")
    debt_lab = "Debt added" if added >= 0 else "Debt paid down"
    r = ratio_txt
    rf = lambda v: f"{v:.1f}%" if v < 10 else f"{v:.0f}%"
    ratio_val = rf(r[-1][3])
    ratio_sub = " · ".join(f'FY{sy}: {rf(r0)} → FY{ey}: {rf(r1)}' for sy, ey, r0, r1 in r)
    if U is None:
        u_sub, u_val, u_cap = "No national estimates before 1890", "—", "Economist Stanley Lebergott's yearly estimates, the earliest national series, begin in 1890"
    else:
      u_cap = U.get("cap", "Monthly rates; the chart shows yearly averages.")
      u_sub = f'{U["start_label"]}: {U["start"]}% → {U["end_label"]}: {U["end"]}%' + (f' · {U["start2_label"]}: {U["start2"]}% → {U["end2_label"]}: {U["end2"]}%' if "start2" in U else "")
      u_val = f'{U.get("end2", U["end"])}%'
    infl_val = f'{infl_txt[0][2]:.1f}%' if infl_txt else "—"
    infl_sub = " · ".join(f'{sy}–{ey}: {avg:.1f}% a year' for sy, ey, avg, _ in infl_txt) or "Too short a time in office to measure"
    t.append(f"""  <section id="numbers" class="block" style="border-top:0;padding-top:4px">
  <div class="tiles">
    <a class="tile" href="#economy"><div class="lab"><span class="dot" style="background:var(--debt)"></span>{debt_lab}</div><div class="val">{a_num}<small>{a_unit}</small></div><div class="sub">{e(debt_sub)}</div></a>
    <a class="tile" href="#economy"><div class="lab">Debt-to-GDP, latest</div><div class="val">{ratio_val}</div><div class="sub">{e(ratio_sub)}</div></a>
    <a class="tile" href="#economy"><div class="lab"><span class="dot" style="background:var(--int)"></span>Unemployment</div><div class="val">{u_val}</div><div class="sub">{e(u_sub)}</div></a>
    <a class="tile" href="#economy"><div class="lab"><span class="dot" style="background:var(--def)"></span>Average inflation</div><div class="val">{infl_val}{"<small>a year</small>" if infl_txt else ""}</div><div class="sub">{e(infl_sub)}</div></a>
    <a class="tile" href="#orders"><div class="lab">Executive orders</div><div class="val">{eo_total:,}</div><div class="sub">About {eo_total / yrs_in_office:.0f} a year in office</div></a>
    <a class="tile" href="#pardons"><div class="lab">Pardons &amp; commutations</div><div class="val">{f"{pard + comm + group_n:,}" if p["clem_total"] else "—"}</div><div class="sub">{f"{pard:,} pardons · {comm:,} commutations" if p["clem_total"] else "Not recorded before 1900"}{f" · about {group_n:,} by group proclamation" if group_n else ""}{f" ({e(p['clem_scope'])})" if p.get("clem_scope") else ""}</div></a>
    <a class="tile" href="#legal"><div class="lab">Impeached</div><div class="val">{e(p["impeached_short"])}</div><div class="sub">{e(legal["Impeached"]["v"])} · Convicted of a crime: {e(legal.get("Convicted", {}).get("v", "No"))}</div></a>
  </div>
  </section>
""")
    # --- economy
    cost_rows = []
    for (sy, ey, avg, v100) in infl_txt:
        cost_rows.append(f'<div class="row"><span>What cost $100 in {sy}</span><b>${v100:.2f} in {ey}</b></div>')
    mw_rows = []
    for s, en in p["terms"]:
        en2 = en or TODAY.isoformat()
        m0, m1 = minwage(s), minwage(en2)
        if m0: mw_rows.append(f'<div class="row"><span>Federal minimum wage, {s[:4]} → {en2[:4]}</span><b>${m0:.2f} → ${m1:.2f}</b></div>')
    dnote = p["debt"].get("note", "")
    first = p["terms"][0][0]
    fy_txt = ("Budget years run October to September, so a new president's first budget year starts the fall after they take office." if first >= "1977"
              else "Until 1842 the federal budget year matched the calendar year and debt figures are dated January 1; from 1843 to 1976 budget years ran July to June." if first < "1843"
              else "Budget years ran July to June until 1976 (now October to September), so each year's figures cover parts of two calendar years.")
    t.append(f"""  <section id="economy" class="block">
    <h2>The economy, first day to last</h2>
    <p class="lede">Shaded areas show the years in office, with a few years before and after for comparison. {fy_txt}</p>
    <div class="grid2">
      <div class="card"><h3>National debt</h3><p class="cap">{e(parts[0][2])}: {money(parts[0][0])} → {e(parts[0][3])}: {money(parts[0][1])}{"" if len(parts) == 1 else f" · {e(parts[1][2])}: {money(parts[1][0])} → {e(parts[1][3])}: {money(parts[1][1])}"}</p><div class="chart" id="ch-debt"></div>{f'<p class="note">{e(dnote)}</p>' if dnote else ""}</div>
      <div class="card"><h3>Debt compared with the economy</h3><p class="cap">Debt as a share of GDP. Above 100% means the debt is bigger than a year of everything the country produces.</p><div class="chart" id="ch-ratio"></div></div>
      <div class="card"><h3>Deficits and surpluses</h3><p class="cap">Money borrowed each budget year (below the line) or paid down (above).{" The White House budget office's yearly figures begin in 1901." if y0 < 1901 else ""}</p><div class="chart" id="ch-deficit"></div>{'<div class="legend"><span><i class="sw" style="background:var(--def)"></i>Deficit</span><span><i class="sw" style="background:var(--debt)"></i>Surplus</span></div>' if any("bal" in r for r in econ) else ""}</div>
      <div class="card"><h3>Unemployment</h3><p class="cap">{e(u_sub)}. {e(u_cap)}</p><div class="chart" id="ch-unemp"></div></div>
      <div class="card"><h3>Inflation</h3><p class="cap">How much prices rose each year (consumer price index).</p><div class="chart" id="ch-infl"></div></div>
      <div class="card"><h3>Cost of living</h3><p class="cap">What everyday prices and paychecks did while in office.</p>
        <div class="cost">{"".join(cost_rows)}{"".join(mw_rows)}</div>
        <p class="note">Prices use the consumer price index (MeasuringWorth). The minimum wage is the federal rate set by Congress.</p></div>
    </div>
  </section>
""")
    # --- executive orders
    eo_chart = ('<div class="chart" id="ch-eo"></div>' if eo_years else
                '<p class="note" style="font-size:13px">Yearly counts aren\'t reliable for this era. Orders were not numbered until 1907, when the State Department numbered the ones already in its files, and many orders were never numbered at all, so only the total is shown.</p>')
    eo_items = "".join(f"""<details class="item"><summary><span class="t">{e(o["t"])}</span><span class="pill kind">{"EO " + e(o["n"]) if o["n"] else "Order"}</span><span class="m">{fmt_date(o["date"])}</span></summary><div class="body"><p style="margin:0">{e(o["d"])}</p><a href="https://www.federalregister.gov/presidential-documents/executive-orders" target="_blank" rel="noopener">Federal Register</a></div></details>""" for o in p["eo_notable"])
    t.append(f"""  <section id="orders" class="block">
    <h2>Executive orders</h2>
    <p class="lede">{eo_total:,} orders{f', numbered {e(p["eo_range"])}' if p.get("eo_range") else ""}. {e(p.get("eo_note", ""))}</p>
    <div class="grid2">
      <div class="card"><h3>Orders signed each year</h3>{eo_chart}<p class="note">Source: <a href="{e(p["eo_source"][1])}" target="_blank" rel="noopener">{e(p["eo_source"][0])}</a> (full list of every order).</p></div>
      <div><h3 style="font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-2);margin:0 0 8px">Notable orders</h3><div class="list">{eo_items or '<p class="note" style="margin:0">Most orders in this era were routine, such as setting aside public land or exempting jobs from civil service rules.</p>'}</div></div>
    </div>
  </section>
""")
    # --- pardons
    def pardon_item(x):
        d = x["date"]; dd = fmt_date(d) if len(d) == 10 else d
        return f"""<details class="item"><summary><span class="t">{e(x["name"])}</span><span class="pill kind">{e(x["kind"])}</span><span class="m">{e(dd)}</span></summary><div class="body"><p style="margin:0"><b>The crime:</b> {e(x["crime"])}</p><p style="margin:0"><b>Sentence:</b> {e(x["sentence"])}</p><p style="margin:0"><b>Why it drew attention:</b> {e(x["why"])}</p><a href="{e(x["src"])}" target="_blank" rel="noopener">Source</a></div></details>"""
    clem_chart = ('<div class="chart" id="ch-clem"></div><div class="legend"><span><i class="sw" style="background:var(--accent)"></i>Pardons</span><span><i class="sw" style="background:var(--int)"></i>Commutations</span></div>' if p["clem_by_year"] else
                  '<p class="note" style="font-size:13px">The Justice Department\'s published clemency counts begin in fiscal 1900, so there are no reliable yearly totals for this presidency.</p>')
    group_html = "".join(f'<div class="row"><span>{e(n)}</span><b>{c:,}</b></div>' for n, c in groups)
    t.append(f"""  <section id="pardons" class="block">
    <h2>Pardons and commutations</h2>
    <p class="lede">A pardon wipes out the punishment for a federal crime; a commutation shortens a sentence but leaves the conviction. {e(p["clem_note"])}</p>
    <div class="grid2">
      <div class="card"><h3>Granted each year</h3>{clem_chart}
        {f'<div class="cost" style="margin-top:10px"><div class="row" style="border:0;padding:0"><span style="color:var(--muted);font-size:12px">Group proclamations (not in the chart)</span></div>{group_html}</div>' if groups else ""}
        <p class="note">Source: <a href="{e(p["clem_source"][1])}" target="_blank" rel="noopener">{e(p["clem_source"][0])}</a>, which lists every recipient with the crime and sentence.</p></div>
      <div><h3 style="font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-2);margin:0 0 8px">Notable grants: tap to see the crime</h3><div class="list">{"".join(pardon_item(x) for x in p["pardons"]) or '<p class="note" style="margin:0">No individual grants from this presidency are highlighted yet.</p>'}</div></div>
    </div>
  </section>
""")
    # --- legal record
    rows = "".join(f"""<details class="item"><summary><span class="k">{e(x["k"])}</span><span class="v">{e(x["v"])}</span><span class="pill {x["status"]}">{STATUS[x["status"]]}</span></summary><div class="body"><p style="margin:0">{e(x["d"])}</p>{f'<a href="{e(x["src"])}" target="_blank" rel="noopener">Source</a>' if x.get("src") else ""}</div></details>""" for x in p["legal"])
    people = "".join(f"""<div class="person"><div class="n">{e(x["name"])}</div><div class="r">{e(x["role"])}</div><div><span class="pill {"proven" if any(w in x["outcome"] for w in ("Convicted", "guilty", "contest")) else "no"}">{e(x["outcome"])}</span></div><div class="d">{e(x["d"])}</div></div>""" for x in p["people"])
    t.append(f"""  <section id="legal" class="block">
    <h2>Investigations and legal record</h2>
    <p class="lede">The same checklist for every president. Tap a row for details and sources.</p>
    <div class="check">{rows}</div>
    <h3 style="font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-2);margin:22px 0 0">People around the president who were charged or penalized</h3>
    <div class="people">{people or '<p class="note" style="margin:6px 0 0">No one in the administration was charged or formally penalized.</p>'}</div>
  </section>
""")
    # --- controversies
    cons = "".join(f"""<details class="item"><summary><span class="t">{e(x["title"])}</span><span class="pill {x["label"]}">{LABEL[x["label"]]}</span><span class="m">{e(x["when"])}</span></summary><div class="body"><p style="margin:0">{e(x["d"])}</p><p style="margin:0"><b>Outcome:</b> {e(x["outcome"])}</p><a href="{e(x["src"])}" target="_blank" rel="noopener">Source</a></div></details>""" for x in p["controversies"])
    t.append(f"""  <section id="controversies" class="block">
    <h2>Controversies and scandals</h2>
    <p class="lede">What happened, what was proven, and how it ended.</p>
    <div class="labels-key"><span><span class="pill proven">Proven</span> convicted, admitted or confirmed by a court or official investigation</span><span><span class="pill charged">Charged</span> indicted or impeached (outcome stated)</span><span><span class="pill disputed">Disputed</span> facts established, whether it was wrong is debated</span><span><span class="pill alleged">Alleged</span> reported but never established</span></div>
    <div class="list">{cons}</div>
  </section>
""")
    quotes = "".join(f"""<blockquote><p>{e(x["q"])}</p><footer>{e(x["when"])} · {e(x["ctx"])} <a href="{e(x["src"])}" target="_blank" rel="noopener">Source</a></footer></blockquote>""" for x in p["quotes"])
    t.append(f"""  <section id="quotes" class="block">
    <h2>In their own words</h2>
    <p class="lede">Widely quoted remarks, with the context they were said in.</p>
    <div class="quotes">{quotes or '<p class="note">No widely quoted remarks with a reliable source are included yet.</p>'}</div>
  </section>
  <section class="block" style="padding-bottom:0">
    <div class="method"><b>How this page is made.</b> Every president gets the same sections and the same checklist. A controversy is listed if it led to an investigation by Congress, an inspector general, a special or independent counsel or a court, or was a sustained national story covered across the political spectrum. Labels follow the strongest official finding, not media coverage. Debt figures come from the U.S. Treasury; deficits and GDP from the White House budget office and the Commerce Department; unemployment from the Bureau of Labor Statistics (before 1948, yearly estimates by Stanley Lebergott via NBER and the Census Bureau's Historical Statistics); prices from MeasuringWorth; executive orders from the Federal Register and National Archives; clemency from the Justice Department.</div>
  </section>
""")
    t.append(FOOT)
    page_data = dict(terms=[[round(a, 3), round(b, 3)] for a, b in tf], econ=econ, eo={str(k): v for k, v in eo_years.items()}, clem={str(k): v for k, v in p["clem_by_year"].items()})
    t.append(f'<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>\n<script>window.PAGE={json.dumps(page_data, separators=(",", ":"))};</script>\n<script src="../assets/president.js"></script>\n</body>\n</html>\n')
    return "".join(t)

def index():
    t = [head("Presidents · Yeas and Nays", "Every U.S. president, with deep dives into the economy, executive orders, pardons, legal records and controversies.", "")]
    t.append("""  <nav class="crumbs">Presidents</nav>
  <section class="hero" style="grid-template-columns:1fr;padding-bottom:6px">
    <div><div class="eyebrow">The presidents</div><h1>Every president, held to the same standard</h1>
    <p class="sum">Pick a president to see what happened to the debt, jobs and prices on their watch, every executive order and pardon, their legal record, and the controversies, each one labeled by what was actually proven.</p></div>
  </section>
""")
    num = 0; cards = []; done_slug = set(); done_names = set()
    for name, party, s, en in ALL_PRES:
        num += 1
        slug = slug_for(name)
        var = side(party)
        yrs = f'{s[:4]}–{en[:4] if en else "present"}'
        if (slug and slug in done_slug) or name in done_names:
            continue  # one card per person (Cleveland and Trump served twice)
        done_names.add(name)
        if slug:
            done_slug.add(slug)
            p = PRESIDENTS[slug]
            yrs = " & ".join(f'{a[:4]}–{b[:4] if b else "present"}' for a, b in p["terms"])
            cards.append(f'<a class="pcard live" href="presidents/{slug}.html"><div class="pic">{portrait(slug, name, placeholder=False, up="")}<span class="num">#{p["number"].replace("th","").replace("nd","").replace("rd","").replace(" & ","/").replace("st","")}</span><span class="bar" style="background:{var}"></span></div><div class="info"><b>{e(name)}</b><span>{e(yrs)} · {e(party.split(" /")[0])}</span><em>Deep dive →</em></div></a>')
        else:
            cards.append(f'<div class="pcard soon" aria-disabled="true"><div class="pic">{portrait(PORTRAIT_SLUG.get(name, "none"), name, placeholder=False, up="")}<span class="num">#{num}</span><span class="bar" style="background:{var}"></span></div><div class="info"><b>{e(name)}</b><span>{e(yrs)} · {e(party.split(" /")[0].split(" (")[0])}</span><span>Coming soon</span></div></div>')
    n_live = sum('class="pcard live"' in c for c in cards)
    t.append(f"""  <div class="ptools"><p>{"Every president has a deep dive." if n_live == len(cards) else f"{n_live} of {len(cards)} presidents have a deep dive so far."} Colored bars show party: Democrats blue, Republicans red, and earlier parties (Federalists gold, Democratic-Republicans teal, Whigs orange) their own colors. Gray means no party or a break with it.</p>
    <div class="ptbtns">{"" if n_live == len(cards) else '<button type="button" class="pbtn" id="pf" aria-pressed="false">Deep dives only</button>'}<button type="button" class="pbtn" id="ps">Oldest first</button></div></div>
  <div class="pgrid" id="pg">
""")
    t.append("\n".join("    " + c for c in reversed(cards)))
    t.append("""\n  </div>
<script>(function(){var g=document.getElementById("pg"),f=document.getElementById("pf"),s=document.getElementById("ps");
if(f)f.onclick=function(){var on=f.getAttribute("aria-pressed")!=="true";f.setAttribute("aria-pressed",on);g.classList.toggle("only",on);};
s.onclick=function(){s.textContent=s.textContent==="Oldest first"?"Newest first":"Oldest first";Array.prototype.slice.call(g.children).reverse().forEach(function(c){g.appendChild(c);});};})();</script>
""")
    t.append(FOOT)
    t.append("</body>\n</html>\n")
    return "".join(t)

os.makedirs(os.path.join(ROOT, "presidents"), exist_ok=True)
for slug, p in PRESIDENTS.items():
    open(os.path.join(ROOT, "presidents", f"{slug}.html"), "w").write(page(slug, p))
open(os.path.join(ROOT, "presidents.html"), "w").write(index())
old = os.path.join(ROOT, "presidents", "index.html")
if os.path.exists(old): os.remove(old)
print("built", ", ".join(PRESIDENTS), "+ index")
