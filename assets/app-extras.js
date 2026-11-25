/*!
 * app-extras.js v1 — "Add to home screen" + "Support this project" for Ryan Behrens's apps.
 *
 * One file, no dependencies. The same copy is dropped into each app so every app
 * installs and asks for support the same way (modeled on Scene Translator).
 * The source of truth lives in github.com/ryanbehrens/software-portfolio/shared/.
 *
 * Usage:
 *   AppExtras.init({ name: 'CubeLab' });
 *   AppExtras.mountBanner(el)        // dismissible "Add CubeLab to your home screen" bar (phones only)
 *   AppExtras.mountInstallCard(el)   // "Install on your phone" card with status + button
 *   AppExtras.mountSupport(el, { text })  // PayPal support card
 *   AppExtras.openInstallHelp()      // device-specific install steps
 *
 * Theming: each app sets these CSS variables (all optional):
 *   --ax-accent, --ax-accent-ink, --ax-surface, --ax-surface-2, --ax-text, --ax-muted,
 *   --ax-line, --ax-radius, --ax-font
 */
(function () {
  'use strict';
  if (window.AppExtras) return;

  var PAYPAL_URL = 'https://paypal.me/RBehrens42';
  var cfg = { name: 'this app', storageKey: 'app-extras' };
  var installEvt = null;
  var listeners = [];

  var ua = navigator.userAgent || '';
  var IS_ANDROID = /Android/i.test(ua);
  // iPads report themselves as a Mac with a touchscreen.
  var IS_IOS = !IS_ANDROID && (/iPad|iPhone|iPod/.test(ua) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1));
  var IS_CHROME_IOS = IS_IOS && /CriOS|FxiOS|EdgiOS/.test(ua);
  var IS_PHONE = IS_IOS || IS_ANDROID;

  function isInstalled() {
    return (window.matchMedia && matchMedia('(display-mode: standalone)').matches) || navigator.standalone === true;
  }
  function get(k, d) { try { var v = localStorage.getItem(cfg.storageKey + ':' + k); return v == null ? d : JSON.parse(v); } catch (e) { return d; } }
  function set(k, v) { try { localStorage.setItem(cfg.storageKey + ':' + k, JSON.stringify(v)); } catch (e) {} }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function el(html) { var t = document.createElement('div'); t.innerHTML = html.trim(); return t.firstChild; }
  function resolve(target) { return typeof target === 'string' ? document.querySelector(target) : target; }
  function changed() { listeners.forEach(function (fn) { try { fn(); } catch (e) {} }); }

  var ICON_PHONE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="6" y="2" width="12" height="20" rx="3"/><path d="M12 7v7m-3-3 3 3 3-3M10 18h4"/></svg>';
  var ICON_HEART = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/></svg>';
  var ICON_SHARE = '<svg class="ax-share" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-label="Share"><path d="M12 3v12M8 7l4-4 4 4"/><path d="M6 11H5a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-8a1 1 0 0 0-1-1h-1"/></svg>';

  var CSS = [
    '.ax{--a:var(--ax-accent,#3b82f6);--ai:var(--ax-accent-ink,#fff);--s:var(--ax-surface,rgba(127,127,127,.08));--s2:var(--ax-surface-2,rgba(127,127,127,.14));',
    '--t:var(--ax-text,inherit);--m:var(--ax-muted,rgba(127,127,127,.95));--l:var(--ax-line,rgba(127,127,127,.25));--r:var(--ax-radius,14px);',
    'font-family:var(--ax-font,inherit);color:var(--t);box-sizing:border-box;text-align:left}',
    '.ax *,.ax *::before,.ax *::after{box-sizing:border-box}',
    '.ax svg{width:22px;height:22px;flex:none}',
    '.ax-btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:44px;padding:0 16px;border-radius:calc(var(--r) - 4px);',
    'border:1px solid var(--l);background:var(--s2);color:var(--t);font:inherit;font-size:15px;font-weight:600;cursor:pointer;text-decoration:none;line-height:1.2}',
    '.ax-btn:hover{border-color:var(--a)}',
    '.ax-btn.ax-primary{background:var(--a);border-color:var(--a);color:var(--ai)}',
    '.ax-btn.ax-block{display:flex;width:100%;min-height:52px;font-size:16px}',
    '.ax-btn svg{color:currentColor}',
    '.ax-btn:not(.ax-primary) svg{color:var(--a)}',
    '.ax-bar{display:flex;align-items:center;gap:10px;margin:0 0 12px;padding:10px 8px 10px 14px;border-radius:var(--r);',
    'border:1px solid color-mix(in srgb,var(--a) 55%,var(--l));background:color-mix(in srgb,var(--a) 13%,var(--s));font-size:14.5px;line-height:1.35}',
    '.ax-bar svg{color:var(--a)}',
    '.ax-bar span{flex:1;min-width:0}',
    '.ax-bar .ax-btn{min-height:38px;padding:0 12px;font-size:14px}',
    '.ax-x{border:0;background:none;color:var(--m);font-size:18px;width:34px;height:34px;flex:none;cursor:pointer;border-radius:8px}',
    '.ax-card{border:1px solid var(--l);background:var(--s);border-radius:var(--r);padding:16px}',
    '.ax-card h3{margin:0 0 6px;font-size:17px;font-weight:700;color:var(--t)}',
    '.ax-card p{margin:0 0 12px;font-size:14.5px;line-height:1.5;color:var(--m)}',
    '.ax-card p:last-child{margin-bottom:0}',
    '.ax-card .ax-note{margin:10px 0 0;font-size:13.5px}',
    '.ax-dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px;background:var(--m);vertical-align:1px}',
    '.ax-dot.ax-ok{background:#22c55e}',
    '.ax-hidden{display:none!important}',
    '.ax-modal{position:fixed;inset:0;z-index:2147483000;display:flex;align-items:flex-end;justify-content:center;padding:16px;background:rgba(0,0,0,.55)}',
    '@media (min-width:600px){.ax-modal{align-items:center}}',
    '.ax-modal .ax-card{width:100%;max-width:440px;background:var(--ax-modal-bg,var(--ax-surface-solid,#1b1f27));color:var(--ax-modal-text,var(--ax-text,#f2f4f8));box-shadow:0 20px 60px rgba(0,0,0,.45);max-height:85vh;overflow:auto}',
    '.ax-modal h2{margin:0 0 6px;font-size:20px;font-weight:700}',
    '.ax-modal ol{padding-left:22px;margin:8px 0 14px}',
    '.ax-modal li{margin:10px 0;line-height:1.45;font-size:15.5px}',
    '.ax-share{display:inline-block;width:20px!important;height:20px!important;vertical-align:-4px;color:var(--a)}'
  ].join('');

  function injectCSS() {
    if (document.getElementById('ax-style')) return;
    var s = document.createElement('style');
    s.id = 'ax-style';
    s.textContent = CSS;
    (document.head || document.documentElement).appendChild(s);
  }

  function stepsHTML() {
    var n = esc(cfg.name);
    if (IS_IOS && !IS_CHROME_IOS) return '<ol>' +
      '<li>Make sure this page is open in <b>Safari</b>.</li>' +
      '<li>Tap the <b>Share</b> button ' + ICON_SHARE + ' (bottom of the screen, or top on iPad).</li>' +
      '<li>Scroll down and tap <b>Add to Home Screen</b>.</li>' +
      '<li>Tap <b>Add</b>. The ' + n + ' icon appears on your home screen.</li></ol>';
    if (IS_CHROME_IOS) return '<ol>' +
      '<li>Tap the <b>Share</b> button ' + ICON_SHARE + ' in the address bar.</li>' +
      '<li>Tap <b>Add to Home Screen</b>, then <b>Add</b>.</li></ol>';
    if (IS_ANDROID) return '<ol>' +
      '<li>Tap Chrome\'s menu <b>⋮</b> (top right).</li>' +
      '<li>Tap <b>Add to Home screen</b> or <b>Install app</b>.</li>' +
      '<li>Tap <b>Install</b>. The icon appears on your home screen.</li></ol>';
    return '<ol><li>In Chrome or Edge, click the install icon at the right end of the address bar, or open the menu and choose <b>Install ' + n + '</b>.</li>' +
      '<li>On a phone, open this page and use <b>Add to Home Screen</b> from the browser menu.</li></ol>';
  }

  function toast(msg) {
    var t = el('<div class="ax" role="status" style="position:fixed;left:50%;bottom:24px;transform:translateX(-50%);z-index:2147483001;padding:12px 16px;border-radius:12px;background:#111;color:#fff;font-size:14.5px;box-shadow:0 10px 30px rgba(0,0,0,.35)"></div>');
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(function () { t.remove(); }, 4500);
  }

  function openInstallHelp() {
    injectCSS();
    var m = el('<div class="ax ax-modal" role="dialog" aria-modal="true" aria-labelledby="ax-h"><div class="ax-card">' +
      '<h2 id="ax-h">Add to your home screen</h2>' + stepsHTML() +
      '<button type="button" class="ax-btn ax-primary ax-block" data-ax-close>Got it</button></div></div>');
    function close() { m.remove(); document.removeEventListener('keydown', onKey); }
    function onKey(e) { if (e.key === 'Escape') close(); }
    m.addEventListener('click', function (e) { if (e.target === m || e.target.hasAttribute('data-ax-close')) close(); });
    document.addEventListener('keydown', onKey);
    document.body.appendChild(m);
    m.querySelector('[data-ax-close]').focus();
  }

  function install() {
    if (installEvt) {
      var evt = installEvt;
      installEvt = null;
      evt.prompt();
      if (evt.userChoice) evt.userChoice.then(function (r) {
        if (r && r.outcome === 'accepted') toast('Installing… look for the icon on your home screen.');
      }).catch(function () {});
      changed();
      return;
    }
    openInstallHelp();
  }

  function mountBanner(target) {
    var host = resolve(target);
    if (!host) return;
    injectCSS();
    var bar = el('<div class="ax ax-bar ax-hidden" role="region" aria-label="Install app">' + ICON_PHONE +
      '<span>Add ' + esc(cfg.name) + ' to your home screen for one-tap access.</span>' +
      '<button type="button" class="ax-btn ax-primary">Install</button>' +
      '<button type="button" class="ax-x" aria-label="Dismiss">✕</button></div>');
    bar.querySelector('.ax-primary').onclick = install;
    bar.querySelector('.ax-x').onclick = function () { set('installDismissed', true); changed(); };
    function update() {
      // Phones only: on a desktop the card in settings is enough.
      var show = !isInstalled() && !get('installDismissed', false) && (IS_PHONE || !!installEvt);
      bar.classList.toggle('ax-hidden', !show);
    }
    listeners.push(update);
    update();
    host.prepend(bar);
    return bar;
  }

  function mountInstallCard(target, opts) {
    var host = resolve(target);
    if (!host) return;
    injectCSS();
    opts = opts || {};
    var card = el('<section class="ax ax-card"><h3>Install on your phone</h3>' +
      '<p>Status: <span class="ax-dot"></span><b class="ax-state">Not installed</b></p>' +
      '<button type="button" class="ax-btn ax-primary ax-block">' + ICON_PHONE + 'Add to home screen</button>' +
      '<p class="ax-note">' + esc(opts.text || ('Opens full screen like a regular app, with the ' + cfg.name + ' icon.')) + '</p></section>');
    card.querySelector('.ax-btn').onclick = install;
    function update() {
      var inst = isInstalled();
      card.querySelector('.ax-state').textContent = inst ? 'Installed — you\'re using the app' : 'Not installed';
      card.querySelector('.ax-dot').classList.toggle('ax-ok', inst);
      card.querySelector('.ax-btn').classList.toggle('ax-hidden', inst);
    }
    listeners.push(update);
    update();
    host.appendChild(card);
    return card;
  }

  function mountSupport(target, opts) {
    var host = resolve(target);
    if (!host) return;
    injectCSS();
    opts = opts || {};
    var text = opts.text || (cfg.name + ' is free and always will be. If it has helped you, you can chip in toward hosting costs.');
    var card = el('<section class="ax ax-card"><h3>Support this project</h3><p>' + esc(text) + '</p>' +
      '<a class="ax-btn ax-block" target="_blank" rel="noopener noreferrer">' + ICON_HEART + 'Support this project (PayPal)</a></section>');
    card.querySelector('a').href = opts.url || PAYPAL_URL;
    host.appendChild(card);
    return card;
  }

  window.addEventListener('beforeinstallprompt', function (e) { e.preventDefault(); installEvt = e; changed(); });
  window.addEventListener('appinstalled', function () {
    installEvt = null;
    set('installDismissed', true);
    changed();
    toast('Installed! Open ' + cfg.name + ' from your home screen.');
  });

  window.AppExtras = {
    version: 1,
    init: function (o) {
      o = o || {};
      cfg.name = o.name || cfg.name;
      cfg.storageKey = o.storageKey || ('app-extras:' + cfg.name.toLowerCase().replace(/[^a-z0-9]+/g, '-'));
      return window.AppExtras;
    },
    mountBanner: mountBanner,
    mountInstallCard: mountInstallCard,
    mountSupport: mountSupport,
    openInstallHelp: openInstallHelp,
    install: install,
    isInstalled: isInstalled,
    paypalUrl: PAYPAL_URL
  };
})();
