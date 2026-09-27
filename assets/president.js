/* Charts for president pages. Reads window.PAGE (built by data/build_presidents.py). */
(function(){
  const P = window.PAGE; if (!P || !window.d3) return;
  const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  const tip = document.createElement("div"); tip.className = "tooltip"; document.body.appendChild(tip);
  const showTip = (ev, html) => { tip.innerHTML = html; tip.classList.add("on");
    const x = Math.min(ev.clientX + 14, window.innerWidth - 250); tip.style.left = x + "px"; tip.style.top = (ev.clientY + 14) + "px"; };
  const hideTip = () => tip.classList.remove("on");
  const money = v => { const a = Math.abs(v), s = v < 0 ? "−" : "";
    if (a >= 1e12) return s + "$" + d3.format(".3~g")(a / 1e12) + "T";
    if (a >= 1e9) return s + "$" + d3.format(".3~g")(a / 1e9) + "B";
    if (a >= 1e6) return s + "$" + d3.format(".3~g")(a / 1e6) + "M";
    return s + "$" + d3.format(",")(Math.round(a)); };
  const pct = v => d3.format(".1f")(v) + "%";

  function frame(el, H, yDomain, yFmt, opts){
    opts = opts || {};
    const W = Math.max(280, el.clientWidth || 500), M = {l: 50, r: 10, t: 12, b: 22};
    const svg = d3.select(el).html("").append("svg").attr("viewBox", `0 0 ${W} ${H}`).attr("role", "img").attr("aria-label", opts.label || "");
    const years = P.econ.map(d => d.y);
    const x = d3.scaleLinear().domain([d3.min(years) - 0.5, d3.max(years) + 0.5]).range([M.l, W - M.r]);
    const y = d3.scaleLinear().domain(yDomain).nice(4).range([H - M.b, M.t]);
    // term shading
    P.terms.forEach((t, i) => {
      const a = Math.max(x.domain()[0], t[0]), b = Math.min(x.domain()[1], t[1]);
      svg.append("rect").attr("x", x(a)).attr("width", Math.max(0, x(b) - x(a))).attr("y", M.t).attr("height", H - M.b - M.t)
        .attr("fill", css("--ink")).attr("fill-opacity", .06);
      svg.append("line").attr("x1", x(a)).attr("x2", x(a)).attr("y1", M.t).attr("y2", H - M.b).attr("stroke", css("--ink-2")).attr("stroke-dasharray", "3 3").attr("stroke-width", 1);
      if (t[1] < x.domain()[1]) svg.append("line").attr("x1", x(b)).attr("x2", x(b)).attr("y1", M.t).attr("y2", H - M.b).attr("stroke", css("--ink-2")).attr("stroke-dasharray", "3 3").attr("stroke-width", 1);
      svg.append("text").attr("x", x(a) + 4).attr("y", M.t + 10).text(P.terms.length > 1 ? (i ? "2nd term" : "1st term") : "In office");
    });
    y.ticks(4).forEach(tk => {
      svg.append("line").attr("x1", M.l).attr("x2", W - M.r).attr("y1", y(tk)).attr("y2", y(tk)).attr("stroke", tk === 0 ? css("--muted") : css("--line"));
      svg.append("text").attr("x", M.l - 6).attr("y", y(tk) + 3.5).attr("text-anchor", "end").text(yFmt(tk));
    });
    const step = years.length > 16 ? 4 : 2;
    years.filter(yr => yr % step === 0).forEach(yr => svg.append("text").attr("x", x(yr)).attr("y", H - 6).attr("text-anchor", "middle").text(yr));
    return {svg, x, y, W, H, M};
  }
  const inTerm = yr => P.terms.some(t => yr + 0.5 >= t[0] && yr - 0.5 <= t[1]);

  function lineChart(id, key, color, fmt, label){
    const el = document.getElementById(id); if (!el) return;
    const pts = P.econ.filter(d => d[key] != null);
    if (!pts.length){ el.innerHTML = `<p class="note">No data for these years.</p>`; return; }
    const f = frame(el, 190, [0, d3.max(pts, d => d[key]) * 1.05], fmt, {label});
    const line = d3.line().x(d => f.x(d.y)).y(d => f.y(d[key])).curve(d3.curveMonotoneX);
    const area = d3.area().x(d => f.x(d.y)).y0(f.y(0)).y1(d => f.y(d[key])).curve(d3.curveMonotoneX);
    f.svg.append("path").attr("d", area(pts)).attr("fill", color).attr("fill-opacity", .14);
    f.svg.append("path").attr("d", line(pts)).attr("fill", "none").attr("stroke", color).attr("stroke-width", 2);
    f.svg.selectAll("circle.p").data(pts.filter(d => inTerm(d.y))).join("circle").attr("class", "p").attr("cx", d => f.x(d.y)).attr("cy", d => f.y(d[key])).attr("r", 3).attr("fill", color);
    hover(f, pts, d => `<b>${d.y}</b><br>${label}: ${fmt(d[key])}`);
  }
  function barChart(id, key, fmt, label, colorFn){
    const el = document.getElementById(id); if (!el) return;
    const pts = P.econ.filter(d => d[key] != null);
    if (!pts.length){ el.innerHTML = `<p class="note">No data for these years.</p>`; return; }
    const lo = Math.min(0, d3.min(pts, d => d[key])), hi = Math.max(0, d3.max(pts, d => d[key]));
    const f = frame(el, 190, [lo, hi], fmt, {label});
    const bw = Math.max(2, (f.x(1) - f.x(0)) * 0.7);
    f.svg.selectAll("rect.b").data(pts).join("rect").attr("class", "b")
      .attr("x", d => f.x(d.y) - bw / 2).attr("width", bw).attr("rx", 2)
      .attr("y", d => Math.min(f.y(0), f.y(d[key]))).attr("height", d => Math.max(1, Math.abs(f.y(d[key]) - f.y(0))))
      .attr("fill", d => colorFn(d)).attr("fill-opacity", d => inTerm(d.y) ? 1 : .35);
    hover(f, pts, d => `<b>${d.y}</b><br>${label}: ${fmt(d[key])}`);
  }
  function hover(f, pts, html){
    const hl = f.svg.append("line").attr("stroke", css("--ink-2")).attr("stroke-width", 1).style("opacity", 0).attr("y1", f.M.t).attr("y2", f.H - f.M.b);
    f.svg.append("rect").attr("x", f.M.l).attr("y", f.M.t).attr("width", f.W - f.M.l - f.M.r).attr("height", f.H - f.M.t - f.M.b).attr("fill", "transparent")
      .on("mousemove", ev => { const [mx] = d3.pointer(ev); const yr = Math.round(f.x.invert(mx)); const d = pts.find(p => p.y === yr); if (!d) return hideTip();
        hl.attr("x1", f.x(yr)).attr("x2", f.x(yr)).style("opacity", 1); showTip(ev, html(d)); })
      .on("mouseleave", () => { hl.style("opacity", 0); hideTip(); });
  }
  function countChart(id, rows, series, label){
    // rows: [{y, a, b}] ; series: [{k, name, color}]
    const el = document.getElementById(id); if (!el || !rows.length) return;
    const W = Math.max(280, el.clientWidth || 500), H = 190, M = {l: 40, r: 10, t: 12, b: 22};
    const svg = d3.select(el).html("").append("svg").attr("viewBox", `0 0 ${W} ${H}`).attr("role", "img").attr("aria-label", label);
    const x = d3.scaleBand().domain(rows.map(r => r.y)).range([M.l, W - M.r]).padding(.25);
    const tot = r => series.reduce((s, se) => s + (r[se.k] || 0), 0);
    const y = d3.scaleLinear().domain([0, d3.max(rows, tot) || 1]).nice(4).range([H - M.b, M.t]);
    y.ticks(4).forEach(tk => { svg.append("line").attr("x1", M.l).attr("x2", W - M.r).attr("y1", y(tk)).attr("y2", y(tk)).attr("stroke", tk === 0 ? css("--muted") : css("--line"));
      svg.append("text").attr("x", M.l - 6).attr("y", y(tk) + 3.5).attr("text-anchor", "end").text(d3.format(",")(tk)); });
    rows.forEach(r => { let acc = 0;
      series.forEach(se => { const v = r[se.k] || 0; if (!v) return;
        svg.append("rect").attr("x", x(r.y)).attr("width", x.bandwidth()).attr("y", y(acc + v)).attr("height", Math.max(1, y(acc) - y(acc + v) - (acc ? 1.5 : 0)))
          .attr("rx", 2).attr("fill", css(se.color))
          .on("mousemove", ev => showTip(ev, `<b>${r.y}</b><br>${series.map(s2 => `${s2.name}: ${d3.format(",")(r[s2.k] || 0)}`).join("<br>")}`)).on("mouseleave", hideTip);
        acc += v; });
      svg.append("text").attr("x", x(r.y) + x.bandwidth() / 2).attr("y", y(tot(r)) - 4).attr("text-anchor", "middle").attr("class", "lbl").text(d3.format(",")(tot(r)));
      svg.append("text").attr("x", x(r.y) + x.bandwidth() / 2).attr("y", H - 6).attr("text-anchor", "middle").text(rows.length > 10 ? "'" + String(r.y).slice(2) : r.y); });
  }

  function drawAll(){
    lineChart("ch-debt", "debt", css("--debt"), money, "National debt");
    lineChart("ch-ratio", "ratio", css("--debt-3"), v => d3.format(".0f")(v) + "%", "Debt-to-GDP");
    barChart("ch-deficit", "bal", money, "Surplus (+) / deficit (−)", d => d.bal >= 0 ? css("--debt") : css("--def"));
    lineChart("ch-unemp", "unemp", css("--int"), pct, "Unemployment");
    barChart("ch-infl", "infl", pct, "Inflation", () => css("--def"));
    countChart("ch-eo", Object.entries(P.eo).map(([y, n]) => ({y: +y, n})), [{k: "n", name: "Executive orders", color: "--accent"}], "Executive orders by year");
    countChart("ch-clem", Object.entries(P.clem).map(([y, v]) => ({y: +y, p: v[0], c: v[1]})),
      [{k: "p", name: "Pardons", color: "--accent"}, {k: "c", name: "Commutations", color: "--int"}], "Pardons and commutations by year");
  }
  drawAll();
  let rt; window.addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(drawAll, 150); });

  // every executive order: search, topic, year, show more
  document.querySelectorAll(".eoall").forEach(box => {
    const items = [...box.querySelectorAll(".eolist li")], q = box.querySelector(".eoq"), tg = box.querySelector(".eotg"), yr = box.querySelector(".eoy"),
      more = box.querySelector(".eomore"), count = box.querySelector(".eocount"); let shown = 50;
    items.forEach(li => li._t = li.textContent.toLowerCase());
    function apply(){
      const qs = q.value.trim().toLowerCase(), t = tg.value, y = yr.value; let n = 0, vis = 0;
      items.forEach(li => { const ok = (!qs || li._t.includes(qs)) && (!t || ("|" + li.dataset.tg + "|").includes("|" + t + "|")) && (!y || li.dataset.y === y);
        if (ok) n++; const show = ok && n <= shown; li.hidden = !show; if (show) vis++; });
      count.textContent = `Showing ${vis.toLocaleString()} of ${n.toLocaleString()}`; more.hidden = vis >= n;
    }
    [q, tg, yr].forEach(el => el.addEventListener("input", () => { shown = 50; apply(); }));
    more.addEventListener("click", () => { shown += 200; apply(); });
    apply();
  });

  // highlight current section in the jump bar
  const jump = document.querySelector(".jump");
  if (jump && "IntersectionObserver" in window){
    const seen = new Map();
    const io = new IntersectionObserver(ents => { ents.forEach(en => seen.set(en.target.id, en.isIntersecting ? en.intersectionRect.height : 0));
      let best = null, bh = 0; seen.forEach((h, id) => { if (h > bh){ bh = h; best = id; } });
      jump.querySelectorAll("a").forEach(a => { const on = a.getAttribute("href") === "#" + best; a.classList.toggle("on", on);
        if (on && jump.scrollWidth > jump.clientWidth) jump.scrollTo({left: a.offsetLeft - 16, behavior: "smooth"}); }); },
      {threshold: [0, .25, .5, .75, 1], rootMargin: "-60px 0px -40% 0px"});
    document.querySelectorAll("section.block").forEach(s => io.observe(s));
  }
})();
