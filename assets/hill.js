/* The Hill: renders Congress data from window.HILL. */
(function(){
  const H = window.HILL; if (!H) return;
  const $ = s => document.querySelector(s);
  const esc = s => String(s == null ? "" : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"})[c]);
  const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  const C = H.congresses, byN = Object.fromEntries(C.map(c => [c.n, c]));
  const COLOR = {D:"var(--dem)", R:"var(--rep)", F:"#c9a227", DR:"#2f9e8f", NR:"#d4803a", W:"#e0a33a", O:"var(--mix)", U:"var(--line)"};
  const FAMNAME = {D:"Democrats", R:"Republicans", F:"Federalists", DR:"Democratic-Republicans", NR:"Adams / anti-Jackson", W:"Whigs", O:"Other parties"};
  const ORDER = ["DR","D","O","U","W","NR","F","R"];
  const col = k => { const c = COLOR[k] || COLOR.O; return c.startsWith("var(") ? css(c.slice(4, -1)) : c; };
  const ord = n => n + (n % 100 >= 11 && n % 100 <= 13 ? "th" : ({1:"st",2:"nd",3:"rd"})[n % 10] || "th");
  const yrs = c => `${c.start.slice(0,4)}–${c.end.slice(0,4)}`;
  const fmt = iso => new Date(iso + "T12:00:00Z").toLocaleDateString("en-US", {month:"long", day:"numeric", year:"numeric", timeZone:"UTC"});
  const tip = document.createElement("div"); tip.className = "tooltip"; document.body.appendChild(tip);
  const showTip = (ev, h) => { tip.innerHTML = h; tip.classList.add("on"); tip.style.left = Math.min(ev.clientX + 14, innerWidth - 270) + "px"; tip.style.top = (ev.clientY + 14) + "px"; };
  const hideTip = () => tip.classList.remove("on");
  const sorted = parties => parties.slice().sort((a, b) => ORDER.indexOf(a.g) - ORDER.indexOf(b.g));
  const total = ps => ps.reduce((s, p) => s + p.n, 0);
  const presLink = p => H.pslug[p.name] ? `<a href="presidents/${H.pslug[p.name]}.html">${esc(p.name)}</a>` : esc(p.name);
  const ctlName = (fam, label) => fam === "shared" ? "Shared (50–50)" : label;
  const SEATED = C.filter(c => !c.elect), NOW = SEATED[SEATED.length - 1], ELECT = C.find(c => c.elect);
  // A members-elect Congress: seats not yet called are drawn as open (gray) seats
  const withUncalled = (c, key) => { const u = c.elect && (c.elect[key + "_uncalled"] || []).length; return u ? c[key].concat([{p: "Not yet called", g: "U", n: u}]) : c[key]; };

  /* ---------- hemicycle seat chart ---------- */
  function hemi(el, parties){
    const ps = sorted(parties).filter(p => p.n > 0), N = total(ps); if (!N){ el.innerHTML = ""; return; }
    const W = 360, R = 170, rows = N > 300 ? 12 : N > 150 ? 9 : N > 80 ? 7 : N > 40 ? 5 : 4, r0 = R * (N > 150 ? .38 : .42);
    const radii = d3.range(rows).map(i => r0 + (R - r0) * i / Math.max(1, rows - 1)), sum = d3.sum(radii);
    let counts = radii.map(r => Math.round(N * r / sum)); let diff = N - d3.sum(counts); counts[rows - 1] += diff;
    const pts = []; radii.forEach((r, i) => { const n = counts[i]; for (let k = 0; k < n; k++){ const a = Math.PI * (n === 1 ? .5 : k / (n - 1)); pts.push({a, r}); } });
    pts.sort((p, q) => p.a - q.a || p.r - q.r); // left-leaning parties on the left, as in most seat charts
    const dotR = Math.min(7, (R - r0) / rows * .42, Math.PI * r0 / (counts[0] || 1) * .42);
    let i = 0; ps.forEach(p => { for (let k = 0; k < p.n; k++) if (pts[i]) pts[i++].p = p; });
    const svg = d3.select(el).html("").append("svg").attr("viewBox", `0 0 ${W} ${R + 16}`).attr("role", "img").attr("aria-label", ps.map(p => `${p.p} ${p.n}`).join(", "));
    svg.selectAll("circle").data(pts).join("circle").attr("cx", d => W / 2 - d.r * Math.cos(d.a)).attr("cy", d => R + 6 - d.r * Math.sin(d.a)).attr("r", dotR)
      .attr("fill", d => col(d.p ? d.p.g : "O")).attr("stroke", d => d.p && d.p.g === "U" ? css("--muted") : null).attr("stroke-dasharray", d => d.p && d.p.g === "U" ? "1.5 1.5" : null).on("mousemove", (ev, d) => d.p && showTip(ev, `<b>${esc(d.p.p)}</b>: ${d.p.n} seat${d.p.n === 1 ? "" : "s"}`)).on("mouseleave", hideTip);
    svg.append("text").attr("x", W / 2).attr("y", R + 2).attr("text-anchor", "middle").attr("class", "hemi-n").text(N);
  }
  const legend = ps => sorted(ps).filter(p => p.n > 0).map(p => `<span><i class="sw" style="background:${COLOR[p.g] || COLOR.O}${p.g === "U" ? ";outline:1px dashed var(--muted)" : ""}"></i>${esc(p.p)} ${p.n}</span>`).join("");

  /* ---------- one Congress ---------- */
  function lawItem(l){
    const c = byN[l.congress];
    const vote = l.vote ? `<p style="margin:0"><b>Vote:</b> House ${esc(l.vote.house)} · Senate ${esc(l.vote.senate)}</p>` : "";
    return `<details class="item"><summary><span class="t">${esc(l.title)}</span><span class="pill" style="color:var(${({lib:"--dem",con:"--rep",mix:"--mix"})[l.bucket] || "--mix"})">${({lib:"Liberal-leaning",con:"Conservative-leaning",mix:"Mixed"})[l.bucket] || ""}</span>
      <span class="m">${fmt(l.date)} · ${c ? ord(c.n) + " Congress" : ""}${l.president ? " · " + esc(l.president) : ""}</span></summary>
      <div class="body"><p style="margin:0">${esc(l.summary || "")}</p>${l.impact ? `<p style="margin:0"><b>Why it matters:</b> ${esc(l.impact)}</p>` : ""}${vote}
      ${c ? `<p style="margin:0"><b>Congress:</b> House ${esc(c.house_label)}, Senate ${esc(c.senate_label)}${l.how && l.how !== "Signed" ? " · " + esc(l.how) : ""}</p>` : ""}</div></details>`;
  }
  function showCongress(n){
    const c = byN[n]; $("#cRange").value = n; $("#cOut").textContent = ord(n); V.n = n;
    if (V.view === "map" && window.HILLMAP) drawMap(n);
    const E = c.elect;
    $("#cTitle").textContent = E ? `The ${ord(n)} Congress (members-elect)` : `The ${ord(n)} Congress`;
    $("#cSub").textContent = E ? `Elected ${fmt(String(+c.start.slice(0,4) - 1) + "-11-03")}; takes office ${fmt(c.start)}. Results as of ${fmt(E.as_of)}; races not yet called are shown as open seats.`
      : n === NOW.n ? `${fmt(c.start)} to today${ELECT ? `, in its lame-duck session until the ${ord(ELECT.n)} Congress is sworn in on ${fmt(c.end)}` : ""}` : `${fmt(c.start)} to ${fmt(c.end)}`;
    const hP = withUncalled(c, "house"), sP = withUncalled(c, "senate");
    hemi($("#hemiH"), hP); hemi($("#hemiS"), sP);
    $("#legH").innerHTML = legend(hP); $("#legS").innerHTML = legend(sP) + (c.senate_vacant ? `<span>Vacant ${c.senate_vacant}</span>` : "");
    $("#cElect") && $("#cElect").setAttribute("aria-pressed", String(!!E)); $("#cNow").setAttribute("aria-pressed", String(n === NOW.n));
    const P = c.pending;
    const gov = E && c.gov === "divided" ? "<b>Divided</b>: from January 2027 Democrats will hold the House and Senate and a Republican the White House" : c.gov === "unified" ? `<b style="color:${COLOR[c.gov_fam]}">Unified</b>: ${FAMNAME[c.gov_fam]} held the White House, House and Senate` : c.gov === "divided" ? "<b>Divided</b>: power was split between the parties" : "The president had no party";
    $("#cFacts").innerHTML = `<div><span>House majority${E ? " (won)" : ""}</span><b>${esc(ctlName(c.house_ctl, c.house_label))}</b></div><div><span>Senate majority${E ? " (won)" : ""}</span><b>${esc(ctlName(c.senate_ctl, c.senate_label))}</b></div>
      <div><span>Speaker of the House</span><b>${P ? esc(P.speaker) : c.speakers.map(s => esc(s.name)).join(", then ") || "—"}</b></div>
      <div><span>Senate majority leader</span><b>${P ? esc(P.senate) : c.leaders.map(s => esc(s.name)).join(", then ") || "No formal post yet"}</b></div>
      <div><span>President</span><b>${c.presidents.map(presLink).join(", then ")}</b></div><div><span>Government</span><b>${gov}</b></div>`
      + (c.note ? `<p class="note" style="grid-column:1/-1;margin:0">${esc(c.note)}</p>` : "")
      + (P && P.others ? `<p class="note" style="grid-column:1/-1;margin:0">${esc(P.others)}</p>` : "")
      + (E ? electDetail(c) : "");
    const ls = H.laws.filter(l => l.congress === n);
    $("#cLaws").innerHTML = ls.length ? `<h3 class="sub3">Landmark laws from this Congress</h3><div class="list">${ls.map(lawItem).join("")}</div>` : "";
  }
  $("#cRange").addEventListener("input", e => showCongress(+e.target.value));

  /* ---------- seat charts / map toggle ---------- */
  const V = {view: "seats", ch: "S", n: null};
  try { const s = JSON.parse(localStorage.getItem("hillView") || "{}"); if (s.view === "map") V.view = "map"; if (s.ch === "H") V.ch = "H"; } catch (e) {}
  const saveV = () => { try { localStorage.setItem("hillView", JSON.stringify({view: V.view, ch: V.ch})); } catch (e) {} };
  let mapLoad = null;
  const loadScript = src => new Promise((ok, no) => { const s = document.createElement("script"); s.src = src; s.onload = ok; s.onerror = () => no(new Error(src)); document.head.appendChild(s); });
  const loadMap = () => mapLoad || (mapLoad = Promise.all([
    window.topojson ? 0 : loadScript("https://cdnjs.cloudflare.com/ajax/libs/topojson/3.0.2/topojson.min.js"),
    window.BORDERS ? 0 : loadScript("assets/borders.js"), window.HILLMAP ? 0 : loadScript("assets/hill-map.js")]));
  function setView(){
    document.querySelectorAll(".viewbar [data-v]").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.v === V.view)));
    document.querySelectorAll("#chSeg [data-c]").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.c === V.ch)));
    const map = V.view === "map"; $("#chSeg").hidden = !map; $("#mapCard").hidden = !map; $("#seatCharts").hidden = map;
    if (map){ $("#mapCap").textContent = "Loading the map…"; loadMap().then(() => drawMap(V.n)).catch(() => { $("#mapCap").textContent = "The map couldn't load. Check your connection and try again."; mapLoad = null; }); }
  }
  document.querySelector(".viewbar").addEventListener("click", e => { const b = e.target.closest("button"); if (!b) return;
    if (b.dataset.v) V.view = b.dataset.v; if (b.dataset.c) V.ch = b.dataset.c; saveV(); setView(); });

  /* ---------- the map ---------- */
  const proj = () => d3.geoAlbersUsa().scale(1300).translate([487.5, 305]);
  let GEO = null;
  const isoN = s => s.slice(0,4) + "-" + s.slice(4,6) + "-" + s.slice(6,8);
  function geo(){
    if (GEO) return GEO; const path = d3.geoPath(proj());
    GEO = topojson.feature(BORDERS, BORDERS.objects.states).features.map(f => { const p = f.properties;
      return {ab: p.id === "dc" ? "DC" : p.id.slice(0,2).toUpperCase(), name: p.n, state: p.ty === "State", sd: isoN(p.s), ed: p.e === "20001231" ? "9999-12-31" : isoN(p.e),
        d: path(f) || "", c: path(f) ? path.centroid(f) : [0, 0], area: path(f) ? path.area(f) : 0}; }).filter(g => g.d);
    return GEO;
  }
  // Small eastern states get their label off the coast, with a leader line
  const CALL = {VT: [0, 0], NH: [0, 1], MA: [0, 2], RI: [0, 3], CT: [0, 4], NJ: [0, 5], DE: [0, 6], MD: [0, 7]};
  const STNAME = {}; // filled from the borders data
  let CTY = null; // county borders (interior lines only), loaded the first time the House map needs them
  const loadCounties = () => CTY || (CTY = Promise.resolve().then(() => fetch("assets/counties-albers-10m.json")).then(r => r.json())
    .then(us => { const gp = d3.geoPath();
      return {mesh: gp(topojson.mesh(us, us.objects.counties, (a, b) => a !== b && (a.id / 1000 | 0) === (b.id / 1000 | 0))),
        feats: topojson.feature(us, us.objects.counties).features.map(f => ({id: f.id, name: f.properties.name, d: gp(f)}))}; }));
  const mcol = k => k === "U" ? css("--ink-2") : k === "V" ? css("--surface-2") : col(k); // uncalled seats: light gray, so they read against the dark page
  function stripes(defs, parts){ // parts: [[family, count]] -> fill
    const rank = k => k === "U" ? 2.5 : k === "V" ? 99 : ORDER.indexOf(k); // same left-to-right order as the seat charts
    const live = parts.filter(p => p[1] > 0).sort((a, b) => rank(a[0]) - rank(b[0])); if (!live.length) return "url(#p-none)";
    if (live.length === 1) return mcol(live[0][0]);
    const id = "p-" + live.map(p => p[0] + p[1]).join("-").replace(/[^\w-]/g, "");
    if (!defs.select("#" + id).size()){
      const T = live.reduce((s, p) => s + p[1], 0), W = live.length === 2 && live[0][1] === live[1][1] ? 12 : 16;
      const pat = defs.append("pattern").attr("id", id).attr("width", W).attr("height", 10).attr("patternUnits", "userSpaceOnUse").attr("patternTransform", "rotate(45)");
      let x = 0; live.forEach(p => { const w = W * p[1] / T; pat.append("rect").attr("x", x).attr("y", 0).attr("width", w + .2).attr("height", 10).attr("fill", mcol(p[0])); x += w; });
    }
    return `url(#${id})`;
  }
  function drawMap(n){
    if (!window.HILLMAP || !window.BORDERS || !window.topojson) return;
    const c = byN[n], M = HILLMAP.congresses[n] || {S: {}, H: {}}, S = V.ch === "S", data = S ? M.S : M.H;
    const date = c.start, G = geo().filter(g => g.sd <= date && date <= g.ed);
    G.forEach(g => { if (g.state) STNAME[g.ab] = g.name; });
    const svg = d3.select("#cMap").html(""), defs = svg.append("defs");
    defs.append("pattern").attr("id", "p-none").attr("width", 6).attr("height", 6).attr("patternUnits", "userSpaceOnUse").attr("patternTransform", "rotate(45)")
      .html(`<rect width="6" height="6" fill="${css("--surface-2")}"/><line x1="0" y1="0" x2="0" y2="6" stroke="${css("--line")}" stroke-width="2"/>`);
    const fam = ab => { const v = data[ab]; if (!v) return [];
      return S ? Object.entries(v.reduce((o, m) => (o[m[2]] = (o[m[2]] || 0) + 1, o), {})).concat(v.length === 1 ? [["none", 1]] : []) : v.map(p => [p[1], p[2]]); };
    const fillFor = ab => { const f = fam(ab); if (S && f.some(x => x[0] === "none")) return stripes(defs, f.filter(x => x[0] !== "none").concat([["V", 1]])); return stripes(defs, f); };
    const tipFor = (g) => { const v = data[g.ab];
      if (g.ab === "DC" && /District of Columbia/.test(g.name)) return `<b>${esc(g.name)}</b><br>Not a state: ${S ? "no senators" : "a delegate who can't vote on the floor"}`;
      if (!g.state) return `<b>${esc(g.name)}</b><br>Not yet a state; ${S ? "no senators" : "a delegate without a vote, if any"}`;
      if (!v || !v.length) return `<b>${esc(g.name)}</b><br>${S ? "No senators seated" : "No representatives seated"} when the Congress began`;
      if (S) return `<b>${esc(g.name)}</b><br>` + v.map(m => `<span style="color:${col(m[2])}">■</span> ${esc(m[0])} (${esc(m[1])})${m[3] ? ` · ${esc(m[3])}` : ""}`).join("<br>");
      const T = v.reduce((s, p) => s + p[2], 0);
      return `<b>${esc(g.name)}</b>: ${T} seat${T === 1 ? "" : "s"}<br>` + v.map(p => `<span style="color:${col(p[1])}">■</span> ${esc(p[0])}: ${p[2]}`).join("<br>"); };
    svg.append("g").selectAll("path").data(G).join("path").attr("d", g => g.d)
      .attr("class", g => g.state ? "stp" : "terr").attr("fill", g => g.state ? fillFor(g.ab) : null)
      .on("mousemove", (ev, g) => showTip(ev, tipFor(g))).on("mouseleave", hideTip)
      .on("click", (ev, g) => showTip(ev, tipFor(g)));
    // County lines (today's counties, U.S. Census via us-atlas), drawn from 1959 on, when today's 50 states were in place
    const COUNTY_FROM = "1959-01-03", showCty = !S && c.start >= COUNTY_FROM;
    if (showCty){ const fg = svg.append("g").attr("class", "ctyfill"), cg = svg.append("g").attr("class", "cty"), og = svg.append("g").attr("class", "stout");
      loadCounties().then(K => { if (!cg.node().isConnected) return;
        if (M.C){ // color each county by the party of the House member(s) whose districts cover it, striped by share of its land
          fg.selectAll("path").data(K.feats.filter(f => M.C[f.id])).join("path").attr("d", f => f.d)
            .attr("fill", f => { const v = M.C[f.id]; return typeof v === "string" ? mcol(v) : stripes(defs, v.map(([k, s]) => [k, Math.max(1, Math.round(s * 10))])); }); }
        cg.append("path").attr("d", K.mesh);
        og.selectAll("path").data(G.filter(g => g.state)).join("path").attr("d", g => g.d); }).catch(() => {}); }
    if (!S){ // seat counts on each state
      const lg = svg.append("g"), states = G.filter(g => g.state && data[g.ab]);
      states.forEach(g => { const T = data[g.ab].reduce((s, p) => s + p[2], 0), k = CALL[g.ab];
        if (k && c.start >= "1790"){ const y = 150 + k[1] * 24, x = 905;
          lg.append("line").attr("class", "lead").attr("x1", g.c[0]).attr("y1", g.c[1]).attr("x2", x - 4).attr("y2", y);
          lg.append("text").attr("class", "ml mlx").attr("x", x).attr("y", y).text(`${g.ab} ${T}`); }
        else if (g.area > 300) lg.append("text").attr("class", "ml").attr("x", g.c[0]).attr("y", g.c[1]).text(T); });
    }
    // caption, legend, every-state list, notes
    const tot = {}; Object.values(data).forEach(v => S ? v.forEach(m => { const k = m[1]; tot[k] = tot[k] || {f: m[2], n: 0}; tot[k].n++; }) : v.forEach(p => { tot[p[0]] = tot[p[0]] || {f: p[1], n: 0}; tot[p[0]].n += p[2]; }));
    const order = Object.entries(tot).sort((a, b) => ORDER.indexOf(a[1].f) - ORDER.indexOf(b[1].f));
    const split = S ? Object.values(data).filter(v => v.length === 2 && v[0][2] !== v[1][2]).length : Object.values(data).filter(v => v.length > 1).length;
    $("#mapH").textContent = S ? "Senate by state" : "House by state";
    $("#mapCap").textContent = (S ? "Each state's two senators" : "Each state's House delegation, with its number of seats") + (c.elect ? ` as elected in ${+c.start.slice(0,4) - 1} (results as of ${fmt(HILLMAP.as_of_120)})` : " when the Congress began")
      + `. ${split} state${split === 1 ? "" : "s"} ${S ? "split between parties" : "with members from more than one party"}, shown striped.`;
    $("#mapLeg").innerHTML = order.map(([p, o]) => `<span><i class="sw" style="background:${col(o.f)}"></i>${esc(p)} ${o.n}</span>`).join("")
      + `<span><i class="sw" style="background:repeating-linear-gradient(45deg,${col("D")} 0 3px,${col("R")} 3px 6px)"></i>Split (striped)</span>`
      + (G.some(g => !g.state && !/District of Columbia/.test(g.name)) ? `<span><i class="sw" style="background:var(--ghost);outline:1px solid var(--line)"></i>Territory, not yet a state</span>` : "");
    const rows = Object.keys(data).filter(ab => STNAME[ab] || CALL[ab] !== undefined).sort((a, b) => (STNAME[a] || a).localeCompare(STNAME[b] || b));
    $("#mapTable").innerHTML = `<div class="stgrid">` + rows.map(ab => { const v = data[ab];
      if (S) return `<div><span class="ab">${ab}</span><span class="bar">${v.map(m => `<i style="flex:1;background:${col(m[2])}"></i>`).join("")}</span><span class="ct">${v.map(m => m[2] === "O" ? "I" : m[2]).join(" · ")}</span><span class="nm">${v.map(m => esc(m[0]) + (m[3] && /won/.test(m[3]) ? " (new term)" : "")).join(", ")}</span></div>`;
      const T = v.reduce((s, p) => s + p[2], 0);
      return `<div><span class="ab">${ab}</span><span class="bar">${v.map(p => `<i style="flex:${p[2]};background:${col(p[1])}"></i>`).join("")}</span><span class="ct">${T}: ${v.map(p => `${p[1] === "U" ? "?" : p[1] === "O" ? "Oth" : p[1]} ${p[2]}`).join(", ")}</span></div>`; }).join("") + `</div>`;
    $("#mapNote").innerHTML = c.elect
      ? `Not certified; states still counting are striped gray for the races not yet called. Sources: ${HILLMAP.sources_120.map(([t, u]) => `<a href="${esc(u)}" target="_blank" rel="noopener">${esc(t)}</a>`).join(" · ")}`
      : `Members seated when the Congress began (Voteview); borders as of ${fmt(c.start)}.`;
    if (!S) $("#mapNote").innerHTML += M.C ? ` Counties are colored by the party of the House member whose district covers them; a county split between districts of different parties is striped by how much of its land each covers (district–county overlaps from the U.S. Census Bureau's 119th Congress relationship file). Counts on each state are its seats.${M.newmaps ? ` ${M.newmaps.join(", ")} drew new districts for 2026 that the Census Bureau hasn't matched to counties yet, so they're colored by state.` : ""}`
      : c.start >= "1959-01-03" ? " Thin lines are county borders (today's counties, U.S. Census Bureau); seats are counted by state, since district lines for this Congress aren't matched to counties here."
      : " County lines are shown from 1959 on, when today's 50 states were in place; earlier county borders were different.";
  }
  $("#cNow").addEventListener("click", () => showCongress(NOW.n));
  $("#cElect") && $("#cElect").addEventListener("click", () => showCongress(ELECT.n));

  /* ---------- members-elect: uncalled races and sources ---------- */
  function electDetail(c){
    const E = c.elect, rows = [["House", E.house_uncalled || []], ["Senate", E.senate_uncalled || []]];
    const list = rows.map(([ch, rs]) => `<p style="margin:0"><b>${ch}: ${rs.length ? `${rs.length} race${rs.length === 1 ? "" : "s"} not yet called` : "every race called"}</b></p>`
      + (rs.length ? `<ul class="uncalled">${rs.map(r => `<li><b>${esc(r.race)}</b>: ${esc(r.status)}</li>`).join("")}</ul>` : "")).join("");
    const src = (E.sources || []).map(([t, u]) => `<a href="${esc(u)}" rel="noopener" target="_blank">${esc(t)}</a>`).join(" · ");
    return `<div class="elect-detail" style="grid-column:1/-1"><h3 class="sub3" style="margin-top:0">Still being counted (as of ${fmt(E.as_of)})</h3>${list}
      <p class="note" style="margin:6px 0 0">Seat counts are races called by news organizations (including the Associated Press) as reported on this date; they are not certified results and will change as the last races are decided. Sources: ${src}</p></div>`;
  }
  if (ELECT){
    const b = $("#electBanner"), tot = ps => ps.reduce((s, p) => s + p.n, 0), fam = (ps, g) => ps.filter(p => p.g === g).reduce((s, p) => s + p.n, 0);
    const hu = (ELECT.elect.house_uncalled || []).length, su = (ELECT.elect.senate_uncalled || []).length;
    const sD = fam(ELECT.senate, "D") + fam(ELECT.senate, "O"), sR = fam(ELECT.senate, "R");
    b.innerHTML = `<b>${+ELECT.start.slice(0,4) - 1} midterms:</b> Democrats won the House (${fam(ELECT.house, "D")}–${fam(ELECT.house, "R")}${hu ? `, ${hu} not yet called` : ""}) and the Senate (${sD}–${sR}${su ? `, ${su} not yet called` : ""}, counting independents who caucus with them). The ${ord(ELECT.n)} Congress takes office ${fmt(ELECT.start)}; until then the ${ord(NOW.n)} keeps serving. <button type="button" class="pbtn" id="bElect">See the ${ord(ELECT.n)}</button>`;
    b.hidden = false; $("#bElect").addEventListener("click", () => showCongress(ELECT.n));
  }

  /* ---------- seats over time ---------- */
  function balance(el, key){
    const W = Math.max(300, el.clientWidth || 600), Hh = 150, M = {l: 34, r: 6, t: 8, b: 20};
    const svg = d3.select(el).html("").append("svg").attr("viewBox", `0 0 ${W} ${Hh}`).attr("role", "img").attr("aria-label", `${key} seats by party, each Congress`);
    const x = d3.scaleBand().domain(C.map(c => c.n)).range([M.l, W - M.r]).paddingInner(.1), y = d3.scaleLinear().domain([0, 100]).range([Hh - M.b, M.t]);
    C.forEach(c => { const ps = sorted(c[key]), T = total(ps); let acc = 0;
      ps.forEach(p => { const v = p.n / T * 100; svg.append("rect").attr("x", x(c.n)).attr("width", x.bandwidth()).attr("y", y(acc + v)).attr("height", y(acc) - y(acc + v)).attr("fill", col(p.g)); acc += v; }); });
    svg.append("line").attr("x1", M.l).attr("x2", W - M.r).attr("y1", y(50)).attr("y2", y(50)).attr("stroke", css("--ink")).attr("stroke-dasharray", "4 3").attr("opacity", .6);
    [0, 50, 100].forEach(t => svg.append("text").attr("x", M.l - 5).attr("y", y(t) + 3.5).attr("text-anchor", "end").text(t + "%"));
    C.filter(c => +c.start.slice(0,4) % (W < 600 ? 50 : 25) === 1 || c.n === 1).forEach(c => svg.append("text").attr("x", x(c.n) + x.bandwidth() / 2).attr("y", Hh - 5).attr("text-anchor", "middle").text(c.start.slice(0,4)));
    svg.append("rect").attr("x", M.l).attr("y", M.t).attr("width", W - M.l - M.r).attr("height", Hh - M.t - M.b).attr("fill", "transparent").style("cursor", "pointer")
      .on("mousemove", ev => { const [mx] = d3.pointer(ev); const c = C[Math.max(0, Math.min(C.length - 1, Math.floor((mx - M.l) / x.step())))];
        showTip(ev, `<b>${ord(c.n)} Congress · ${yrs(c)}</b><br>` + sorted(c[key]).filter(p => p.n).map(p => `<span style="color:${col(p.g)}">■</span> ${esc(p.p)}: ${p.n}`).join("<br>")); })
      .on("mouseleave", hideTip)
      .on("click", ev => { const [mx] = d3.pointer(ev); const c = C[Math.max(0, Math.min(C.length - 1, Math.floor((mx - M.l) / x.step())))]; showCongress(c.n); $("#congress").scrollIntoView({behavior: "smooth"}); });
  }
  $("#legBal").innerHTML = ORDER.map(k => `<span><i class="sw" style="background:${COLOR[k]}"></i>${FAMNAME[k]}</span>`).join("");

  /* ---------- size ---------- */
  function size(){
    const el = $("#chSize"), W = Math.max(300, el.clientWidth || 600), Hh = 170, M = {l: 34, r: 8, t: 10, b: 20};
    const svg = d3.select(el).html("").append("svg").attr("viewBox", `0 0 ${W} ${Hh}`).attr("role", "img").attr("aria-label", "Members of the House and Senate, each Congress");
    const pts = C.map(c => ({y: +c.start.slice(0,4), h: total(withUncalled(c, "house")), s: total(withUncalled(c, "senate")) + (c.senate_vacant || 0), c}));
    const x = d3.scaleLinear().domain([1789, +C[C.length - 1].start.slice(0,4)]).range([M.l, W - M.r]), y = d3.scaleLinear().domain([0, 460]).range([Hh - M.b, M.t]);
    [0, 100, 200, 300, 435].forEach(t => { svg.append("line").attr("x1", M.l).attr("x2", W - M.r).attr("y1", y(t)).attr("y2", y(t)).attr("stroke", css("--line")).attr("stroke-dasharray", t === 435 ? "4 3" : null);
      svg.append("text").attr("x", M.l - 5).attr("y", y(t) + 3.5).attr("text-anchor", "end").text(t); });
    [["h", "--accent"], ["s", "--int"]].forEach(([k, v]) => svg.append("path").attr("d", d3.line().x(d => x(d.y)).y(d => y(d[k])).curve(d3.curveStepAfter)(pts)).attr("fill", "none").attr("stroke", css(v)).attr("stroke-width", 2));
    d3.range(1800, 2026, W < 600 ? 50 : 25).forEach(yr => svg.append("text").attr("x", x(yr)).attr("y", Hh - 5).attr("text-anchor", "middle").text(yr));
    svg.append("rect").attr("x", M.l).attr("y", M.t).attr("width", W - M.l - M.r).attr("height", Hh - M.t - M.b).attr("fill", "transparent")
      .on("mousemove", ev => { const [mx] = d3.pointer(ev); const yr = x.invert(mx); const d = pts.filter(p => p.y <= yr).pop() || pts[0];
        showTip(ev, `<b>${ord(d.c.n)} Congress · ${yrs(d.c)}</b><br>House: ${d.h}<br>Senate: ${d.s}`); }).on("mouseleave", hideTip);
  }

  /* ---------- unified vs divided ---------- */
  function gov(){
    $("#govBand").innerHTML = C.map(c => `<i data-n="${c.n}" class="${c.gov}" style="${c.gov === "unified" ? `background:${COLOR[c.gov_fam]}` : ""}" title="${ord(c.n)} Congress (${yrs(c)}): ${c.gov === "unified" ? "unified, " + FAMNAME[c.gov_fam] : c.gov === "divided" ? "divided government" : "president with no party"}"></i>`).join("");
    const fams = [...new Set(C.filter(c => c.gov === "unified").map(c => c.gov_fam))];
    $("#legGov").innerHTML = ORDER.filter(k => fams.includes(k)).map(k => `<span><i class="sw" style="background:${COLOR[k]}"></i>Unified: ${FAMNAME[k]}</span>`).join("") + `<span><i class="sw divided"></i>Divided</span><span><i class="sw" style="background:var(--line)"></i>President with no party</span>`;
    const since = y => { const cs = C.filter(c => +c.start.slice(0,4) >= y); const u = cs.filter(c => c.gov === "unified").length; return [u, cs.length]; };
    const [a, b] = since(1789), [a2, b2] = since(1969);
    $("#govSum").innerHTML = `One party held the White House, House and Senate at the start of <b>${a} of ${b}</b> Congresses since 1789, but only <b>${a2} of ${b2}</b> since 1969.`;
  }
  $("#govBand").addEventListener("click", e => { const i = e.target.closest("[data-n]"); if (!i) return; showCongress(+i.dataset.n); $("#congress").scrollIntoView({behavior: "smooth"}); });

  /* ---------- polarization ---------- */
  function polar(){
    const el = $("#chPol");
    if (!H.pol){ el.innerHTML = `<p class="note" style="font-size:13px">The polarization data is being added.</p>`; $("#polNote").textContent = ""; return; }
    const W = Math.max(300, el.clientWidth || 600), Hh = 200, M = {l: 34, r: 8, t: 10, b: 20};
    const svg = d3.select(el).html("").append("svg").attr("viewBox", `0 0 ${W} ${Hh}`).attr("role", "img").attr("aria-label", "Median DW-NOMINATE score of each party, each Congress");
    const series = [];
    ["house", "senate"].forEach(ch => ["D", "R"].forEach(p => series.push({ch, p, pts: Object.entries(H.pol[ch]).filter(([, v]) => v[p] != null).map(([n, v]) => ({n: +n, y: +byN[+n].start.slice(0,4), v: v[p]}))})));
    const x = d3.scaleLinear().domain([1855, 2025]).range([M.l, W - M.r]), y = d3.scaleLinear().domain([-.6, .75]).range([Hh - M.b, M.t]);
    [-.5, 0, .5].forEach(t => { svg.append("line").attr("x1", M.l).attr("x2", W - M.r).attr("y1", y(t)).attr("y2", y(t)).attr("stroke", t === 0 ? css("--muted") : css("--line"));
      svg.append("text").attr("x", M.l - 5).attr("y", y(t) + 3.5).attr("text-anchor", "end").text(t > 0 ? "+" + t : t); });
    svg.append("text").attr("x", M.l + 4).attr("y", M.t + 9).attr("class", "st").text("More conservative ↑");
    svg.append("text").attr("x", M.l + 4).attr("y", Hh - M.b - 4).attr("class", "st").text("More liberal ↓");
    series.forEach(s => svg.append("path").attr("d", d3.line().x(d => x(d.y)).y(d => y(d.v))(s.pts.filter(d => d.y >= 1855))).attr("fill", "none")
      .attr("stroke", css(s.p === "D" ? "--dem" : "--rep")).attr("stroke-width", s.ch === "house" ? 2.2 : 1.6).attr("stroke-dasharray", s.ch === "senate" ? "5 3" : null));
    d3.range(1860, 2026, W < 600 ? 40 : 20).forEach(yr => svg.append("text").attr("x", x(yr)).attr("y", Hh - 5).attr("text-anchor", "middle").text(yr));
    svg.append("rect").attr("x", M.l).attr("y", M.t).attr("width", W - M.l - M.r).attr("height", Hh - M.t - M.b).attr("fill", "transparent")
      .on("mousemove", ev => { const [mx] = d3.pointer(ev); const yr = x.invert(mx); const c = C.filter(c => +c.start.slice(0,4) <= yr).pop(); const hv = H.pol.house[c.n] || {}, sv = H.pol.senate[c.n] || {};
        const f = v => v == null ? "—" : (v > 0 ? "+" : "") + v.toFixed(2);
        showTip(ev, `<b>${ord(c.n)} Congress · ${yrs(c)}</b><br>House: Democrats ${f(hv.D)}, Republicans ${f(hv.R)}${hv.D != null && hv.R != null ? ` (gap ${(hv.R - hv.D).toFixed(2)})` : ""}<br>Senate: Democrats ${f(sv.D)}, Republicans ${f(sv.R)}`); })
      .on("mouseleave", hideTip);
    $("#legPol").innerHTML = `<span><i class="sw" style="background:var(--dem)"></i>Democrats</span><span><i class="sw" style="background:var(--rep)"></i>Republicans</span><span>Solid: House · Dashed: Senate</span>`;
    const last = C[C.length - 1].n, gap = n => H.pol.house[n] && H.pol.house[n].R - H.pol.house[n].D;
    const low = Object.keys(H.pol.house).map(Number).filter(n => n >= 60 && gap(n) != null).reduce((a, b) => gap(b) < gap(a) ? b : a);
    $("#polNote").innerHTML = `In the House, the gap between the parties' median members was <b>${gap(low).toFixed(2)}</b> at its narrowest (the ${ord(low)} Congress, ${yrs(byN[low])}) and is <b>${gap(last) != null ? gap(last).toFixed(2) : "—"}</b> in the ${ord(last)} Congress. Source: Voteview (UCLA), DW-NOMINATE first dimension.`;
  }

  /* ---------- laws ---------- */
  const CATS = {tax:"Taxes & tariffs", spend:"Spending & programs", budget:"Budget rules & debt limit", money:"Money & banking", wage:"Wages", war:"War", crisis:"Crises & rescues"};
  const LF = {bucket: new Set(["lib","con","mix"]), who: new Set(["D","R","both"]), cat: new Set(Object.keys(CATS))};
  const lineage = n => { if (!n) return null; if (/^(Democratic|Anti-Administration|Jacksonian|Jackson & Crawford)/.test(n)) return "D"; if (/^(Republican|Federalist|Pro-Administration|Whig|Adams|Anti-Jackson|Opposition|National Republican|Unaffiliated \(Federalist)/.test(n)) return "R"; return null; };
  function passedBy(l){ if (l.type === "amendment" || /override/i.test(l.how || "") || l.pattern === "Bipartisan") return "both";
    const c = byN[l.congress]; const h = lineage(c && c.house_label), s = lineage(c && c.senate_label); if (h && h === s) return h;
    const pr = c && c.presidents.find(p => p.name === l.president) || (c && c.presidents[0]); return lineage(pr && pr.party) || h || s || "both"; }
  H.laws.forEach(l => l._who = passedBy(l));
  function toggle(set, k, all){ if (set.size === all.length){ set.clear(); set.add(k); return; } set.has(k) ? set.delete(k) : set.add(k); if (!set.size) all.forEach(x => set.add(x)); }
  function chipRow(label, items, isOn, cls){ return `<div class="frow"><span class="flab">${label}</span>${items.map(([k, l, c]) => `<button type="button" class="fchip ${cls}" data-k="${k}" aria-pressed="${isOn(k)}">${c ? `<i style="background:${c}"></i>` : ""}${esc(l)}</button>`).join("")}</div>`; }
  function renderLF(){
    const n = (k, v) => H.laws.filter(l => l[k] === v).length;
    $("#lFilters").innerHTML = chipRow("What it did", [["lib", `Liberal-leaning ${n("bucket","lib")}`, "var(--dem)"], ["con", `Conservative-leaning ${n("bucket","con")}`, "var(--rep)"], ["mix", `Mixed ${n("bucket","mix")}`, "var(--mix)"]], k => LF.bucket.has(k), "lb")
      + chipRow("Passed by", [["D", `Democratic side ${n("_who","D")}`, "var(--dem)"], ["R", `Republican side ${n("_who","R")}`, "var(--rep)"], ["both", `Both parties ${n("_who","both")}`, "var(--mix)"]], k => LF.who.has(k), "lw")
      + chipRow("Topic", Object.entries(CATS), k => LF.cat.has(k), "lc");
  }
  function renderLaws(){
    const list = H.laws.filter(l => LF.bucket.has(l.bucket) && LF.who.has(l._who) && LF.cat.has(l.cat)).slice().reverse();
    const shown = LF.all ? list : list.slice(0, 15);
    $("#lList").innerHTML = (shown.map(lawItem).join("") || `<p class="note">No laws match these filters.</p>`)
      + (list.length > shown.length ? `<button type="button" class="pbtn more" id="lMore">Show all ${list.length} laws</button>` : "");
  }
  $("#lFilters").addEventListener("click", e => { const b = e.target.closest(".fchip"); if (!b) return; const k = b.dataset.k;
    if (b.classList.contains("lb")) toggle(LF.bucket, k, ["lib","con","mix"]); else if (b.classList.contains("lw")) toggle(LF.who, k, ["D","R","both"]); else toggle(LF.cat, k, Object.keys(CATS));
    renderLF(); renderLaws(); });
  $("#lList").addEventListener("click", e => { if (e.target.id === "lMore"){ LF.all = true; renderLaws(); } });

  /* ---------- every Congress ---------- */
  function renderEvery(){
    const EV = C.slice().reverse(), cut = renderEvery.all ? EV.length : 20;
    $("#eList").innerHTML = EV.slice(0, cut).map(c => { const ls = H.laws.filter(l => l.congress === c.n);
      const top = ps => sorted(ps).filter(p => p.n).map(p => `<span class="seg" style="flex:${p.n};background:${COLOR[p.g] || COLOR.O}" title="${esc(p.p)} ${p.n}"></span>`).join("");
      return `<details class="item cong" id="c-${c.n}"><summary><span class="t">${ord(c.n)} Congress <span class="yrs">${yrs(c)}${c.elect ? " · members-elect" : ""}</span></span>
        <span class="pill ${c.gov}" ${c.gov === "unified" ? `style="color:${COLOR[c.gov_fam]};border-color:${COLOR[c.gov_fam]}"` : ""}>${c.gov === "unified" ? "Unified" : c.gov === "divided" ? "Divided" : "No-party president"}</span>
        <span class="m"><span class="mini"><b>House</b><span class="bar">${top(c.house)}</span></span><span class="mini"><b>Senate</b><span class="bar">${top(c.senate)}</span></span></span></summary>
        <div class="body"><p style="margin:0"><b>House:</b> ${sorted(withUncalled(c, "house")).filter(p => p.n).map(p => `${esc(p.p)} ${p.n}`).join(", ")}</p>
          <p style="margin:0"><b>Senate:</b> ${sorted(c.senate).filter(p => p.n).map(p => `${esc(p.p)} ${p.n}`).join(", ")}${c.senate_vacant ? `, vacant ${c.senate_vacant}` : ""}</p>
          <p style="margin:0"><b>Speaker:</b> ${c.pending ? esc(c.pending.speaker) : c.speakers.map(s => esc(s.name)).join(", then ") || "—"}${c.leaders.length ? ` · <b>Senate majority leader:</b> ${c.leaders.map(s => esc(s.name)).join(", then ")}` : ""}</p>
          <p style="margin:0"><b>President:</b> ${c.presidents.map(presLink).join(", then ")}</p>${c.note ? `<p class="meta">${esc(c.note)}</p>` : ""}
          ${ls.length ? `<p style="margin:0"><b>Landmark laws:</b> ${ls.map(l => esc(l.title)).join("; ")}</p>` : ""}
          <a href="#congress" data-show="${c.n}">See the seat charts →</a></div></details>`; }).join("")
      + (cut < EV.length ? `<button type="button" class="pbtn more" id="eMore">Show all ${EV.length} Congresses</button>` : "");
  }
  $("#eList").addEventListener("click", e => { if (e.target.id === "eMore"){ renderEvery.all = true; renderEvery(); return; } const a = e.target.closest("[data-show]"); if (!a) return; e.preventDefault(); showCongress(+a.dataset.show); $("#congress").scrollIntoView({behavior: "smooth"}); });

  function drawAll(){ balance($("#chBalH"), "house"); balance($("#chBalS"), "senate"); size(); polar(); }
  showCongress(NOW.n); setView(); gov(); renderLF(); renderLaws(); renderEvery(); drawAll();
  let rt; addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(drawAll, 150); });
  if (location.hash.startsWith("#c-")){ const n = +location.hash.slice(3); if (byN[n]){ showCongress(n); renderEvery.all = true; renderEvery(); const d = document.getElementById("c-" + n); if (d){ d.open = true; } } }
})();
