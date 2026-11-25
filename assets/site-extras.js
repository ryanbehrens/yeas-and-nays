// Puts the shared install + support UI (assets/app-extras.js) on every page:
// the "Add to home screen" bar at the top, and the install + PayPal cards just
// above the footer. Also registers the service worker (sw.js).
(function () {
  var ax = window.AppExtras;
  if (!ax) return;
  ax.init({ name: 'Yeas and Nays', storageKey: 'yeas-nays-app-extras' });

  var style = document.createElement('style');
  style.textContent =
    ':root{--ax-accent:var(--accent);--ax-accent-ink:#fff;--ax-surface:var(--surface);--ax-surface-2:var(--surface-2);' +
    '--ax-text:var(--ink);--ax-muted:var(--muted);--ax-line:var(--line);--ax-radius:10px;--ax-font:var(--sans);--ax-modal-bg:var(--surface)}' +
    '.yn-extras{display:grid;gap:12px;margin:28px 0 8px}' +
    '@media (min-width:720px){.yn-extras{grid-template-columns:1fr 1fr}}' +
    '.yn-banner{padding:12px 16px 0}';
  document.head.appendChild(style);

  function ready(fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }

  ready(function () {
    var banner = document.createElement('div');
    banner.className = 'yn-banner';
    document.body.prepend(banner);
    ax.mountBanner(banner);

    var footer = document.querySelector('footer');
    var cards = document.createElement('div');
    cards.className = 'yn-extras';
    if (footer) footer.parentNode.insertBefore(cards, footer);
    else document.body.appendChild(cards);
    ax.mountInstallCard(cards, { text: 'Opens full screen like a regular app, with the Yeas and Nays icon. Pages you have viewed open even without a signal.' });
    ax.mountSupport(cards, { text: 'Yeas and Nays is free, ad-free and always will be. If it has helped you understand how we got here, you can chip in toward hosting and data costs.' });
  });

  if ('serviceWorker' in navigator && location.protocol === 'https:') {
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('/sw.js').catch(function () {});
    });
  }
})();
