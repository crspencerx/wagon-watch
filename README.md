# Wagon Watch

Mobile-first static site for finding interesting old UK estates and durable survivors.

## Publish to GitHub Pages (no server)

1. Create a **public** GitHub repository named `wagon-watch` (do not tick README; this ZIP includes one).
2. On the repository page choose **Add file → Upload files**. Upload **the contents of this folder**, preserving the `.github/workflows/update.yml` path. GitHub's browser uploader can accept a dragged folder on desktop; alternatively use GitHub Desktop or the command line for reliable nested-folder uploads. **Do not upload the ZIP as one file.**
3. Commit to `main`.
4. Open **Settings → Pages**. Under **Build and deployment**, choose **Deploy from a branch**, branch **main**, folder **/(root)**, then **Save**.
5. Wait a few minutes, then visit `https://YOUR-USERNAME.github.io/wagon-watch/`.
6. In **Actions**, enable workflows if GitHub asks. The workflow runs every six hours and can be run manually using **Update permitted feeds → Run workflow**.

## IMPORTANT: What updates automatically?

The initial database contains **clearly labelled fictional demonstration cards**. The marketplace radar uses external searches, not live imported inventory. By default `data/feeds.json` has no feeds, so the scheduled job **does not discover real adverts**. This is intentional: Auto Trader and other marketplaces may restrict extraction.

For a legitimate RSS/Atom feed that explicitly permits automated use, add an object to `data/feeds.json`:

```json
{"feeds":[{"name":"Example approved feed","url":"https://example.org/approved-listings.xml","permission_confirmed":true}]}
```

The importer reads titles and URLs, identifies estate keywords, deduplicates by URL, and adds new discoveries. It does **not** verify prices, mileage, car condition or listing availability. Only use feeds you have permission to consume. Avoid putting API keys in public repository files. If an authorised source needs secrets, use GitHub Actions secrets and extend the collector.

## Add a real advert manually

Edit `data/listings.json`, insert a new listing object with a unique `id`, `demo:false`, a real `https://` advert `url`, and accurate fields. Use `score:null` unless you have assigned a score based on model/engine research. Do not copy copyrighted listing photos without permission. Commit to `main`; Pages will republish.

## Local test

Run `python3 -m http.server 8000` from this folder, then open `http://localhost:8000`.

## Technical notes

Plain HTML/CSS/JS, no build step, no paid hosting. The scheduled workflow commits only if new records are found. GitHub schedules can be delayed or paused on inactive public repos. Public GitHub Pages sites are not private. Future improvements: approved source integrations, saved favourites (localStorage), genuine MOT API integration, verified scoring and expired listing handling.
