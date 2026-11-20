# Wagon Watch collector upgrade

Upload these files to the same paths on `main`:
- `app.js` (replace existing)
- `scripts/update.py` (replace existing)
- `scripts/collect_pages.py` (new)
- `data/sources.json` (new)
- `.github/workflows/update.yml` (replace existing)

**Do not replace `data/listings.json`**: that contains your current listings.

## Current status
The site adds GeoffTrader search links immediately. The scheduled job checks RSS feeds configured in `data/feeds.json` and explicitly approved public-page sources configured in `data/sources.json`. Both source lists start empty, so there is **no live automatic marketplace scraping** until a permitted source is configured.

For a site which explicitly permits automated access, add a source with `name`, `search_url`, `listing_path_contains`, `permission_confirmed: true`, `enabled: true`. Do not mark permission confirmed without checking the site terms and applicable usage rights. Robots.txt must also allow the page. No restricted sites or access-control bypasses.

Go to GitHub Actions → Update permitted feeds → Run workflow to test. Inspect the run logs and `data/listings.json` for new discoveries. GitHub Actions runs approximately every six hours, not at guaranteed times.
