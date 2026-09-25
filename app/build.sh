#!/bin/sh
# Builds the site from app.html + data.js
#   index.html            -> the full web page Vercel serves (open it in any browser too)
#   american-ledger.html  -> the same page without <html>/<head> wrapper, for Claude artifact previews
cd "$(dirname "$0")"
python3 - <<'P'
t = open("app.html").read()
d = open("data.js").read()
body = t.replace('<script src="data.js"></script>', '<script>\n' + d + '</script>')
open("../american-ledger.html", "w").write(body)
head, rest = body.split("</style>", 1)
page = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '<meta name="description" content="Scrub from 1776 to today and watch the national debt, deficits, interest, minimum wage and the states change, with the laws and court rulings that moved them.">\n'
        '<style>:root{color-scheme:light}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n'
        + head + "</style>\n</head>\n<body>\n" + rest + "\n</body>\n</html>\n")
open("../index.html", "w").write(page)
print("wrote index.html and american-ledger.html", len(page)//1024, "KB")
P
