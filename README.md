# Dmitry Glukhov — Open Source & Research

A responsive, bilingual (English / Russian), zero-backend project directory designed for **https://dmitry-dev-pet.github.io/**.

The public catalog is generated from the two GitHub accounts `Dmitry-dev-pet` and `Dimkin33`. It covers public repositories only, groups related repositories into projects, and maintains editorial descriptions of featured work. It does not copy private project data or store API credentials.

## Publication

The public repository is [Dmitry-dev-pet/dmitry-dev-pet.github.io](https://github.com/Dmitry-dev-pet/dmitry-dev-pet.github.io).

Repository creation and GitHub Pages administration use the reviewed, owner-only
`Dmitry-dev-pet/github-control` operations (`[create-repo]` and `[enable-pages]`).
The static site is deployed from `web/` by `.github/workflows/pages.yml`.

The daily GitHub Actions build reads only public GitHub REST metadata and
rebuilds the catalog from the two account inventories. No PAT, local Mac runner
or external database is required for the site. If GitHub Actions artifact
storage is exhausted, publishing may temporarily fail until storage is
available; repository creation and page configuration are separate steps.

## Preview locally

```bash
python scripts/build_catalog.py --offline
python -m http.server --directory web 8000
```

Open http://localhost:8000/. Network access is only necessary for `python scripts/build_catalog.py` **without** `--offline` and for the published GitHub Actions workflow. The checked-in offline snapshot covers 36 public repositories verified on October 13, 2026. Editorially excluded legacy repositories do not appear on the public site; the current curated snapshot contains 25 included repositories grouped into 23 project families.

## Maintain the catalog

Edit **`data/curation.json`**. For each public repository you can set:

- `title_en`, `title_ru`, `summary_en`, `summary_ru` — editorial text;
- `category` — one of `agents`, `science`, `visual`, `tools`, `research`, `experiments`;
- `featured_order` — 1 through 8 for featured projects;
- `demo`, `demo_kind` — verified public demo URL or video URL;
- `tags` — short keywords;
- `family` and `primary` — merge companion repositories into a single project card while preserving related links;
- `support` — put test fixtures and supporting infrastructure behind the extra toggle;
- `hidden` — omit a standalone profile or CV repo from the project cards (it remains in the GitHub source snapshot).
- `excluded_repositories` — top-level list of legacy repository names that must **never** appear in public cards, related links or search (even with the supporting-repository toggle). The repos stay on GitHub; this filter is applied before grouping on every scheduled refresh.

**New public repositories appear automatically** under the default `experiments` category during the next scheduled build, even without a curation entry. To promote one, add its metadata and set `featured_order`. Keep the full registry under GitHub ownership; do not publish private projects by accident.

## Tests

```bash
python scripts/build_catalog.py --offline
python -m unittest discover -s tests -v
node --check web/app.js
```

## License caveat

A public repository isn't automatically open-source under a recognized license. This directory lists publicly visible projects, but does not presume the licensing rights of each individual repository. Check that repository's LICENSE file before reuse.
