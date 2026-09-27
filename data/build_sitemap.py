"""Writes sitemap.xml and robots.txt for search engines. Run after the other build scripts:
python3 data/build_sitemap.py"""
import os, sys, datetime as dt
sys.path.insert(0, os.path.dirname(__file__))
import seo
from presidents_data import PRESIDENTS
ROOT = os.path.join(os.path.dirname(__file__), "..")
today = dt.date.today().isoformat()
pages = [("/", "1.0"), ("/presidents", "0.9"), ("/hill", "0.9"), ("/bench", "0.9")] + [(f"/presidents/{k}", "0.7") for k in PRESIDENTS]
xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
xml += [f"  <url><loc>{seo.url(p)}</loc><lastmod>{today}</lastmod><priority>{pr}</priority></url>" for p, pr in pages]
xml.append("</urlset>")
open(os.path.join(ROOT, "sitemap.xml"), "w").write("\n".join(xml) + "\n")
open(os.path.join(ROOT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nDisallow: /data/\nDisallow: /app/\n\nSitemap: {seo.SITE}/sitemap.xml\n")
print("wrote sitemap.xml with", len(pages), "pages and robots.txt")
