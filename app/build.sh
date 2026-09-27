#!/bin/sh
# Builds the site from app.html + data.js
#   index.html            -> the full web page Vercel serves (open it in any browser too)
#   american-ledger.html  -> the same page without <html>/<head> wrapper, for Claude artifact previews
cd "$(dirname "$0")"
python3 - <<'P'
t = open("app.html").read()
d = open("data.js").read()
body = t.replace('<script src="data.js"></script>', '<script>\n' + d + '</script>')
import sys; sys.path.insert(0, "../data")
import seo
from presidents_data import PRESIDENTS
pres = sorted(PRESIDENTS.items(), key=lambda kv: kv[1]["terms"][0][0])
explore = ('<nav class="explore" aria-label="Explore the site"><div class="about-h">Explore</div>'
           '<p><a href="presidents.html">Every president</a> · <a href="hill.html">The Hill: Congress</a> · <a href="bench.html">The Bench: the Supreme Court</a></p><p class="plist">'
           + " ".join(f'<a href="presidents/{k}.html">{v["name"]}</a>' for k, v in pres) + '</p></nav>')
body = body.replace('<!--EXPLORE-->', explore)
open("../american-ledger.html", "w").write(body)
head, rest = body.split("</style>", 1)
TITLE = "Yeas and Nays: the U.S. debt, laws, presidents and Supreme Court since 1776"
DESC = "Scrub from 1776 to today and watch the national debt, deficits, interest, minimum wage and the states change, with the laws, presidents and Supreme Court rulings that moved them."
page = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '<link rel="icon" type="image/svg+xml" href="assets/yeas-nays-icon.svg">\n'
        '<meta name="description" content="' + DESC + '">\n' + seo.tags(TITLE, DESC, "/", jsonld=[seo.website_ld(DESC)]) + '\n'
        '<meta name="theme-color" content="#0d1311">\n<style>:root{color-scheme:dark;background:#0d1311}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n'
        + head + "</style>\n</head>\n<body>\n" + rest + "\n</body>\n</html>\n")
open("../index.html", "w").write(page)
print("wrote index.html and american-ledger.html", len(page)//1024, "KB")
P
