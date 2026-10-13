# Dmitry Glukhov — Open Source & Research

A responsive, bilingual (English / Russian), zero-backend project directory designed for **https://dmitry-dev-pet.github.io/**.

The public portfolio is an **editorially approved selection**, not a mirror of all repositories. The daily build reads public GitHub metadata from `Dmitry-dev-pet` and `Dimkin33` but displays only repositories explicitly listed in `data/curation.json` under `published_repositories`. Related repositories must also be approved. No private project data, tokens, or credentials are copied.

## Publication

The public repository is [Dmitry-dev-pet/dmitry-dev-pet.github.io](https://github.com/Dmitry-dev-pet/dmitry-dev-pet.github.io).

Repository creation and GitHub Pages administration use the reviewed, owner-only
`Dmitry-dev-pet/github-control` operations (`[create-repo]` and `[enable-pages]`).
The static site is deployed from `web/` by `.github/workflows/pages.yml`.

The daily GitHub Actions build reads only public GitHub REST metadata and
rebuilds the manually approved catalog from the two account inventories.
Unapproved public repositories remain absent from cards, related links and search.
Their names are listed for editorial review in the GitHub Actions build log.
No PAT, local Mac runner or external database is required for the site. If GitHub Actions artifact
storage is exhausted, publishing may temporarily fail until storage is
available; repository creation and page configuration are separate steps.

## Preview locally

```bash
python scripts/build_catalog.py --offline
python -m http.server --directory web 8000
```

Open http://localhost:8000/. Network access is only necessary for `python scripts/build_catalog.py` **without** `--offline` and for the published GitHub Actions workflow. The checked-in offline snapshot covers 36 public repositories verified on October 13, 2026. Only 14 explicitly approved repositories are published, grouped into 13 independent projects (including one related Truthrail starter repository).

## Maintain the catalog

Edit **`data/curation.json`**. Public repository status is editorial:

- **Featured** — approved in `published_repositories` and assigned `featured_order` (1–8).
- **Published** — approved in `published_repositories` without featured order.
- **Hidden / pending review** — every other repository, regardless of GitHub visibility. Not included in cards, search, related links or publicly deployed JSON.

For each approved public repository you can set:

- `title_en`, `title_ru`, `summary_en`, `summary_ru` — editorial text;
- `category` — one of `agents`, `science`, `visual`, `tools`, `research`, `experiments`;
- `featured_order` — 1 through 8 for featured projects; omit for non-featured published projects;
- `demo`, `demo_kind` — manually verified demo/video URL, with priority over automatic discovery; otherwise canonical GitHub Pages links are inferred from GitHub's `has_pages` + matching homepage metadata (or canonical owner.github.io path if homepage is empty). Discovery alone is not a live availability guarantee;
- `tags` — short keywords;
- `family` and `primary` — merge **approved** companion repositories into a single project card while preserving related links;
- `published_repositories` — the only names allowed into the public catalog, including approved related repositories;
- `excluded_repositories` — permanent blocklist for legacy projects, even if mistakenly approved;
- `hidden` — additional backward-compatible suppression for any approved repository, normally unnecessary.

**New public repositories are discovered but NEVER auto-published.** Review the candidate names in the latest `Publish open-source portfolio` Actions build log, then deliberately add appropriate entries to `published_repositories` and their editorial metadata through a reviewed PR. Hide educational, obsolete and internal-support repositories by leaving them unapproved; leave their GitHub repositories untouched. To promote a published project, assign `featured_order`. Keep the approval list independent from repository age or last commit date.

## Tests

```bash
python scripts/build_catalog.py --offline
python -m unittest discover -s tests -v
node --check web/app.js
```

## License caveat

A public repository isn't automatically open-source under a recognized license. This directory lists publicly visible projects, but does not presume the licensing rights of each individual repository. Check that repository's LICENSE file before reuse.
