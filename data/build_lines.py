"""Builds The Lines: lines.html (gerrymandering: how district lines are drawn, the history and court cases, and every state's maps).
Run from the project root after data/build_lines_data.py:  python3 data/build_lines.py
"""
import os, sys, html
sys.path.insert(0, os.path.dirname(__file__))
from build_presidents import head, FOOT
import seo

ROOT = os.path.join(os.path.dirname(__file__), "..")
e = lambda s: html.escape(str(s), quote=True)

# History and court cases. Sources: Library of Congress and Smithsonian (the 1812 cartoon); U.S. Code and the House Historian (federal
# districting laws); Oyez and supremecourt.gov (rulings); National Constitution Center (Louisiana v. Callais); Wikipedia's summary of
# 2025-26 redistricting (map changes for 2026).
HISTORY = [
    ("1812", "The word is born", "Massachusetts Governor Elbridge Gerry signs a state senate map that twists one district around Boston's northern suburbs. A Boston Gazette cartoon draws it as a salamander, the \"Gerry-mander.\" The tactic was older than the name.", None),
    ("1842", "One district, one member", "Congress requires states to elect House members from single-member districts of contiguous territory instead of statewide, so the lines start to matter everywhere.", None),
    ("1872–1911", "Equal and compact", "Later apportionment laws add rules: districts should hold as nearly equal populations as practicable (1872) and be compact (1901, renewed in 1911).", None),
    ("1929", "The rules lapse", "The Reapportionment Act fixes the House at 435 seats but drops the size and shape rules; the Supreme Court confirms they expired (Wood v. Broom, 1932). Many states stop redrawing at all, and rural districts end up with far fewer people than city ones.", None),
    ("1962–64", "One person, one vote", "Baker v. Carr lets federal courts hear districting cases. Wesberry v. Sanders (1964) requires congressional districts of nearly equal population, and Reynolds v. Sims does the same for state legislatures. States must redraw after every census.", "baker"),
    ("1965 & 1982", "The Voting Rights Act", "The Act bans voting rules that discriminate by race; the 1982 amendments let maps be challenged for diluting minority votes even without proof of intent. Thornburg v. Gingles (1986) sets the test, leading to majority-minority districts.", None),
    ("1986", "Partisan gerrymanders: maybe", "Davis v. Bandemer says partisan gerrymandering claims can be heard in court, but no majority agrees on a test. No map is ever struck down under it.", None),
    ("1993", "Race can't be the main reason", "Shaw v. Reno: North Carolina's snaking 12th District, drawn to give Black voters a second majority district, can be challenged as a racial gerrymander. Some of the least compact districts ever drawn date from this decade.", None),
    ("2004–06", "No test, and mid-decade redraws allowed", "Vieth v. Jubelirer (2004) finds no workable standard for partisan gerrymanders. LULAC v. Perry (2006) lets Texas redraw in the middle of a decade, though one district violated the Voting Rights Act.", None),
    ("2010–12", "The data era", "Detailed voter data and mapping software let map-drawers predict outcomes precisely. After the 2010 census, Republicans, having won many state legislatures, draw most maps; Democrats do the same where they control them.", None),
    ("2013", "Preclearance ends", "Shelby County v. Holder frees states with a history of discrimination from needing federal approval before changing maps.", "shelby"),
    ("2015–18", "Commissions and state courts", "Arizona State Legislature v. AIRC (2015) lets voters hand map-drawing to independent commissions. In 2018 Pennsylvania's Supreme Court throws out the state's map under the state constitution, and Michigan and Colorado voters create commissions.", None),
    ("2019", "Federal courts step out", "Rucho v. Common Cause (5–4): partisan gerrymandering is a political question federal courts can't decide. Challenges move to state courts and state constitutions.", None),
    ("2023–24", "The Voting Rights Act, again", "Allen v. Milligan (2023) orders Alabama to draw a second district where Black voters can elect their choice. Moore v. Harper (2023) keeps state courts able to review maps. Alexander v. South Carolina NAACP (2024) gives legislatures a presumption of good faith.", None),
    ("2025–26", "The mid-decade map war", "Texas redraws in mid-decade to add Republican seats; California voters answer with Proposition 50. After Louisiana v. Callais (April 2026, 6–3) narrows race-conscious districts under the Voting Rights Act, more states redraw. Alabama, California, Florida, Louisiana, North Carolina, Ohio, Tennessee, Texas and Utah vote under new maps in 2026.", None),
]

DESC = ("How congressional district lines are drawn and redrawn: the history of gerrymandering from 1812 to the 2026 map war, the court cases, "
        "and every state's House districts since 1789, with how compact they are and, since 1976, how votes compared with seats.")
t = [head("The Lines: gerrymandering and every House district since 1789 | Yeas and Nays", DESC, "", current="lines", path="/lines", image="/assets/og/hill.jpg",
          jsonld=[{"@context": "https://schema.org", "@type": "CollectionPage", "name": "The Lines: gerrymandering", "url": seo.url("/lines"), "description": DESC},
                  seo.breadcrumbs(("Yeas and Nays", "/"), ("The Lines", "/lines"))])]
hist = "".join(f'''<li><span class="hy">{e(y)}</span><div><b>{e(ti)}</b><p>{e(tx)}{f' <a href="bench.html#r-{b}">On The Bench →</a>' if b else ""}</p></div></li>''' for y, ti, tx, b in HISTORY)
t.append(f"""  <nav class="crumbs">The Lines</nav>
  <section class="hero" style="grid-template-columns:1fr;padding-bottom:6px">
    <div><div class="eyebrow">Redistricting</div><h1>The Lines</h1>
    <p class="sum">Every ten years, and lately more often, someone redraws the map of House districts. Where the lines go can decide who wins before anyone votes. Here's how it works, how it got this way, and every state's maps since 1789.</p></div>
  </section>
  <nav class="jump" aria-label="Jump to section"><a href="#how">How it works</a><a href="#state">Explore a state</a><a href="#shapes">Shapes over time</a><a href="#history">History</a><a href="#caveats">What the numbers can't tell you</a><a href="#method">How this works</a></nav>

  <section id="how" class="block" style="border-top:0">
    <h2>Same voters, different maps</h2>
    <p class="lede">Fifty voters: 30 blue, 20 red. They need five districts of ten. Tap a map to redraw the lines.</p>
    <div class="card gm"><div class="vseg" id="gmSeg" role="group" aria-label="District map"><button type="button" data-m="fair" aria-pressed="true">Proportional</button><button type="button" data-m="blue" aria-pressed="false">Blue sweeps</button><button type="button" data-m="red" aria-pressed="false">Red wins</button></div>
      <div class="gmwrap"><svg id="gmGrid" viewBox="0 0 420 220" role="img" aria-label="Fifty voters in five districts"></svg><div class="gmres" id="gmRes"></div></div>
      <p class="note" id="gmNote"></p></div>
    <p class="lede"><b>Packing</b> crowds the other side's voters into a few districts they win by huge margins. <b>Cracking</b> spreads the rest thin so they fall short everywhere else. Do both and a minority of the votes can win a majority of the seats.</p>
  </section>

  <section id="state" class="block">
    <h2>Explore a state</h2>
    <p class="lede">Pick a state and move through its maps. Each district is colored by the party of the member seated when that Congress began; hover or tap one for its member and how compact it is.</p>
    <div class="lpick"><label for="stSel">State</label><select id="stSel"></select>
      <div class="yearpick"><input type="range" id="stRange" min="1" max="120" value="119" aria-label="Congress"><output id="stOut"></output></div></div>
    <div class="lgrid">
      <div class="card"><h3 id="stMapH"></h3><p class="cap" id="stMapCap"></p><svg id="stMap" viewBox="0 0 600 420" role="img" aria-label="Districts of the selected state"></svg><div class="legend" id="stLeg"></div></div>
      <div class="lside">
        <div class="cfacts" id="stFacts"></div>
        <div class="card"><h3>How compact its districts are</h3><p class="cap">Median district shape score each Congress, this state vs. the whole country. Lower means stretched, twisting districts.</p><div class="chart" id="stPP"></div><div class="legend" id="stPPLeg"></div></div>
        <div class="card"><h3>Votes vs. seats</h3><p class="cap" id="stVCap">The Democratic share of the state's two-party House vote, and of the seats it won.</p><div class="chart" id="stVotes"></div><div class="legend" id="stVLeg"></div></div>
      </div>
    </div>
    <p class="note" id="stNote"></p>
  </section>

  <section id="shapes" class="block">
    <h2>Shapes over time</h2>
    <p class="lede">The median shape score of every House district, each Congress. Districts were drawn from whole counties for most of history; the sharp drop in the 1990s came with computer mapping and with districts drawn around race, and scores have recovered somewhat as courts and commissions pushed back.</p>
    <div class="card"><div class="chart" id="natPP"></div><p class="note">Polsby-Popper score: a circle is 1; most districts fall between 0.2 and 0.5. Statewide (at-large) seats aren't counted, since nobody draws their lines.</p></div>
    <h3 class="sub3">The least compact districts in the current Congress</h3>
    <div class="list" id="worst"></div>
  </section>

  <section id="history" class="block">
    <h2>A short history of the gerrymander</h2>
    <ol class="ltime">{hist}</ol>
  </section>

  <section id="caveats" class="block">
    <h2>What the numbers can't tell you</h2>
    <div class="method">
      <p><b>Odd shapes aren't proof.</b> Coastlines, rivers, county lines and the Voting Rights Act's requirements all bend districts. A compact map can still be gerrymandered; a sprawling one can be fair.</p>
      <p><b>Votes vs. seats isn't proof either.</b> Democratic voters cluster in cities, so even neutral lines tend to give them fewer seats than their vote share. A few points of gap is normal under any single-member system; the winning party usually gets a seat bonus.</p>
      <p><b>Uncontested races skew vote totals.</b> When one party doesn't run, that district's votes all go one way, and some states don't count votes in uncontested races at all. Those districts are left out of the efficiency gap here.</p>
      <p><b>What it does show:</b> when a state's seats stay lopsided across elections in which the votes swing back and forth, or when its maps change sharply right after one party takes control of redistricting, the lines are doing work.</p>
    </div>
  </section>

  <section id="method" class="block">
    <div class="method"><b>How this works.</b>
      <p><b>District boundaries</b>: Jeffrey B. Lewis, Brandon DeVine, Lincoln Pitcher and Kenneth C. Martis, <i>Digital Boundary Definitions of United States Congressional Districts, 1789–2012</i> (UCLA), kept current through the 119th Congress, simplified for the web. Members and parties: Voteview (UCLA). The 120th Congress uses the 2026 results; the nine states with new 2026 maps aren't in the boundary data yet.</p>
      <p><b>Compactness</b> is the Polsby-Popper score, 4π × area ÷ perimeter², measured on each district's shape on the globe. Boundaries are simplified to about 1 km, which smooths coastlines; scores compare well with each other but run a little higher than ones from full-detail maps.</p>
      <p><b>Votes</b>: MIT Election Data and Science Lab, <i>U.S. House 1976–2024</i> (Harvard Dataverse, CC0). Vote share is the Democratic share of Democratic plus Republican votes. The <b>efficiency gap</b> counts each party's "wasted" votes (every vote for a loser, and a winner's votes beyond the half needed) and divides the difference by all votes cast; shown only for states with at least two districts, leaving out uncontested races.</p>
      <p><b>History</b>: Library of Congress and Smithsonian (the 1812 cartoon); the House Historian and U.S. Code (districting laws); Oyez and supremecourt.gov (rulings); the National Constitution Center on <i>Louisiana v. Callais</i>.</p>
    </div>
  </section>
""")
t.append(FOOT)
t.append('<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>\n<script src="https://cdnjs.cloudflare.com/ajax/libs/topojson/3.0.2/topojson.min.js"></script>\n'
         '<script src="assets/borders.js"></script>\n<script src="assets/lines-data.js"></script>\n<script src="assets/lines.js"></script>\n</body>\n</html>\n')
open(os.path.join(ROOT, "lines.html"), "w").write("".join(t))
print("built lines.html")
