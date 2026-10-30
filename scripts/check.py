#!/usr/bin/env python3
"""Check built local links, source fidelity, the skill download, and personal-information hygiene without external access."""
import argparse
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / 'skills/right-shape'
SKILL_FILES = ('SKILL.md', 'references/rubric.md', 'references/audit.md', 'scripts/validate_placement.py', 'scripts/validate_audit.py', 'LICENSE')
TEXT_SUFFIXES = {'.md', '.json', '.yaml', '.yml', '.html', '.css', '.js', '.py', '.svg', '.txt', ''}
# Personal information must never ship: email addresses, phone numbers, street addresses,
# or anything that looks like a credential. Fictional examples use no real names.
PII_PATTERNS = {
    'email address': re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,}'),
    'phone number': re.compile(r'(?<!\d)(?:\+?1[ .-]?)?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?!\d)'),
    'street address': re.compile(r'\b\d{1,5} [A-Z][a-z]+ (?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd)\b'),
    'credential': re.compile(r'(?i)(?:api[_-]?key|secret|token|password)\s*[:=]\s*["\']?[A-Za-z0-9_\-]{12,}'),
}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.references = []
        self.downloads = []
        self.duplicates = []
        self.textarea = False
        self.skill = ''
        self.h1s = 0
        self.lang = None
        self.examples = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'html':
            self.lang = attrs.get('lang')
        if tag == 'h1':
            self.h1s += 1
        if 'id' in attrs:
            identifier = attrs['id']
            if identifier in self.ids:
                self.duplicates.append(identifier)
            self.ids.add(identifier)
        if 'data-example' in attrs:
            self.examples.append((attrs['data-example'], 'hidden' in attrs))
        for key in ('href', 'src', 'poster'):
            if key in attrs:
                self.references.append(attrs[key])
        if 'download' in attrs:
            self.downloads.append(attrs.get('href', ''))
        if tag == 'textarea' and attrs.get('id') == 'skill-text':
            self.textarea = True

    def handle_endtag(self, tag):
        if tag == 'textarea':
            self.textarea = False

    def handle_data(self, data):
        if self.textarea:
            self.skill += data


def source_files():
    for path in sorted(ROOT.rglob('*')):
        parts = path.relative_to(ROOT).parts
        if path.is_file() and parts[0] not in {'.git', '_site', '.research'} and path.suffix in TEXT_SUFFIXES:
            yield path


def check_personal_information():
    findings = []
    for path in source_files():
        text = path.read_text(encoding='utf-8', errors='ignore')
        for label, pattern in PII_PATTERNS.items():
            for match in pattern.finditer(text):
                findings.append(f'{path.relative_to(ROOT)}: {label}: matched text withheld')
    assert not findings, 'Personal information or credentials found:\n' + '\n'.join(findings)
    return sum(1 for _ in source_files())


def check(output):
    page = Page()
    raw = (output / 'index.html').read_text(encoding='utf-8')
    page.feed(raw)
    assert not page.duplicates, f'Duplicate IDs: {page.duplicates}'
    assert page.h1s == 1 and page.lang == 'en', 'Expected one page title and an English document language'
    assert not re.search(r'@@[A-Z_]+@@', raw), 'Unresolved placeholders'
    local_count = 0
    for reference in page.references:
        parsed = urlsplit(reference)
        if parsed.scheme or parsed.netloc:
            assert parsed.scheme == 'https', f'Unexpected external protocol: {reference}'
            continue
        assert not parsed.path.startswith('/'), f'Root-relative link would break repository hosting: {reference}'
        target = (output / unquote(parsed.path)).resolve() if parsed.path else output / 'index.html'
        assert target.is_relative_to(output.resolve()), f'Link escapes output: {reference}'
        assert target.exists(), f'Missing link or asset: {reference}'
        if parsed.fragment:
            assert target.name == 'index.html' and parsed.fragment in page.ids, f'Missing anchor: {reference}'
        local_count += 1
    markdown_count = 0
    for document in output.rglob('*.md'):
        for reference in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', document.read_text(encoding='utf-8')):
            parsed = urlsplit(reference)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            target = (document.parent / unquote(parsed.path)).resolve()
            assert target.is_relative_to(output.resolve()), f'Markdown link escapes output: {document.name}: {reference}'
            assert target.exists(), f'Missing Markdown link: {document.relative_to(output)}: {reference}'
            markdown_count += 1
    # Each placement has one panel; exactly the first shows without JavaScript.
    config = json.loads((ROOT / 'site/site.json').read_text(encoding='utf-8'))
    ids = [e['id'] for e in config['examples']]
    assert sorted(i for i, _ in page.examples) == sorted(ids), 'Every placement needs exactly one panel'
    visible = [i for i, hidden in page.examples if not hidden]
    assert visible == [ids[0]], 'Only the first placement should show before JavaScript runs'
    assert raw.count('class="ladder-svg"') == len(ids), 'Every placement needs a ladder'
    assert raw.count('data-cap=') == 6 and raw.count('data-check=') == 4, 'Calculator needs six gates and four shape checks'
    for phrase in ('fictional', 'not measured', 'not yet run'):
        assert phrase in raw.lower(), f'Honesty label missing: {phrase}'
    skill = (SKILL_DIR / 'SKILL.md').read_text(encoding='utf-8')
    assert page.skill == skill, 'Copy source differs from canonical SKILL.md'
    for name in SKILL_FILES:
        assert (SKILL_DIR / name).read_bytes() == (output / name).read_bytes(), f'Download changed source: {name}'
    with ZipFile(output / 'right-shape.zip') as bundle:
        assert bundle.namelist() == ['right-shape/' + name for name in SKILL_FILES]
        assert bundle.testzip() is None
        for name in SKILL_FILES:
            assert bundle.read('right-shape/' + name) == (SKILL_DIR / name).read_bytes(), f'Bundle changed source: {name}'
    skill_downloads = [d for d in page.downloads if not d.startswith('./assets/')]
    assert len(skill_downloads) == 2, 'Expected skill and bundle download links'
    for name in ('right-shape-film.mp4', 'right-shape-film.webm', 'right-shape-film.vtt', 'right-shape-film-poster.jpg', 'right-shape-film-15s.mp4'):
        assert (output / 'assets' / name).is_file(), f'Film asset missing: {name}'
    assert len(list(ROOT.rglob('SKILL.md'))) - len(list((ROOT / '_site').rglob('SKILL.md'))) == 1, 'Keep exactly one SKILL.md in the source tree'
    # Locally hosted assets are the only runtime dependencies.
    for name in ('assets/style.css', 'assets/family.css'):
        css = (output / name).read_text(encoding='utf-8')
        assert not re.search(r'@import|url\(\s*[\'"]?https?:', css), f'External CSS dependency: {name}'
    assert 'default-src \'self\'' in raw and 'object-src \'none\'' in raw
    scanned = check_personal_information()
    digest = hashlib.sha256((output / 'right-shape.zip').read_bytes()).hexdigest()
    print(f'PASS: {local_count} local links/assets and fragments; no missing targets or duplicate IDs')
    print(f'PASS: {markdown_count} local destinations in shipped Markdown documentation')
    print('PASS: source textarea, both Markdown downloads, and ZIP match canonical files byte-for-byte')
    print(f'PASS: {len(ids)} fictional placements recomputed from the rubric, each with a ladder; calculator wired; honesty labels present')
    print(f'PASS: {scanned} source files scanned; no email addresses, phone numbers, street addresses or credentials')
    print(f'Bundle SHA-256: {digest}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / '_site')
    args = parser.parse_args()
    check(args.output.resolve())
