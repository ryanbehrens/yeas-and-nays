# Yeas & Nays

*How America got here, one vote at a time.*

**The Ledger**, the first section, is an interactive timeline of U.S. history from 1776 to today: national debt, deficits, interest,
debt-to-GDP, the minimum wage, presidential elections by state, and the landmark laws and
Supreme Court rulings that moved the numbers.

## How it's built
- `index.html` is the finished site. It's a single static page; Vercel serves it as-is (no build step).
- `app/app.html` is the page source (layout, styles, and code).
- `data/` holds the data and the scripts that turn it into `app/data.js`:
  - `data/political.py` presidents, Congress, elections, statehood, minimum wage
  - `data/laws.py` landmark laws, court rulings and events
  - `data/raw/` downloaded source data (Treasury, OMB/FRED, MeasuringWorth, DOL, 270toWin, Vaghul & Zipperer)

## Rebuilding
```
python3 data/build.py   # regenerates app/data.js from the data files
sh app/build.sh         # combines app.html + data.js into index.html
```

## Deploying
The GitHub repository is connected to Vercel. Every push to `main` deploys to the live site;
pushes to other branches get their own preview link.
