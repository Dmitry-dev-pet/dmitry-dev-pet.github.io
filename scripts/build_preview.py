#!/usr/bin/env python3
"""Generate a standalone HTML preview of the current catalog (no web server required)."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / 'web'
html = (WEB / 'index.html').read_text(encoding='utf-8')
css = (WEB / 'styles.css').read_text(encoding='utf-8')
js = (WEB / 'app.js').read_text(encoding='utf-8')
data = json.loads((WEB / 'data' / 'catalog.json').read_text(encoding='utf-8'))
data_literal = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
html = html.replace('<link rel="stylesheet" href="./styles.css">', f'<style>{css}</style>')
html = html.replace('  <script src="./app.js" defer></script>\n', '')
inline = f'''  <script>
  const offlinePortfolioData = {data_literal};
  const originalFetch = window.fetch;
  window.fetch = (url, options) => String(url).includes('data/catalog.json')
    ? Promise.resolve({{ok: true, json: () => Promise.resolve(offlinePortfolioData)}})
    : originalFetch(url, options);
  </script>
  <script>{js}</script>
'''
html = html.replace('</body>', inline + '</body>')
output = ROOT.parent / 'portfolio-preview.html'
output.write_text(html, encoding='utf-8')
print('Wrote', output, 'bytes:', output.stat().st_size)
