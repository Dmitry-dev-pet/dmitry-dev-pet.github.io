import json
from pathlib import Path
import copy
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_catalog import (  # noqa: E402
    build_catalog, discover_github_pages_demo,
    editorial_review_candidates, normalize_repository,
)


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seed = json.loads((ROOT / 'data' / 'repositories-seed.json').read_text(encoding='utf-8'))
        cls.config = json.loads((ROOT / 'data' / 'curation.json').read_text(encoding='utf-8'))
        cls.catalog = build_catalog(cls.seed, cls.config, 'snapshot')

    def test_public_snapshot_count(self):
        self.assertEqual(self.catalog['discovered_repositories'], 36)
        self.assertEqual(self.catalog['total_repositories'], 14)
        self.assertEqual(self.catalog['total_projects'], 13)

    def test_featured_count_is_eight(self):
        featured = [p for p in self.catalog['projects'] if p['featured_order'] > 0]
        self.assertEqual(len(featured), 8)
        self.assertEqual(len({p['featured_order'] for p in featured}), 8)

    def test_grouping_keeps_related_links(self):
        groups = {p['full_name']: p for p in self.catalog['projects']}
        self.assertEqual(groups['Dmitry-dev-pet/truthrail-core']['related'][0]['full_name'], 'Dmitry-dev-pet/truthrail-starter')
        self.assertEqual(groups['Dmitry-dev-pet/apatch-blender']['related'], [])
        self.assertIn('Dmitry-dev-pet/time-receiver', groups)

    def test_each_included_repository_reachable_from_catalog_or_marked_hidden(self):
        all_names = {r['full_name'] for r in self.seed}
        catalog_names = set()
        for project in self.catalog['projects']:
            catalog_names.add(project['full_name'])
            catalog_names.update(p['full_name'] for p in project['related'])
        self.assertEqual(set(self.config['published_repositories']), catalog_names)
        self.assertTrue(catalog_names.issubset(all_names))

    def test_private_repositories_not_published(self):
        malicious = {'full_name': 'Dimkin33/private-prototype', 'private': True}
        result = build_catalog(self.seed + [malicious], self.config, 'snapshot')
        self.assertEqual(result['total_repositories'], 14)

    def test_legacy_repositories_are_entirely_absent(self):
        all_listed = set()
        for project in self.catalog['projects']:
            all_listed.add(project['full_name'])
            all_listed.update(link['full_name'] for link in project['related'])
        self.assertTrue(set(self.config['excluded_repositories']).isdisjoint(all_listed))
        self.assertNotIn('Dimkin33/Currency_Exchange', all_listed)
        self.assertNotIn('Dimkin33/tennis_scoreboard', all_listed)
        self.assertNotIn('Dmitry-dev-pet/cloud-file-storage', all_listed)
        self.assertNotIn('Dmitry-dev-pet/viselitsa-web', all_listed)
        self.assertNotIn('Dmitry-dev-pet/star_elite', all_listed)

    def test_excluded_repository_cannot_reappear_on_next_sync(self):
        # Simulate GitHub returning the legacy repository again in the next build.
        resurrected = {'full_name': 'Dimkin33/Simulation2', 'private': False}
        result = build_catalog(self.seed + [resurrected], self.config, 'github')
        included = {p['full_name'] for p in result['projects']}
        self.assertNotIn(resurrected['full_name'], included)
        self.assertEqual(result['total_repositories'], 14)

    def test_exclusion_is_case_insensitive(self):
        result = build_catalog(
            [{'full_name': 'dimkin33/feohxyz', 'private': False}],
            self.config,
            'github',
        )
        self.assertEqual(result['total_repositories'], 0)
        self.assertEqual(result['projects'], [])

    def test_sanitized_urls(self):
        repo = normalize_repository({'full_name': 'Dimkin33/Docling_Colab', 'url': 'https://attacker.example/steal'})
        self.assertEqual(repo['url'], 'https://github.com/Dimkin33/Docling_Colab')

    def test_no_licenses_are_assumed(self):
        repo = normalize_repository({'full_name': 'Dimkin33/example'})
        self.assertFalse(repo['license'])

    def test_portfolio_itself_is_not_a_project(self):
        own = {'full_name': 'Dmitry-dev-pet/dmitry-dev-pet.github.io', 'private': False}
        result = build_catalog(self.seed + [own], self.config, 'github')
        self.assertEqual(result['discovered_repositories'], 37)
        self.assertEqual(result['total_repositories'], 14)
        self.assertNotIn(own['full_name'], [p['full_name'] for p in result['projects']])

    def test_new_public_repository_requires_editorial_approval(self):
        new = {'full_name': 'Dimkin33/a-new-open-project', 'private': False}
        result = build_catalog(self.seed + [new], self.config, 'github')
        self.assertEqual(result['discovered_repositories'], 37)
        self.assertEqual(result['total_repositories'], 14)
        self.assertNotIn(new['full_name'], [p['full_name'] for p in result['projects']])
        self.assertIn(new['full_name'], editorial_review_candidates(self.seed + [new], self.config))

    def test_editor_approval_enables_new_project(self):
        new = {'full_name': 'Dimkin33/a-new-open-project', 'private': False}
        approved = copy.deepcopy(self.config)
        approved['published_repositories'].append(new['full_name'])
        result = build_catalog(self.seed + [new], approved, 'github')
        self.assertEqual(result['total_repositories'], 15)
        self.assertEqual(result['total_projects'], 14)
        self.assertIn(new['full_name'], [p['full_name'] for p in result['projects']])

    def test_new_private_repository_never_enters_review_queue(self):
        new = {'full_name': 'Dimkin33/new-private', 'private': True}
        self.assertNotIn(new['full_name'], editorial_review_candidates(self.seed + [new], self.config))

    def test_github_pages_auto_detected_for_approved_projects(self):
        projects = {p['full_name']: p for p in self.catalog['projects']}
        base = 'https://dmitry-dev-pet.github.io/'
        for name in ('feynman-reader', 'hotwills', 'form-field-lab'):
            project = projects[f'Dmitry-dev-pet/{name}']
            with self.subTest(project=name):
                self.assertEqual(project['demo'], f'{base}{name}/')
                self.assertEqual(project['demo_source'], 'github_pages')

    def test_curated_demo_takes_priority_over_discovery(self):
        project = next(p for p in self.catalog['projects'] if p['name'] == 'time-receiver')
        self.assertEqual(project['demo'], 'https://dmitry-dev-pet.github.io/time-receiver/')
        self.assertEqual(project['demo_source'], 'curated')
        self.assertEqual(project['category'], 'research')
        self.assertEqual(project['featured_order'], 7)

    def test_pages_discovery_rejects_unrelated_or_insecure_homepages(self):
        for homepage in (
            'http://dmitry-dev-pet.github.io/hotwills/',
            'https://attacker.invalid/hotwills/',
            'https://dmitry-dev-pet.github.io/other-repo/',
            'https://dmitry-dev-pet.github.io:8443/hotwills/',
        ):
            with self.subTest(homepage=homepage):
                repo = {'full_name': 'Dmitry-dev-pet/hotwills', 'has_pages': True, 'homepage': homepage}
                self.assertEqual(discover_github_pages_demo(repo), '')
        self.assertEqual(
            discover_github_pages_demo({'full_name': 'Dmitry-dev-pet/hotwills', 'has_pages': False}),
            '',
        )
        self.assertEqual(
            discover_github_pages_demo({'full_name': 'Dmitry-dev-pet/hotwills', 'has_pages': True}),
            'https://dmitry-dev-pet.github.io/hotwills/',
        )

    def test_only_eight_editorial_features(self):
        projects = {p['full_name']: p for p in self.catalog['projects']}
        self.assertEqual(projects['Dmitry-dev-pet/time-receiver']['featured_order'], 7)
        self.assertEqual(projects['Dmitry-dev-pet/form-field-lab']['featured_order'], 0)


if __name__ == '__main__':
    unittest.main()
