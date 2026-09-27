/* The Bench: renders the Court on a date, balance charts, justices and rulings from window.BENCH. */
(function(){
  const B = window.BENCH; if (!B) return;
  const $ = s => document.querySelector(s);
  const esc = s => String(s == null ? "" : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"})[c]);
  const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  const LEAN_ORDER = ["lib","llib","mod","lcon","con","nr"];
  const LEAN_VAR = {lib:"--dem", llib:"--dem-soft", mod:"--mix", lcon:"--rep-soft", con:"--rep", nr:"--nr"};
  const PARTY_NAME = {R:"Republican", D:"Democratic", F:"Federalist", DR:"Democratic-Republican", W:"Whig", "—":"No party"};
  const PARTY_COLOR = {R:"var(--rep)", D:"var(--dem)", F:"#c9a227", DR:"#2f9e8f", W:"#e0a33a", "—":"var(--mix)"};
  const PARTY_ORDER = ["D","DR","—","W","F","R"];
  const ABBR = {"Republican":"R","Democratic":"D","Democratic-Republican":"DR","Federalist":"F","Whig":"W","No party":"—"};
  const BUCKET = {lib:"Liberal-leaning", con:"Conservative-leaning", mix:"Mixed"};
  const BUCKET_VAR = {lib:"--dem", con:"--rep", mix:"--mix"};
  const yearOf = iso => +iso.slice(0,4);
  const fmt = iso => new Date(iso + "T12:00:00Z").toLocaleDateString("en-US", {month:"long", day:"numeric", year:"numeric", timeZone:"UTC"});
  const lastName = n => n.replace(/,? Jr\.?$/, "").replace(/ II$/, "").split(" ").slice(-1)[0];
  const P = B.people, byName = Object.fromEntries(P.map(p => [p.name, p]));
  const tip = document.createElement("div"); tip.className = "tooltip"; document.body.appendChild(tip);
  const showTip = (ev, h) => { tip.innerHTML = h; tip.classList.add("on"); tip.style.left = Math.min(ev.clientX + 14, innerWidth - 260) + "px"; tip.style.top = (ev.clientY + 14) + "px"; };
  const hideTip = () => tip.classList.remove("on");
  const leanPill = (l, method) => `<span class="lpill l-${l}" title="${method === "score" ? "From Martin-Quinn voting scores" : method === "history" ? "Historians' assessment" : "Not rated"}">${esc(B.leans[l])}${method === "history" ? " <i>(historians)</i>" : ""}</span>`;
  const partyTag = s => `<span class="ptag"><i style="background:${PARTY_COLOR[ABBR[s.party]]}"></i>${esc(s.appointed_by)} <b>(${esc(ABBR[s.party] === "—" ? "no party" : ABBR[s.party])})</b></span>`;
  const years = p => p.stints.map(s => `${yearOf(s.oath)}–${s.ended ? yearOf(s.ended) : "present"}`).join(", ");
  const initials = n => n.replace(/,? Jr\.?/, "").split(" ").filter(w => /^[A-Z]/.test(w)).map(w => w[0]).filter((c,i,a) => i === 0 || i === a.length - 1).join("");

  /* ---------- the Court on a date ---------- */
  function seatedOn(iso){
    const out = [];
    P.forEach(p => p.stints.forEach(s => { if (s.oath <= iso && (!s.ended || s.ended > iso)) out.push({p, s}); }));
    return out.sort((a, b) => LEAN_ORDER.indexOf(a.p.lean) - LEAN_ORDER.indexOf(b.p.lean) || (a.p.mq_avg || 0) - (b.p.mq_avg || 0) || a.s.oath.localeCompare(b.s.oath));
  }
  function showCourt(y){
    const iso = y >= 2026 ? B.today : `${y}-07-01`;
    $("#yearRange").value = y; $("#yearOut").textContent = y;
    $("#courtTitle").textContent = y >= 2026 ? "The Court today" : `The Court on July 1, ${y}`;
    const seats = seatedOn(iso);
    const pc = {}, lc = {}; seats.forEach(({p, s}) => { const a = ABBR[s.party]; pc[a] = (pc[a]||0) + 1; lc[p.lean] = (lc[p.lean]||0) + 1; });
    const pTxt = PARTY_ORDER.filter(k => pc[k]).map(k => `<b style="color:${PARTY_COLOR[k]}">${pc[k]}</b> appointed by ${k === "—" ? "a president with no party" : PARTY_NAME[k] + (k === "D" || k === "R" ? "s" : " presidents")}`).join(", ");
    const lTxt = LEAN_ORDER.filter(k => lc[k]).map(k => `${lc[k]} ${B.leans[k].toLowerCase()}`).join(", ");
    $("#courtSum").innerHTML = `${seats.length} justices. ${pTxt}.<br>By lean: ${lTxt}.`;
    $("#seats").innerHTML = seats.map(({p, s}) => `<a class="seat" href="#j-${p.id}" data-j="${p.id}"><div class="mono">${esc(initials(p.name))}</div>
      <div class="sn">${esc(p.name)}${s.position === "chief" ? ' <span class="chief">Chief</span>' : ""}</div>
      <div class="sa">${partyTag(s)}</div><div class="sy">Since ${yearOf(s.oath)}</div>${leanPill(p.lean, p.method)}</a>`).join("");
  }
  $("#yearRange").addEventListener("input", e => showCourt(+e.target.value));
  $("#yearNow").addEventListener("click", () => showCourt(2026));
  $("#seats").addEventListener("click", e => { const a = e.target.closest("[data-j]"); if (!a) return; openJustice(a.dataset.j); });

  /* ---------- balance charts ---------- */
  function stacked(el, key, order, color, name){
    const W = Math.max(300, el.clientWidth || 600), H = 150, M = {l: 24, r: 6, t: 8, b: 20};
    const svg = d3.select(el).html("").append("svg").attr("viewBox", `0 0 ${W} ${H}`).attr("role", "img").attr("aria-label", name);
    const x = d3.scaleBand().domain(B.balance.map(d => d.y)).range([M.l, W - M.r]).paddingInner(.08);
    const y = d3.scaleLinear().domain([0, 10]).range([H - M.b, M.t]);
    [0, 5, 9].forEach(t => { svg.append("line").attr("x1", M.l).attr("x2", W - M.r).attr("y1", y(t)).attr("y2", y(t)).attr("stroke", css("--line"));
      svg.append("text").attr("x", M.l - 5).attr("y", y(t) + 3.5).attr("text-anchor", "end").text(t); });
    B.balance.forEach(d => { let acc = 0;
      order.forEach(k => { const v = d[key][k] || 0; if (!v) return;
        svg.append("rect").attr("x", x(d.y)).attr("width", x.bandwidth()).attr("y", y(acc + v)).attr("height", y(acc) - y(acc + v)).attr("fill", color(k)); acc += v; }); });
    d3.range(1800, 2027, W < 600 ? 50 : 25).forEach(yr => svg.append("text").attr("x", x(yr) + x.bandwidth() / 2).attr("y", H - 5).attr("text-anchor", "middle").text(yr));
    const hl = svg.append("rect").attr("y", M.t).attr("height", H - M.t - M.b).attr("fill", "none").attr("stroke", css("--ink")).style("opacity", 0);
    svg.append("rect").attr("x", M.l).attr("y", M.t).attr("width", W - M.l - M.r).attr("height", H - M.t - M.b).attr("fill", "transparent").style("cursor", "pointer")
      .on("mousemove", ev => { const [mx] = d3.pointer(ev); const i = Math.max(0, Math.min(B.balance.length - 1, Math.floor((mx - M.l) / x.step()))); const d = B.balance[i];
        hl.attr("x", x(d.y) - 1).attr("width", x.bandwidth() + 2).style("opacity", .8);
        showTip(ev, `<b>${d.y}</b><br>` + order.filter(k => d[key][k]).map(k => `<span style="color:${color(k)}">■</span> ${key === "lean" ? B.leans[k] : PARTY_NAME[k]}: ${d[key][k]}`).join("<br>") + `<br><i>Tap to see this Court</i>`); })
      .on("mouseleave", () => { hl.style("opacity", 0); hideTip(); })
      .on("click", ev => { const [mx] = d3.pointer(ev); const i = Math.max(0, Math.min(B.balance.length - 1, Math.floor((mx - M.l) / x.step()))); showCourt(B.balance[i].y); document.getElementById("court").scrollIntoView({behavior: "smooth"}); });
  }
  const leanColor = k => css(LEAN_VAR[k]) || css("--line");
  const partyColor = k => { const c = PARTY_COLOR[k]; return c.startsWith("var(") ? css(c.slice(4, -1)) : c; };
  function caseChart(){
    const el = $("#chCases"), W = Math.max(300, el.clientWidth || 600), H = 170, M = {l: 34, r: 6, t: 8, b: 20};
    const svg = d3.select(el).html("").append("svg").attr("viewBox", `0 0 ${W} ${H}`).attr("role", "img").attr("aria-label", "Supreme Court decisions per term");
    const C = B.caseload, keys = [["argued", "--accent"], ["summary", "--int"], ["other", "--muted"]];
    const x = d3.scaleBand().domain(C.map(d => d.y)).range([M.l, W - M.r]).paddingInner(.08);
    const y = d3.scaleLinear().domain([0, d3.max(C, d => d.argued + d.summary + d.other)]).nice(4).range([H - M.b, M.t]);
    y.ticks(4).forEach(t => { svg.append("line").attr("x1", M.l).attr("x2", W - M.r).attr("y1", y(t)).attr("y2", y(t)).attr("stroke", css("--line"));
      svg.append("text").attr("x", M.l - 5).attr("y", y(t) + 3.5).attr("text-anchor", "end").text(t); });
    C.forEach(d => { let acc = 0; keys.forEach(([k, v]) => { const n = d[k]; if (!n) return;
      svg.append("rect").attr("x", x(d.y)).attr("width", x.bandwidth()).attr("y", y(acc + n)).attr("height", y(acc) - y(acc + n)).attr("fill", css(v)); acc += n; }); });
    d3.range(1800, 2026, W < 600 ? 50 : 25).forEach(yr => x(yr) != null && svg.append("text").attr("x", x(yr) + x.bandwidth() / 2).attr("y", H - 5).attr("text-anchor", "middle").text(yr));
    const hl = svg.append("rect").attr("y", M.t).attr("height", H - M.t - M.b).attr("fill", "none").attr("stroke", css("--ink")).style("opacity", 0);
    svg.append("rect").attr("x", M.l).attr("y", M.t).attr("width", W - M.l - M.r).attr("height", H - M.t - M.b).attr("fill", "transparent")
      .on("mousemove", ev => { const [mx] = d3.pointer(ev); const d = C[Math.max(0, Math.min(C.length - 1, Math.floor((mx - M.l) / x.step())))];
        hl.attr("x", x(d.y) - 1).attr("width", x.bandwidth() + 2).style("opacity", .8);
        showTip(ev, `<b>${d.y} term</b><br>After argument: ${d.argued}<br>Summary: ${d.summary}<br>Other: ${d.other}<br>Total: ${d.argued + d.summary + d.other}`); })
      .on("mouseleave", () => { hl.style("opacity", 0); hideTip(); });
  }
  function dirChart(){
    const el = $("#chDir"), W = Math.max(300, el.clientWidth || 600), H = 150, M = {l: 34, r: 6, t: 8, b: 20};
    const C = B.caseload.filter(d => d.y >= 1946 && (d.lib + d.con) > 0).map(d => ({y: d.y, s: d.lib / (d.lib + d.con) * 100, n: d.lib + d.con}));
    const svg = d3.select(el).html("").append("svg").attr("viewBox", `0 0 ${W} ${H}`).attr("role", "img").attr("aria-label", "Share of decisions with a liberal outcome");
    const x = d3.scaleLinear().domain([1946, d3.max(C, d => d.y)]).range([M.l, W - M.r]), y = d3.scaleLinear().domain([0, 100]).range([H - M.b, M.t]);
    svg.append("rect").attr("x", M.l).attr("width", W - M.l - M.r).attr("y", M.t).attr("height", H - M.t - M.b).attr("fill", css("--rep")).attr("fill-opacity", .5);
    svg.append("path").attr("d", d3.area().x(d => x(d.y)).y0(y(0)).y1(d => y(d.s)).curve(d3.curveStep)(C)).attr("fill", css("--dem")).attr("fill-opacity", .75);
    [0, 50, 100].forEach(t => { svg.append("line").attr("x1", M.l).attr("x2", W - M.r).attr("y1", y(t)).attr("y2", y(t)).attr("stroke", t === 50 ? css("--ink") : css("--line")).attr("stroke-dasharray", t === 50 ? "4 3" : null);
      svg.append("text").attr("x", M.l - 5).attr("y", y(t) + 3.5).attr("text-anchor", "end").text(t + "%"); });
    d3.range(1950, 2025, 10).forEach(yr => svg.append("text").attr("x", x(yr)).attr("y", H - 5).attr("text-anchor", "middle").text(yr));
    svg.append("rect").attr("x", M.l).attr("y", M.t).attr("width", W - M.l - M.r).attr("height", H - M.t - M.b).attr("fill", "transparent")
      .on("mousemove", ev => { const [mx] = d3.pointer(ev); const yr = Math.round(x.invert(mx)); const d = C.find(c => c.y === yr); if (!d) return hideTip();
        showTip(ev, `<b>${d.y} term</b><br>Liberal outcome: ${d.s.toFixed(0)}%<br>Conservative: ${(100 - d.s).toFixed(0)}%<br>${d.n} decisions with a direction`); })
      .on("mouseleave", hideTip);
  }
  (function(){ const C = B.caseload, last = C[C.length - 1], peak = C.reduce((a, b) => (b.argued > a.argued ? b : a));
    $("#clSum").innerHTML = `The Court has decided <b>${B.total_cases.toLocaleString()}</b> cases since 1791, <b>${B.total_argued.toLocaleString()}</b> of them after argument with a full opinion. The busiest term was ${peak.y}, with ${peak.argued} argued decisions; in the ${last.y} term${last.y >= 2025 ? " (from provisional records, before the database's official release)" : ""} it decided ${last.argued}.`;
    $("#legCases").innerHTML = [["After argument (plenary)", "--accent"], ["Summary, no argument", "--int"], ["Other (4–4 ties, decrees)", "--muted"]].map(([l, v]) => `<span><i class="sw" style="background:var(${v})"></i>${l}</span>`).join(""); })();
  function drawCharts(){
    caseChart(); dirChart();
    stacked($("#chLean"), "lean", LEAN_ORDER, leanColor, "Justices by lean, each year");
    stacked($("#chParty"), "party", PARTY_ORDER, partyColor, "Justices by appointing president's party, each year");
  }
  $("#legLean").innerHTML = LEAN_ORDER.map(k => `<span><i class="sw" style="background:var(${LEAN_VAR[k]})"></i>${B.leans[k]}</span>`).join("");
  $("#legParty").innerHTML = PARTY_ORDER.map(k => `<span><i class="sw" style="background:${PARTY_COLOR[k]}"></i>${PARTY_NAME[k]}</span>`).join("");

  /* ---------- justices ---------- */
  const JF = {lean: new Set(LEAN_ORDER), party: new Set(Object.keys(PARTY_NAME)), era: "all", q: ""};
  const ERA = {all:"All eras", now:"Serving now", modern:"1937–today", mid:"1865–1936", early:"Before 1865"};
  function eraOf(p){ const y = yearOf(p.first); return y >= 1937 ? "modern" : y >= 1865 ? "mid" : "early"; }
  function spark(p){
    const ys = Object.keys(p.mq).map(Number); if (ys.length < 2) return "";
    const W = 260, H = 54, x = d3.scaleLinear().domain(d3.extent(ys)).range([4, W - 4]), y = d3.scaleLinear().domain([-5, 4]).range([4, H - 4]);
    const pts = ys.map(t => `${x(t).toFixed(1)},${y(-p.mq[t]).toFixed(1)}`).join(" ");
    return `<div class="spark"><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Martin-Quinn score by term"><line x1="0" x2="${W}" y1="${y(0)}" y2="${y(0)}" stroke="var(--line)"/>
      <text x="2" y="10" class="st">Conservative ↑</text><text x="2" y="${H - 2}" class="st">Liberal ↓</text>
      <polyline points="${pts}" fill="none" stroke="var(--ink-2)" stroke-width="1.8"/></svg><span>${ys[0]}–${ys[ys.length - 1]} voting score by term</span></div>`;
  }
  function renderJustices(){
    const q = JF.q.toLowerCase();
    const list = P.slice().reverse().filter(p => JF.lean.has(p.lean) && p.stints.some(s => JF.party.has(ABBR[s.party]))
      && (JF.era === "all" || (JF.era === "now" ? p.current : eraOf(p) === JF.era)) && (!q || (p.name + " " + p.stints.map(s => s.appointed_by).join(" ")).toLowerCase().includes(q)));
    $("#jGrid").innerHTML = list.map(p => `<details class="jcard" id="j-${p.id}"><summary>
        <div class="jh"><span class="jn">${esc(p.name)}</span>${p.chief ? '<span class="chief">Chief</span>' : ""}${p.current ? '<span class="now">Serving</span>' : ""}</div>
        <div class="jy">${years(p)}</div>
        <div class="ja">${p.stints.map(s => `${s.position === "chief" && p.stints.length > 1 ? "As chief: " : p.stints.length > 1 ? "Associate: " : ""}${partyTag(s)}`).join("<br>")}</div>
        ${leanPill(p.lean, p.method)}</summary>
      <div class="jb">
        ${p.method === "score" ? `<p><b>Lean:</b> ${esc(B.leans[p.lean])}, from an average Martin-Quinn score of ${p.mq_avg > 0 ? "+" : ""}${p.mq_avg} across ${Object.keys(p.mq).length} terms.</p>` : ""}
        ${p.method === "history" ? `<p><b>Lean (historians' assessment):</b> ${esc(p.basis)}</p>` : ""}
        ${p.method === "none" ? `<p><b>Not rated.</b> ${yearOf(p.first) < 1865 ? "Today's left and right don't map onto the early Court's main questions." : "The record is too thin or mixed to call."}</p>` : ""}
        ${p.drift ? `<p class="drift">${esc(p.drift)}</p>` : ""}
        ${p.method === "score" ? spark(p) : ""}
        ${p.known ? `<p>${esc(p.known)}</p>` : ""}
        ${p.record && p.record.cases ? `<p class="rec"><span><b>${p.record.cases.toLocaleString()}</b> cases voted in</span><span><b>${Math.round(p.record.majority_share * 100)}%</b> in the majority</span><span><b>${(p.record.dissents || 0).toLocaleString()}</b> dissents</span><span><b>${(p.record.opinions_written || 0).toLocaleString()}</b> opinions written</span></p>` : ""}
        ${p.stints.filter(s => s.conf).map(s => `<p class="meta">Senate confirmation vote: ${esc(s.conf)}</p>`).join("")}
        <p class="meta">${p.stints.map(s => `${s.position === "chief" ? "Chief justice" : "Associate justice"}, sworn in ${fmt(s.oath)}${s.ended ? `; ${s.end_reason || "left"} ${fmt(s.ended)}` : ""}`).join(". ")}.</p>
        ${B.rulings.some(r => r.author === p.name) ? `<p class="meta">Wrote: ${B.rulings.filter(r => r.author === p.name).map(r => `<a href="#r-${r.id}" data-r="${r.id}">${esc(r.title)}</a>`).join(", ")}</p>` : ""}
      </div></details>`).join("") || `<p class="note">No justices match these filters.</p>`;
  }
  function chipRow(label, items, isOn, cls){ return `<div class="frow"><span class="flab">${label}</span>${items.map(([k, l, c]) => `<button type="button" class="fchip ${cls}" data-k="${k}" aria-pressed="${isOn(k)}">${c ? `<i style="background:${c}"></i>` : ""}${esc(l)}</button>`).join("")}</div>`; }
  function renderJFilters(){
    $("#jFilters").innerHTML = chipRow("Lean", LEAN_ORDER.map(k => [k, B.leans[k], `var(${LEAN_VAR[k]})`]), k => JF.lean.has(k), "jl")
      + chipRow("Appointed by", ["R","D","DR","F","W","—"].map(k => [k, k === "—" ? "No party" : PARTY_NAME[k] + (k === "R" || k === "D" ? "s" : "s"), PARTY_COLOR[k]]), k => JF.party.has(k), "jp")
      + chipRow("When", Object.entries(ERA), k => JF.era === k, "je")
      + `<div class="frow"><input type="search" id="jq" placeholder="Search a justice or president" value="${esc(JF.q)}" aria-label="Search justices"></div>`;
  }
  $("#jFilters").addEventListener("click", e => { const b = e.target.closest(".fchip"); if (!b) return; const k = b.dataset.k;
    if (b.classList.contains("jl")) toggle(JF.lean, k, LEAN_ORDER); else if (b.classList.contains("jp")) toggle(JF.party, k, Object.keys(PARTY_NAME)); else JF.era = k;
    renderJFilters(); renderJustices(); });
  $("#jFilters").addEventListener("input", e => { if (e.target.id === "jq"){ JF.q = e.target.value; renderJustices(); } });
  // First tap on a chip shows only that value; later taps add or remove; removing the last one resets.
  function toggle(set, k, all){ if (set.size === all.length){ set.clear(); set.add(k); return; } set.has(k) ? set.delete(k) : set.add(k); if (!set.size) all.forEach(x => set.add(x)); }
  function openJustice(id){ JF.lean = new Set(LEAN_ORDER); JF.party = new Set(Object.keys(PARTY_NAME)); JF.era = "all"; JF.q = ""; renderJFilters(); renderJustices();
    const el = document.getElementById("j-" + id); if (el){ el.open = true; el.scrollIntoView({behavior: "smooth", block: "center"}); } }

  /* ---------- rulings ---------- */
  const RF = {bucket: new Set(Object.keys(BUCKET)), topic: new Set(Object.keys(B.topics))};
  const who = list => { const c = {}; list.forEach(m => c[m.party] = (c[m.party] || 0) + 1);
    return PARTY_ORDER.filter(k => c[k]).map(k => `<b style="color:${PARTY_COLOR[k]}">${c[k]}</b> ${k === "—" ? "appointed by Washington or Tyler (no party)" : PARTY_NAME[k] + " appointee" + (c[k] > 1 ? "s" : "")}`).join(", "); };
  const names = list => list.map(m => `<a href="#j-${m.id}" data-j="${m.id}" class="jname"><i style="background:${PARTY_COLOR[m.party]}"></i>${esc(lastName(m.n))}</a>`).join(" ");
  function renderRulings(){
    const list = B.rulings.filter(r => RF.bucket.has(r.bucket) && RF.topic.has(r.topic)).slice().reverse();
    $("#rList").innerHTML = list.map(r => `<details class="item" id="r-${r.id}"><summary><span class="t">${esc(r.title)}</span>
        <span class="pill" style="color:var(${BUCKET_VAR[r.bucket]});border-color:color-mix(in srgb,var(${BUCKET_VAR[r.bucket]}) 45%,transparent)">${BUCKET[r.bucket]}</span>
        <span class="m">${fmt(r.date)} · ${esc(r.split)} · ${esc(B.topics[r.topic])}</span></summary>
      <div class="body"><p style="margin:0">${esc(r.summary)}</p><p style="margin:0"><b>Why it matters:</b> ${esc(r.impact)}</p>
        ${r.overruled ? `<p style="margin:0"><b>Later overruled or superseded by:</b> ${esc(r.overruled)}</p>` : ""}
        <p style="margin:0"><b>Majority opinion:</b> ${esc(r.author)}</p>
        <div class="vote"><div><b>Majority (${r.maj.length})</b>: ${who(r.maj)}<div class="names">${names(r.maj)}</div></div>
          ${r.dis.length ? `<div><b>Dissent (${r.dis.length})</b>: ${who(r.dis)}<div class="names">${names(r.dis)}</div></div>` : `<div><b>No dissents.</b></div>`}</div>
        ${r.vote_note ? `<p class="meta">${esc(r.vote_note)}</p>` : ""}${r.legacy ? `<p class="meta">Vote list from the Supreme Court Database's older records.</p>` : ""}
        ${r.link ? `<a href="${r.link}" target="_blank" rel="noopener">Read the opinion (${esc(r.cite)})</a>` : ""}</div></details>`).join("") || `<p class="note">No rulings match these filters.</p>`;
  }
  function renderRFilters(){
    const cnt = k => B.rulings.filter(r => r.bucket === k && RF.topic.has(r.topic)).length;
    $("#rFilters").innerHTML = chipRow("What it did", Object.entries(BUCKET).map(([k, l]) => [k, `${l} ${cnt(k)}`, `var(${BUCKET_VAR[k]})`]), k => RF.bucket.has(k), "rb")
      + chipRow("Topic", Object.entries(B.topics), k => RF.topic.has(k), "rt");
  }
  $("#rFilters").addEventListener("click", e => { const b = e.target.closest(".fchip"); if (!b) return;
    b.classList.contains("rb") ? toggle(RF.bucket, b.dataset.k, Object.keys(BUCKET)) : toggle(RF.topic, b.dataset.k, Object.keys(B.topics));
    renderRFilters(); renderRulings(); });
  document.addEventListener("click", e => {
    const j = e.target.closest("a[data-j]"); if (j && !j.closest("#seats")){ e.preventDefault(); openJustice(j.dataset.j); return; }
    const r = e.target.closest("a[data-r]"); if (r){ e.preventDefault(); RF.bucket = new Set(Object.keys(BUCKET)); RF.topic = new Set(Object.keys(B.topics)); renderRFilters(); renderRulings();
      const el = document.getElementById("r-" + r.dataset.r); if (el){ el.open = true; el.scrollIntoView({behavior: "smooth", block: "center"}); } }
  });

  showCourt(2026); drawCharts(); renderJFilters(); renderJustices(); renderRFilters(); renderRulings();
  let rt; addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(drawCharts, 150); });
  if (location.hash){ const h = location.hash.slice(1); if (h.startsWith("j-")) openJustice(h.slice(2)); else if (h.startsWith("r-")){ const el = document.getElementById(h); if (el){ el.open = true; el.scrollIntoView(); } } }
})();
