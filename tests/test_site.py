"""Dependency-free checks for deployment content and navigation."""
from html.parser import HTMLParser
from pathlib import Path
import unittest
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'

class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.ids, self.refs, self.headings, self.metas = [], [], [], []
        self.feed(source)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag in ('a', 'link', 'script', 'img'):
            self.refs.append(attrs.get('href', attrs.get('src', '')))
        if tag == 'h1':
            self.headings.append(tag)
        if tag == 'meta':
            self.metas.append(attrs)

class WebsiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (SITE / 'index.html').read_text()
        cls.page = Page(cls.html)
    def test_resume_sections(self):
        for section in ('projects', 'skills', 'experience'):
            self.assertIn(section, self.page.ids)
        self.assertIn('Calvin Nguyen', self.html)
        self.assertIn('British Columbia Institute of Technology', self.html)
    def test_internal_navigation(self):
        for ref in self.page.refs:
            if ref.startswith('#'):
                self.assertIn(ref[1:], self.page.ids, f'Broken navigation: {ref}')
    def test_local_assets(self):
        for ref in self.page.refs:
            parsed = urlsplit(ref)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            asset = (SITE / unquote(parsed.path)).resolve()
            self.assertTrue(asset.is_relative_to(SITE.resolve()))
            self.assertTrue(asset.is_file(), f'Missing asset: {ref}')
    def test_unique_ids_and_heading(self):
        self.assertEqual(len(self.page.ids), len(set(self.page.ids)))
        self.assertEqual(len(self.page.headings), 1)
    def test_mobile_viewport(self):
        self.assertTrue(any(m.get('name') == 'viewport' and 'width=device-width' in m.get('content', '') for m in self.page.metas))
    def test_download_is_pdf(self):
        self.assertTrue((SITE / 'assets/Calvin-Nguyen-Resume.pdf').read_bytes().startswith(b'%PDF-'))
    def test_build_contains_only_website_files(self):
        import subprocess, sys
        subprocess.run([sys.executable, str(ROOT / 'scripts/build.py')], check=True)
        source = {p.relative_to(SITE) for p in SITE.rglob('*') if p.is_file()}
        output = {p.relative_to(ROOT / 'dist') for p in (ROOT / 'dist').rglob('*') if p.is_file()}
        self.assertEqual(source, output)
        for path in source:
            self.assertEqual((SITE / path).read_bytes(), (ROOT / 'dist' / path).read_bytes())

if __name__ == '__main__':
    unittest.main()
