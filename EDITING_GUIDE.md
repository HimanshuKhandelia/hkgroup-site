# HK Group website — editing guide

The website is intentionally static: no WordPress database, plugins or server-side maintenance.

## 1. Add research news

1. Copy `_templates/news-template.qmd` into a new folder under `news/`, e.g. `news/2026-10-new-paper/index.qmd`.
2. Change the title, date, description and text.
3. Commit/push. GitHub Pages rebuilds automatically.

The home page automatically displays the three newest news posts.

## 2. Add a simulation movie

1. Put an MP4 in `media/simulations/`. Keep web movies reasonably compressed; for very large movies use YouTube/Zenodo and embed/link them instead.
2. Copy `_templates/simulation-template.qmd` into a new folder under `simulations/`.
3. Change the title, description and MP4 filename.
4. Commit/push.

## 3. Add or move a group member

Edit `members/present.qmd` and `members/past.qmd`. If someone joins or leaves, also add a short News post if desired.

## 4. Publications

No routine editing is required. `scripts/fetch_pubmed.py` refreshes the PubMed list at every site build and once a week through GitHub Actions.

## 5. Open positions

Edit `open-positions.qmd`. When a position closes, replace the advertisement with a short "No current vacancies" message rather than deleting the page.

## Preview locally

Install Quarto, open this folder and run:

    quarto preview

## Custom SDU domain

Once SDU points `hkgroup.sdu.dk` to GitHub Pages, copy `CNAME.example` to `CNAME` and add `CNAME` under `project.resources` in `_quarto.yml`, or configure the custom domain in the repository Pages settings.
