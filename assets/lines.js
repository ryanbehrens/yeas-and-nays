/* The Lines: gerrymandering explainer, state district explorer and charts. Data: window.LINES (assets/lines-data.js), assets/districts/NNN.json, window.BORDERS. */
(function(){
  const L = window.LINES; if (!L) return;
  const $ = s => document.querySelector(s);
  const esc = s => String(s == null ? "" : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"})[c]);
  const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  const COLOR = {D:"--dem", R:"--rep", F:"#c9a227", DR:"#2f9e8f", NR:"#d4803a", W:"#e0a33a", O:"--mix", U:"--ink-2"};
  const col = k => { const c = COLOR[k] || COLOR.O; return c.startsWith("--") ? css(c) : c; };
  const ord = n => n + (n % 100 >= 11 && n % 100 <= 13 ? "th" : ({1:"st",2:"nd",3:"rd"})[n % 10] || "th");
  const startYear = n => n <= 73 ? 1789 + 2 * (n - 1) : 1935 + 2 * (n - 74);
  const pct = x => x == null ? "—" : Math.round(x * 100) + "%";
  const tip = document.createElement("div"); tip.className = "tooltip"; document.body.appendChild(tip);
  const showTip = (ev, h) => { tip.innerHTML = h; tip.classList.add("on"); tip.style.left = Math.min(ev.clientX + 14, innerWidth - 270) + "px"; tip.style.top = (ev.clientY + 14) + "px"; };
  const hideTip = () => tip.classList.remove("on");

  /* ---------- packing and cracking demo: 10 x 5 voters, columns 0-5 blue, 6-9 red ---------- */
  const W = 10, H = 5, voter = (x) => x < 6 ? "D" : "R";
  const MAPS = {
    fair: (x, y) => Math.floor(x / 2),                           // five 2-column districts: 3 blue, 2 red
    blue: (x, y) => y,                                            // five rows, each 6 blue to 4 red: blue sweeps
    red: (x, y) => x < 2 ? 0 : x < 4 ? 1 : x === 9 ? 4 : y < 2 ? 2 : y < 4 ? 3 : 4,  // pack blue into two, crack the rest
  };
  const NOTES = {
    fair: "Districts follow where people live: blue wins 3 of 5 seats with 60% of the votes.",
    blue: "Every district gets a 6–4 blue majority: 60% of the votes wins every seat.",
    red: "Blue voters are packed into two districts they win 10–0 and cracked across the other three: red wins 3 of 5 seats with 40% of the votes.",
  };
  function drawGM(m){
    document.querySelectorAll("#gmSeg button").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.m === m)));
    const f = MAPS[m], S = 40, ox = 10, oy = 10, svg = d3.select("#gmGrid").html("");
    const dist = {}; for (let x = 0; x < W; x++) for (let y = 0; y < H; y++){ const d = f(x, y); (dist[d] = dist[d] || []).push(voter(x)); }
    const win = Object.fromEntries(Object.entries(dist).map(([d, v]) => [d, v.filter(c => c === "D").length > v.length / 2 ? "D" : "R"]));
    for (let x = 0; x < W; x++) for (let y = 0; y < H; y++){
      svg.append("rect").attr("x", ox + x * S).attr("y", oy + y * S).attr("width", S).attr("height", S).attr("fill", col(win[f(x, y)])).attr("opacity", .18);
      svg.append("circle").attr("cx", ox + x * S + S / 2).attr("cy", oy + y * S + S / 2).attr("r", 11).attr("fill", col(voter(x)));
    }
    const edge = (x1, y1, x2, y2) => svg.append("line").attr("x1", x1).attr("y1", y1).attr("x2", x2).attr("y2", y2).attr("class", "gmline");
    for (let x = 0; x <= W; x++) for (let y = 0; y < H; y++) if (x === 0 || x === W || f(x - 1, y) !== f(x, y)) edge(ox + x * S, oy + y * S, ox + x * S, oy + (y + 1) * S);
    for (let y = 0; y <= H; y++) for (let x = 0; x < W; x++) if (y === 0 || y === H || f(x, y - 1) !== f(x, y)) edge(ox + x * S, oy + y * S, ox + (x + 1) * S, oy + y * S);
    const wins = Object.values(win), b = wins.filter(w => w === "D").length;
    $("#gmRes").innerHTML = `<div><b style="color:${col("D")}">${b}</b><span>Blue seats</span></div><div><b style="color:${col("R")}">${5 - b}</b><span>Red seats</span></div><p>Votes: 60% blue, 40% red</p>`;
    $("#gmNote").textContent = NOTES[m];
  }
  $("#gmSeg").addEventListener("click", e => { const b = e.target.closest("[data-m]"); if (b) drawGM(b.dataset.m); });
  drawGM("fair");

  /* ---------- district files ---------- */
  const DIST = {};
  const loadDistricts = n => DIST[n] || (DIST[n] = Promise.resolve().then(() => fetch(`assets/districts/${String(n).padStart(3, "0")}.json`))
    .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }).then(tp => topojson.feature(tp, tp.objects.d).features));
  let BOR = null;
  const isoN = s => s.slice(0,4) + "-" + s.slice(4,6) + "-" + s.slice(6,8);
  const borders = () => BOR || (BOR = window.BORDERS ? topojson.feature(BORDERS, BORDERS.objects.states).features.filter(f => f.properties.ty === "State")
    .map(f => ({f, ab: f.properties.id.slice(0,2).toUpperCase(), sd: isoN(f.properties.s), ed: f.properties.e === "20001231" ? "9999" : isoN(f.properties.e)})) : []);
  const stateShape = (ab, n) => { const d = (startYear(n) + "-03-04"); return borders().filter(b => b.ab === ab && b.sd <= d && d <= b.ed).map(b => b.f); };

  /* ---------- explore a state ---------- */
  const ST = Object.entries(L.states).sort((a, b) => a[1].name.localeCompare(b[1].name));
  $("#stSel").innerHTML = ST.map(([ab, s]) => `<option value="${ab}">${esc(s.name)}</option>`).join("");
  const S = {st: "NC", n: 119};
  try { const h = new URLSearchParams(location.hash.slice(1)); if (L.states[h.get("state")]) S.st = h.get("state"); if (+h.get("congress")) S.n = +h.get("congress"); } catch (e) {}
  const congs = st => Object.keys(L.congress[st] || {}).map(Number).sort((a, b) => a - b);
  function setState(st, n){
    const cs = congs(st); S.st = st; S.n = cs.includes(n) ? n : cs.includes(119) ? 119 : cs[cs.length - 1];
    $("#stSel").value = st; const r = $("#stRange"); r.min = cs[0]; r.max = cs[cs.length - 1]; r.value = S.n;
    try { history.replaceState(null, "", `#state=${st}&congress=${S.n}`); } catch (e) {}
    drawState(); drawStatePP(); drawVotes();
  }
  $("#stSel").addEventListener("change", e => setState(e.target.value, S.n));
  $("#stRange").addEventListener("input", e => { const cs = congs(S.st), v = +e.target.value; S.n = cs.reduce((a, b) => Math.abs(b - v) < Math.abs(a - v) ? b : a); drawState(); drawStatePP(); });

  function drawState(){
    const st = S.st, n = S.n, info = L.congress[st][n] || {}, name = L.states[st].name, elect = n === 120;
    $("#stOut").textContent = `${ord(n)} · ${startYear(n)}`;
    $("#stMapH").textContent = `${name}, ${ord(n)} Congress (${startYear(n)}–${startYear(n) + 2})`;
    const svg = d3.select("#stMap").html(""), w = 600, h = 420;
    svg.append("defs").html(`<pattern id="lh" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="6" height="6" fill="${css("--surface-2")}"/><line x1="0" y1="0" x2="0" y2="6" stroke="${css("--line")}" stroke-width="2"/></pattern>`);
    $("#stMapCap").textContent = "Loading…";
    loadDistricts(n).then(F => {
      if (S.st !== st || S.n !== n) return;
      const fs = F.filter(f => f.properties.s === st), outline = stateShape(st, n), show = fs.length ? fs : outline;
      if (!show.length){ $("#stMapCap").textContent = "No map for this state in this Congress."; return; }
      const fc = {type: "FeatureCollection", features: show};
      const lon = d3.geoCentroid(fc)[0], proj = d3.geoTransverseMercator().rotate([-lon, 0]).fitExtent([[10, 10], [w - 10, h - 10]], fc), path = d3.geoPath(proj);
      if (!fs.length || fs.some(f => f.properties.x)) svg.append("g").selectAll("path").data(outline).join("path").attr("d", path).attr("fill", "url(#lh)").attr("class", "lst");
      const fam = f => { const ms = f.properties.m || []; if (!ms.length || f.properties.x) return "url(#lh)";
        const k = Object.entries(ms.reduce((o, m) => (o[m[2]] = (o[m[2]] || 0) + 1, o), {})).sort((a, b) => b[1] - a[1]); return k.length > 1 && k[0][1] === k[1][1] ? col("O") : col(k[0][0]); };
      const dtip = f => { const p = f.properties;
        if (p.x) return `<b>${esc(name)}</b><br>District lines for this Congress aren't in the boundary data.`;
        return `<b>${p.d ? ord(p.d) + " district" : (p.m && p.m.length > 1 ? "Elected statewide" : "At-large")}</b><br>` + (p.m || []).map(m => `<span style="color:${col(m[2])}">■</span> ${m[0] ? esc(m[0]) + " (" + esc(m[1]) + ")" : esc(m[1])}`).join("<br>")
          + (p.pp != null ? `<br><span class="tsub">Shape score ${p.pp.toFixed(2)}${L.national[n] && L.national[n].pp ? ` (national median ${L.national[n].pp.toFixed(2)})` : ""}</span>` : ""); };
      svg.append("g").selectAll("path").data(fs.filter(f => !f.properties.x)).join("path").attr("d", path).attr("fill", fam).attr("class", "ldist")
        .on("mousemove", (ev, f) => showTip(ev, dtip(f))).on("mouseleave", hideTip).on("click", (ev, f) => showTip(ev, dtip(f)));
      $("#stMapCap").textContent = !fs.length ? (elect ? "New districts for 2026 aren't in the boundary data yet." : "No district lines for this Congress in the boundary data.")
        : fs.length === 1 && !fs[0].properties.d ? "One statewide seat: no lines to draw." : `${fs.length} district${fs.length === 1 ? "" : "s"}${elect ? ", with 2026 results" : ""}.`;
    }).catch(() => { $("#stMapCap").textContent = "The districts couldn't load."; });
    // facts
    const parties = Object.entries(info.parties || {}).sort((a, b) => b[1] - a[1]);
    const nat = L.national[n] || {};
    $("#stLeg").innerHTML = parties.map(([k, v]) => `<span><i class="sw" style="background:${col(k)}"></i>${({D:"Democratic",R:"Republican",U:"Not yet called",O:"Other",F:"Federalist / Pro-Admin.",DR:"Dem.-Republican / Anti-Admin.",NR:"Adams / Anti-Jackson",W:"Whig"})[k] || k} ${v}</span>`).join("");
    $("#stFacts").innerHTML = `<div><span>Seats</span><b>${info.seats || "—"}</b></div><div><span>Median shape score</span><b>${info.pp != null ? info.pp.toFixed(2) : "—"}</b></div>
      <div><span>National median</span><b>${nat.pp != null ? nat.pp.toFixed(2) : "—"}</b></div><div><span>Least compact district</span><b>${info.ppmin != null ? info.ppmin.toFixed(2) : "—"}</b></div>`;
    $("#stNote").textContent = elect ? "The 120th Congress shows the 2026 results; states that drew new maps for 2026 appear as an outline until the new boundaries are published." : "";
  }

  /* ---------- small line chart helper ---------- */
  function lineChart(el, series, opt){
    const Wd = Math.max(280, el.clientWidth || 360), Hh = opt.h || 160, M = {l: 34, r: 8, t: 8, b: 20};
    const svg = d3.select(el).html("").append("svg").attr("viewBox", `0 0 ${Wd} ${Hh}`);
    const xs = series.flatMap(s => s.pts.map(p => p[0])); if (!xs.length){ svg.remove(); el.innerHTML = `<p class="note">${opt.empty || "No data."}</p>`; return; }
    const x = d3.scaleLinear().domain(opt.xd || d3.extent(xs)).range([M.l, Wd - M.r]), y = d3.scaleLinear().domain(opt.yd).range([Hh - M.b, M.t]);
    opt.yt.forEach(t => { svg.append("line").attr("x1", M.l).attr("x2", Wd - M.r).attr("y1", y(t)).attr("y2", y(t)).attr("stroke", css("--line")).attr("stroke-dasharray", t === opt.ref ? "4 3" : null);
      svg.append("text").attr("x", M.l - 5).attr("y", y(t) + 3.5).attr("text-anchor", "end").attr("class", "ax").text(opt.yf ? opt.yf(t) : t); });
    x.ticks(Wd < 420 ? 4 : 7).forEach(t => svg.append("text").attr("x", x(t)).attr("y", Hh - 5).attr("text-anchor", "middle").attr("class", "ax").text(Math.round(t)));
    series.forEach(s => { svg.append("path").attr("d", d3.line().defined(p => p[1] != null).x(p => x(p[0])).y(p => y(p[1])).curve(s.step ? d3.curveStepAfter : d3.curveMonotoneX)(s.pts))
      .attr("fill", "none").attr("stroke", s.color).attr("stroke-width", s.w || 2).attr("stroke-dasharray", s.dash || null);
      if (s.dots) svg.append("g").selectAll("circle").data(s.pts.filter(p => p[1] != null)).join("circle").attr("cx", p => x(p[0])).attr("cy", p => y(p[1])).attr("r", 2.6).attr("fill", s.color); });
    if (opt.mark != null) svg.append("line").attr("x1", x(opt.mark)).attr("x2", x(opt.mark)).attr("y1", M.t).attr("y2", Hh - M.b).attr("stroke", css("--ink")).attr("opacity", .5);
    svg.append("rect").attr("x", M.l).attr("y", M.t).attr("width", Wd - M.l - M.r).attr("height", Hh - M.t - M.b).attr("fill", "transparent").style("cursor", opt.click ? "pointer" : null)
      .on("mousemove", ev => { const xv = x.invert(d3.pointer(ev)[0]); showTip(ev, opt.tip(xv)); }).on("mouseleave", hideTip)
      .on("click", ev => opt.click && opt.click(x.invert(d3.pointer(ev)[0])));
  }
  const nearestN = (ns, yr) => ns.reduce((a, b) => Math.abs(startYear(b) - yr) < Math.abs(startYear(a) - yr) ? b : a);

  function drawStatePP(){
    const st = S.st, ns = congs(st).filter(n => n <= 119);
    const sp = ns.map(n => [startYear(n), L.congress[st][n].pp]), np = Object.keys(L.national).map(Number).filter(n => n <= 119).map(n => [startYear(n), L.national[n].pp]);
    lineChart($("#stPP"), [{pts: np, color: css("--muted"), dash: "4 3", w: 1.5}, {pts: sp, color: css("--accent") || col("D"), step: true}],
      {yd: [0, .7], yt: [0, .2, .4, .6], xd: [1789, 2027], mark: startYear(S.n), yf: t => t.toFixed(1), empty: "One statewide seat throughout: no district lines.",
       tip: yr => { const n = nearestN(ns.length ? ns : [S.n], yr), v = L.congress[st][n] || {}; return `<b>${ord(n)} Congress · ${startYear(n)}</b><br>${esc(L.states[st].name)}: ${v.pp != null ? v.pp.toFixed(2) : "no drawn districts"}<br>National: ${(L.national[n] || {}).pp != null ? L.national[n].pp.toFixed(2) : "—"}`; },
       click: yr => { if (!ns.length) return; S.n = nearestN(ns, yr); $("#stRange").value = S.n; drawState(); drawStatePP(); }});
    $("#stPPLeg").innerHTML = `<span><i class="sw" style="background:${css("--accent") || col("D")}"></i>${esc(L.states[st].name)}</span><span><i class="sw" style="background:${css("--muted")}"></i>National median</span>`;
  }

  function drawVotes(){
    const st = S.st, V = L.votes[st] || {}, yrs = Object.keys(V).map(Number).sort((a, b) => a - b);
    if (!L.votes_years.length){ $("#stVotes").innerHTML = `<p class="note">Election results by district (1976–2024) are being added.</p>`; $("#stVLeg").innerHTML = ""; return; }
    const seatsD = yrs.map(y => [y, V[y].sD + V[y].sR ? V[y].sD / (V[y].sD + V[y].sR) : null]), voteD = yrs.map(y => [y, V[y].dv]);
    lineChart($("#stVotes"), [{pts: voteD, color: col("D"), dots: true}, {pts: seatsD, color: col("D"), dash: "5 3", dots: true}],
      {yd: [0, 1], yt: [0, .25, .5, .75, 1], ref: .5, xd: [1976, 2024], yf: t => Math.round(t * 100) + "%", empty: "No House results for this state.",
       tip: yr => { const y = yrs.reduce((a, b) => Math.abs(b - yr) < Math.abs(a - yr) ? b : a, yrs[0]), v = V[y];
         return `<b>${y} election</b><br>Democratic share of votes: ${pct(v.dv)}<br>Seats: ${v.sD} D, ${v.sR} R${v.sO ? `, ${v.sO} other` : ""}` + (v.eg != null ? `<br>Efficiency gap: ${Math.abs(v.eg * 100).toFixed(1)}% toward ${v.eg > 0 ? "Republicans" : "Democrats"}` : "") + (v.unc ? `<br><span class="tsub">${v.unc} race${v.unc === 1 ? "" : "s"} without both parties</span>` : ""); }});
    $("#stVLeg").innerHTML = `<span><i class="sw" style="background:${col("D")}"></i>Democratic share of votes</span><span><i class="sw" style="background:repeating-linear-gradient(90deg,${col("D")} 0 5px,transparent 5px 8px)"></i>Democratic share of seats</span><span>Above the line: Democrats win more seats than votes</span>`;
  }

  /* ---------- national compactness and the least compact districts ---------- */
  function drawNat(){
    const ns = Object.keys(L.national).map(Number).filter(n => n <= 119);
    lineChart($("#natPP"), [{pts: ns.map(n => [startYear(n), L.national[n].pp]), color: css("--accent") || col("D")}],
      {h: 190, yd: [0, .6], yt: [0, .2, .4, .6], xd: [1789, 2027], yf: t => t.toFixed(1),
       tip: yr => { const n = nearestN(ns, yr); return `<b>${ord(n)} Congress · ${startYear(n)}</b><br>Median shape score ${L.national[n].pp.toFixed(2)} across ${L.national[n].districts} districts`; }});
  }
  loadDistricts(119).then(F => {
    const ws = F.map(f => f.properties).filter(p => p.pp != null).sort((a, b) => a.pp - b.pp).slice(0, 10);
    $("#worst").innerHTML = ws.map(p => `<a class="item wrow" href="#state=${p.s}&congress=119" data-s="${p.s}"><span class="t">${esc(L.states[p.s].name)} ${ord(p.d)}</span><span class="m">${(p.m || []).map(m => esc(m[0]) + " (" + esc(m[1][0]) + ")").join(", ")}</span><span class="pill">${p.pp.toFixed(2)}</span></a>`).join("");
  }).catch(() => {});
  $("#worst").addEventListener("click", e => { const a = e.target.closest("[data-s]"); if (!a) return; e.preventDefault(); setState(a.dataset.s, 119); $("#state").scrollIntoView({behavior: "smooth"}); });

  setState(S.st, S.n); drawNat();
  let rt; addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(() => { drawStatePP(); drawVotes(); drawNat(); }, 150); });
})();
