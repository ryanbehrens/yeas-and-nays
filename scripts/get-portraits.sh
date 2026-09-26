#!/bin/sh
# Downloads every official presidential portrait (Library of Congress, public domain)
# into ./portraits-to-crop/, already named the way the site expects.
# Crop each one to a 4:5 portrait if you like, then move it into assets/presidents/.
# Run from the project folder:  sh scripts/get-portraits.sh
BASE="https://www.loc.gov/static/portals/free-to-use/public-domain/presidential-portraits"
OUT="portraits-to-crop"; mkdir -p "$OUT"
ok=0; fail=""
while read slug file; do
  [ -z "$slug" ] && continue
  if [ -f "assets/presidents/$slug.jpg" ]; then echo "  have   $slug (already on the site)"; continue; fi
  ext="${file##*.}"
  if curl -fsSL -A "Mozilla/5.0" "$BASE/$file" -o "$OUT/$slug.$ext"; then
    if [ "$ext" != "jpg" ]; then  # the site uses .jpg; convert with the Mac's built-in sips
      sips -s format jpeg "$OUT/$slug.$ext" --out "$OUT/$slug.jpg" >/dev/null 2>&1 && rm -f "$OUT/$slug.$ext"
    fi
    echo "  got    $slug"; ok=$((ok+1))
  else rm -f "$OUT/$slug.$ext"; echo "  MISSING $slug"; fail="$fail $slug"; fi
done <<'LIST'
washington 01-washington.jpg
jadams 02-adams.jpg
jefferson 03-jefferson.jpg
madison 04-madison.jpg
monroe 05-monroe.jpg
jqadams 06-adams.jpg
jackson 07-jackson.jpg
vanburen 08-van-buren.jpg
whharrison 09-harrison.jpg
tyler 10-tyler.jpg
polk 11-polk.jpg
taylor 12-taylor.jpg
fillmore 13-fillmore.jpg
pierce 14-pierce.jpg
buchanan 15-buchanan.jpg
lincoln 16-lincoln.jpg
ajohnson 17-johnson.jpg
grant 18-grant.jpg
hayes 19-hayes.jpg
garfield 20-garfield.jpg
arthur 21-arthur.jpg
cleveland 22-24-cleveland.jpg
bharrison 23-harrison.jpg
mckinley 25-mckinley.jpg
troosevelt 26-roosevelt.jpg
taft 27-taft.jpg
wilson 28-wilson.jpg
harding 29-harding.jpg
coolidge 30-coolidge.jpg
hoover 31-hoover.jpg
fdr 32-roosevelt.jpg
truman 33-truman.jpg
eisenhower 34-eisenhower.jpg
jfk 35-kennedy.jpg
lbj 36-johnson.jpg
nixon 37-nixon.jpg
ford 38-ford.jpg
carter 39-carter.jpg
reagan 40-reagan.jpg
ghwbush 41-bush.jpg
clinton 42-clinton.jpg
gwbush 43-bush.jpg
obama 44-obama.jpg
trump 47-donald-trump.jpg
biden 46-joe-biden.png
LIST
echo ""; echo "Downloaded $ok portraits into $OUT/"
[ -n "$fail" ] && echo "Not found:$fail  (save these by hand as $OUT/<name>.jpg)"
open "$OUT" 2>/dev/null || true
