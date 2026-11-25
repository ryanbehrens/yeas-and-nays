"""Search-engine and social-sharing tags shared by every page.
SITE is the public address; change it here if the site moves to a custom domain, then rebuild."""
import html, json

SITE = "https://yeas-and-nays.vercel.app"
NAME = "Yeas and Nays"
e = lambda s: html.escape(str(s), quote=True)

def url(path):
    # Vercel serves clean URLs (/presidents/lincoln), so canonical links use them
    return SITE + (path if path.startswith("/") else "/" + path)

def tags(title, desc, path, image="/assets/og/site.jpg", kind="website", jsonld=None):
    u = url(path); img = url(image)
    out = [
        f'<link rel="canonical" href="{e(u)}">',
        f'<meta property="og:site_name" content="{NAME}">',
        f'<meta property="og:type" content="{kind}">',
        f'<meta property="og:title" content="{e(title)}">',
        f'<meta property="og:description" content="{e(desc)}">',
        f'<meta property="og:url" content="{e(u)}">',
        f'<meta property="og:image" content="{e(img)}">',
        '<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{e(title)}">',
        f'<meta name="twitter:description" content="{e(desc)}">',
        f'<meta name="twitter:image" content="{e(img)}">',
        '<meta name="robots" content="index, follow, max-image-preview:large">',
        extras(path),
    ]
    for block in (jsonld or []):
        out.append('<script type="application/ld+json">' + json.dumps(block, ensure_ascii=False).replace("</", "<\\/") + "</script>")
    return "\n".join(out)

def extras(path):
    """Install-to-home-screen and support tags (manifest, icon, and the shared
    app-extras script). Paths are relative so pages also work opened from disk."""
    p = "../" * path.strip("/").count("/")
    return "\n".join([
        f'<link rel="manifest" href="{p}manifest.webmanifest">',
        f'<link rel="apple-touch-icon" href="{p}assets/icons/apple-touch-icon.png?v=2">',
        '<meta name="apple-mobile-web-app-title" content="Yeas &amp; Nays">',
        f'<script src="{p}assets/app-extras.js?v=1" defer></script>',
        f'<script src="{p}assets/site-extras.js?v=1" defer></script>',
    ])

def website_ld(desc):
    return {"@context": "https://schema.org", "@type": "WebSite", "name": NAME, "url": SITE + "/", "description": desc, "inLanguage": "en-US"}

def breadcrumbs(*crumbs):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": url(p)} for i, (n, p) in enumerate(crumbs)]}
