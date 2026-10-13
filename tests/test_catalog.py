import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_catalog import build_catalog, normalize_repository  # noqa: E402


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seed = json.loads((ROOT / 'data' / 'repositories-seed.json').read_text(encoding='utf-8'))
        cls.config = json.loads((ROOT / 'data' / 'curation.json').read_text(encoding='utf-8'))
        cls.catalog = build_catalog(cls.seed, cls.config, 'snapshot')

    def test_public_snapshot_count(self):
        self.assertEqual(self.catalog['total_repositories'], 36)
        self.assertEqual(self.catalog['total_projects'], 32)

    def test_featured_count_is_eight(self):
        featured = [p for p in self.catalog['projects'] if p['featured_order'] > 0]
        self.assertEqual(len(featured), 8)
        self.assertEqual(len({p['featured_order'] for p in featured}), 8)

    def test_grouping_keeps_related_links(self):
        groups = {p['full_name']: p for p in self.catalog['projects']}
        self.assertEqual(groups['Dmitry-dev-pet/truthrail-core']['related'][0]['full_name'], 'Dmitry-dev-pet/truthrail-starter')
        self.assertEqual(groups['Dimkin33/Currency_Exchange']['related'][0]['full_name'], 'Dimkin33/currency-exchange-frontend')

    def test_each_repository_reachable_from_catalog_or_marked_hidden(self):
        all_names = {r['full_name'] for r in self.seed}
        catalog_names = set()
        for project in self.catalog['projects']:
            catalog_names.add(project['full_name'])
            catalog_names.update(p['full_name'] for p in project['related'])
        self.assertEqual(all_names, catalog_names)

    def test_private_repositories_not_published(self):
        malicious = {'full_name': 'Dimkin33/private-prototype', 'private': True}
        result = build_catalog(self.seed + [malicious], self.config, 'snapshot')
        self.assertEqual(result['total_repositories'], 36)

    def test_sanitized_urls(self):
        repo = normalize_repository({'full_name': 'Dimkin33/Docling_Colab', 'url': 'https://attacker.example/steal'})
        self.assertEqual(repo['url'], 'https://github.com/Dimkin33/Docling_Colab')

    def test_no_licenses_are_assumed(self):
        repo = normalize_repository({'full_name': 'Dimkin33/example'})
        self.assertFalse(repo['license'])

    def test_portfolio_itself_is_not_a_project(self):
        own = {'full_name': 'Dmitry-dev-pet/dmitry-dev-pet.github.io', 'private': False}
        result = build_catalog(self.seed + [own], self.config, 'github')
        self.assertEqual(result['total_repositories'], 37)
        self.assertNotIn(own['full_name'], [p['full_name'] for p in result['projects']])

    def test_new_public_repository_is_auto_discovered(self):
        new = {'full_name': 'Dimkin33/a-new-open-project', 'private': False}
        result = build_catalog(self.seed + [new], self.config, 'github')
        self.assertEqual(result['total_repositories'], 37)
        self.assertIn('Dimkin33/a-new-open-project', [p['full_name'] for p in result['projects']])


if __name__ == '__main__':
    unittest.main()
