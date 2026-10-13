#!/usr/bin/env python3
"""Build a public, static project catalog from two GitHub accounts.

No third-party dependencies. No private-repository endpoints and no credential files.
The optional GITHUB_TOKEN is read only by CI to avoid low public API rate limits.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CURATION = ROOT / 'data' / 'curation.json'
SEED = ROOT / 'data' / 'repositories-seed.json'
OUTPUT = ROOT / 'web' / 'data' / 'catalog.json'
PER_PAGE = 100


def read_json(path: Path):
    with path.open('r', encoding='utf-8') as handle:
        return json.load(handle)


def fetch_public_repositories(owner: str, token: str = '') -> list[dict]:
    """Fetch only public owner repositories from GitHub's official REST API."""
    repos: list[dict] = []
    page = 1
    while True:
        qs = urlencode({'per_page': PER_PAGE, 'page': page, 'type': 'owner'})
        url = f'https://api.github.com/users/{owner}/repos?{qs}'
        headers = {
            'Accept': 'application/vnd.github+json',
            'User-Agent': 'dmitry-dev-pet-open-source-portfolio',
            'X-GitHub-Api-Version': '2022-11-28',
        }
        if token:
            headers['Authorization'] = f'Bearer {token}'
        request = Request(url, headers=headers)
        with urlopen(request, timeout=20) as response:
            batch = json.load(response)
        if not isinstance(batch, list):
            raise ValueError(f'Unexpected GitHub response for {owner}: not a list')
        for repo in batch:
            if repo.get('private') or repo.get('visibility', 'public') != 'public':
                continue
            if repo.get('owner', {}).get('login', '').lower() != owner.lower():
                continue
            repos.append(repo)
        if len(batch) < PER_PAGE:
            break
        page += 1
        if page > 30:
            raise RuntimeError(f'Unexpected pagination depth for {owner}')
    return repos


def normalize_repository(repo: dict) -> dict:
    full_name = repo['full_name']
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', full_name):
        raise ValueError(f'Invalid repository identifier {full_name!r}')
    license_value = repo.get('license')
    license_spdx = license_value.get('spdx_id') if isinstance(license_value, dict) else None
    return {
        'full_name': full_name,
        'name': full_name.split('/')[1],
        'url': f'https://github.com/{full_name}',
        'description': repo.get('description') or '',
        'language': repo.get('language') or '',
        'topics': repo.get('topics') or [],
        'license': license_spdx if license_spdx and license_spdx != 'NOASSERTION' else '',
        'fork': bool(repo.get('fork', False)),
        'archived': bool(repo.get('archived', False)),
        'pushed_at': repo.get('pushed_at') or '',
        'stars': int(repo.get('stargazers_count') or 0),
    }

def discover_github_pages_demo(repo: dict) -> str:
    """Return a conservative GitHub Pages URL for a public repository.

    GitHub's has_pages flag is the discovery signal. Only the canonical
    owner.github.io/repository/ path is inferred. Custom domains or unrelated
    homepage URLs need an explicit, manually reviewed 'demo' entry.
    This is a link candidate, not a live HTTP availability assertion.
    """
    if not repo.get('has_pages'):
        return ''
    full_name = repo.get('full_name') or ''
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', full_name):
        return ''
    owner, name = full_name.split('/', 1)
    host = f'{owner.lower()}.github.io'
    homepage = str(repo.get('homepage') or '').strip()
    if homepage:
        try:
            parsed = urlsplit(homepage)
            if (
                parsed.scheme.lower() != 'https'
                or parsed.hostname != host
                or parsed.username or parsed.password or parsed.port is not None
                or parsed.path.rstrip('/').casefold() != f'/{name}'.casefold()
            ):
                return ''
        except ValueError:
            return ''
    return f'https://{host}/{name}/'


def editorial_review_candidates(repos: list[dict], config: dict) -> list[str]:
    """Unlisted PUBLIC repos for the build log, never the deployed catalog."""
    owners = {owner.casefold() for owner in config['owners']}
    published = {name.casefold() for name in config['published_repositories']}
    excluded = {name.casefold() for name in config.get('excluded_repositories', [])}
    own = config.get('site_repository', '').casefold()
    return sorted({
        repo['full_name'] for repo in repos
        if not repo.get('private')
        and repo['full_name'].split('/')[0].casefold() in owners
        and repo['full_name'].casefold() not in published
        and repo['full_name'].casefold() not in excluded
        and repo['full_name'].casefold() != own
    }, key=str.casefold)


def build_catalog(repos: list[dict], config: dict, source: str) -> dict:
    owners = {owner.lower() for owner in config['owners']}
    metadata = config['projects']
    own_site = config.get('site_repository', '').casefold()
    # Opt-in only: public GitHub repos never appear until explicitly approved.
    published = {name.casefold() for name in config['published_repositories']}
    # Explicit editorial exclusions are applied before family grouping, so an
    # excluded legacy repository cannot leak into cards or related links.
    exclusions = {name.casefold() for name in config.get('excluded_repositories', [])}
    groups: dict[str, list[dict]] = {}
    seen: set[str] = set()
    for raw in repos:
        full_name = raw['full_name']
        if full_name.casefold() in seen:
            continue
        if full_name.split('/')[0].lower() not in owners or raw.get('private'):
            continue
        seen.add(full_name.casefold())
        if full_name.casefold() == own_site:
            continue  # the portfolio itself is not a portfolio project
        if full_name.casefold() in exclusions:
            continue  # curated legacy exclusion persists across API refreshes
        if full_name.casefold() not in published:
            continue  # unapproved repo; never include it in public site JSON
        current = normalize_repository(raw)
        curated = metadata.get(full_name, {})
        current.update({k: v for k, v in curated.items() if k != 'family'})
        if current.get('demo'):
            current['demo_source'] = 'curated'
        else:
            discovered_demo = discover_github_pages_demo(raw)
            if discovered_demo:
                current['demo'] = discovered_demo
                current['demo_source'] = 'github_pages'
        group = curated.get('family') or full_name
        groups.setdefault(group, []).append(current)

    projects = []
    for group, entries in groups.items():
        preferred = [r for r in entries if r.get('primary')]
        canonical = preferred[0] if preferred else sorted(entries, key=lambda r: r['full_name'].lower())[0]
        project = dict(canonical)
        project['related'] = [
            {'full_name': item['full_name'], 'url': item['url'], 'archived': item['archived']}
            for item in entries if item is not canonical
        ]
        project['category'] = project.get('category', 'experiments')
        project['featured_order'] = int(project.get('featured_order') or 0)
        project['support'] = bool(project.get('support', False))
        project['hidden'] = bool(project.get('hidden', False))
        project['tags'] = list(project.get('tags') or [project['language'], *project['topics']])[:5]
        projects.append(project)

    projects.sort(key=lambda p: (
        bool(p['support'] or p['archived']),
        p['featured_order'] == 0,
        p['featured_order'] if p['featured_order'] > 0 else 999,
        (p.get('title_en') or p['name']).casefold(),
    ))
    return {
        'schema_version': 1,
        'generated_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'sync_source': source,
        'owners': config['owners'],
        'discovered_repositories': len(seen),
        'total_repositories': sum(len(entries) for entries in groups.values()),
        'total_projects': len(projects),
        'projects': projects,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--offline', action='store_true', help='Use checked-in public repository snapshot; no network')
    parser.add_argument('--output', type=Path, default=OUTPUT)
    args = parser.parse_args(argv)
    config = read_json(CURATION)
    seed = read_json(SEED)
    if args.offline:
        repos, source = seed, 'snapshot'
    else:
        try:
            token = os.environ.get('GITHUB_TOKEN', '')
            repos = []
            for owner in config['owners']:
                found = fetch_public_repositories(owner, token)
                print(f'{owner}: {len(found)} public repositories')
                repos.extend(found)
            if not repos:
                raise RuntimeError('Empty GitHub API result')
            source = 'github'
        except (HTTPError, URLError, TimeoutError, ValueError, RuntimeError) as exc:
            print(f'WARNING: GitHub refresh failed; using checked-in public snapshot: {exc}', file=sys.stderr)
            repos, source = seed, 'snapshot'
    catalog = build_catalog(repos, config, source)
    candidates = editorial_review_candidates(repos, config)
    if candidates:
        print(f'Editorial review: {len(candidates)} public repositories are unlisted')
        for name in candidates:
            print(f'  review candidate: {name}')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Wrote {args.output}: {catalog["total_repositories"]} repositories, {catalog["total_projects"]} project groups, source={source}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
