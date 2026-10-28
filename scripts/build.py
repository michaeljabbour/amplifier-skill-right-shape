#!/usr/bin/env python3
"""Build a portable static site and skill bundle using only Python's standard library."""
import argparse
import html
import json
import re
import shutil
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / 'skills/right-shape'
SKILL_FILES = ('SKILL.md', 'references/rubric.md')
ARCHIVE_DATE = (2026, 10, 28, 0, 0, 0)


def escape(value):
    return html.escape(str(value), quote=True)


def section(markdown, heading):
    """Return the body of one '## heading' section."""
    match = re.search(rf'^## {re.escape(heading)}\n(.*?)(?=^## |\Z)', markdown, re.M | re.S)
    if not match:
        raise ValueError(f'Missing section: {heading}')
    return match.group(1)


def table_rows(block):
    rows = [line for line in block.splitlines() if line.startswith('|')]
    return [[cell.strip() for cell in row.strip('|').split('|')] for row in rows[2:]]


def bullets(block):
    return [line[2:].split(' | ') for line in block.splitlines() if line.startswith('- ')]


def read_rubric(rubric, benchmark):
    # The site presents the canonical method, never a second copy of it.
    r = {
        'questions': re.findall(r'^\d\. (.+)$', section(rubric, 'Sorting questions'), re.M),
        'shapes': bullets(section(rubric, 'Shapes')),
        'need': bullets(section(rubric, 'Need dimensions')),
        'need_map': table_rows(section(rubric, 'Need to rung')),
        'ladder': bullets(section(rubric, 'Ladder')),
        'gates': table_rows(section(rubric, 'Gates')),
        'checks': bullets(section(rubric, 'Shape checks')),
        'engines': table_rows(section(rubric, 'Engines')),
        'replace': bullets(section(rubric, 'Replaceability')),
        'evals': table_rows(section(rubric, 'Evaluation ladder')),
        'contract': re.search(r'```\n(.*?)```', section(rubric, 'Capability contract'), re.S).group(1),
        'dispositions': table_rows(section(rubric, 'Dispositions')),
        'diagnosis': table_rows(section(rubric, 'Diagnosis')),
        'tests': table_rows(section(benchmark, 'Tests')),
    }
    expect = {'questions': (4, None), 'shapes': (6, 2), 'need': (4, 5), 'need_map': (6, 2), 'ladder': (10, 4),
              'gates': (6, 3), 'checks': (4, 2), 'engines': (3, 3), 'replace': (5, 2), 'evals': (5, 3),
              'dispositions': (11, 2), 'diagnosis': (8, 3), 'tests': (12, 3)}
    for key, (count, width) in expect.items():
        rows = r[key]
        if len(rows) != count or (width and any(len(row) != width for row in rows)):
            raise ValueError(f'Rubric section {key}: expected {count} rows of {width} fields')
    if [int(row[0]) for row in r['ladder']] != list(range(10)):
        raise ValueError('The ladder must run from rung 0 to rung 9')
    # Need score bands, for example "0 to 1" -> rung 1, must cover 0 to 12 exactly once.
    bands = []
    for span, rung in r['need_map']:
        low, high = (int(x) for x in span.split(' to '))
        bands.append((low, high, int(rung)))
    covered = [s for low, high, _ in bands for s in range(low, high + 1)]
    if covered != list(range(13)):
        raise ValueError('Need-to-rung bands must cover scores 0 to 12 exactly once')
    r['bands'] = bands
    r['caps'] = {row[0].split()[0]: int(row[2]) for row in r['gates']}
    return r


def need_rung(score, bands):
    return next(rung for low, high, rung in bands if low <= score <= high)


def place(example, r):
    """Recompute a fictional placement from the rubric and refuse one that does not follow it."""
    eid = example['id']
    need = example['need']
    if len(need) != 4 or any(v not in (0, 1, 2, 3) for v in need):
        raise ValueError(f'{eid}: need is four scores from 0 to 3')
    score = sum(need)
    wanted = need_rung(score, r['bands'])
    unknown = set(example['failed']) - set(r['caps'])
    if unknown:
        raise ValueError(f'{eid}: unknown gates {sorted(unknown)}')
    ceiling = min([r['caps'][g] for g in example['failed']] or [9])
    expected = min(wanted, ceiling)
    rung = example['rung']
    if rung > expected:
        raise ValueError(f'{eid}: rung {rung} is above min(need {wanted}, ceiling {ceiling})')
    if rung < expected and not example.get('tiebreak'):
        raise ValueError(f'{eid}: a rung below {expected} needs a stated tiebreak')
    if (wanted > ceiling) != bool(example.get('honest_move')):
        raise ValueError(f'{eid}: an honest move is required exactly when need exceeds the ceiling')
    check_ids = {row[0].split()[0] for row in r['checks']}
    if not set(example['checks']) <= check_ids:
        raise ValueError(f'{eid}: unknown shape checks')
    shape = 'Outer harness behind an agent interface' if len(example['checks']) >= 2 else 'Single worker'
    if example['engine'] not in {row[0] for row in r['engines']}:
        raise ValueError(f'{eid}: unknown engine')
    return score, wanted, ceiling, shape


def ladder_svg(example, r, score, wanted, ceiling):  # noqa: C901
    rung = example['rung']
    width, cell, top = 640, 64, 30
    parts = []
    for i, (number, name, _role, _what) in enumerate(r['ladder']):
        x = i * cell
        state = 'pick' if i == rung else ('capped' if i > ceiling else 'open')
        parts.append(f'<rect class="rung-cell {state}" x="{x + 2}" y="{top}" width="{cell - 4}" height="44" rx="6"/>')
        parts.append(f'<text class="rung-num {state}" x="{x + cell / 2}" y="{top + 28}" text-anchor="middle">{number}</text>')
    if ceiling < 9:
        x = (ceiling + 1) * cell
        parts.append(f'<path class="rung-ceiling" d="M{x} {top - 12}V{top + 56}"/><text class="rung-note" x="{x - 6}" y="{top - 16}" text-anchor="end">ceiling {ceiling}</text>')
    if wanted != rung:
        x = wanted * cell + cell / 2
        parts.append(f'<rect class="rung-need" x="{wanted * cell + 2}" y="{top}" width="{cell - 4}" height="44" rx="6"/><text class="rung-note" x="{x}" y="{top + 72}" text-anchor="middle">wants {wanted}</text>')
    x = rung * cell + cell / 2
    parts.append(f'<text class="rung-note pick" x="{x}" y="{top + 88 if wanted != rung else top + 72}" text-anchor="middle">placed {rung}</text>')
    summary = f'Need score {score} wants rung {wanted}; ceiling {ceiling}; placed at rung {rung}, {r["ladder"][rung][1]}.'
    return (f'<div class="trace-scroll" tabindex="0" role="region" aria-label="Ladder for {escape(example["label"])}"><svg class="ladder-svg" viewBox="0 0 {width} 130" role="img" aria-labelledby="l-{example["id"]}">'
            f'<title id="l-{example["id"]}">{escape(summary)} Fictional example.</title>' + ''.join(parts) + '</svg></div>')


def card(example, r, score, wanted, ceiling, shape):
    rung = example['rung']
    need = '  '.join(f'N{i + 1} {v}' for i, v in enumerate(example['need']))
    failed = ', '.join(example['failed']) or 'none'
    lines = [f'<p class="verdict"><b>{escape(r["ladder"][rung][1])} at rung {rung}, engine {escape(example["engine"])}.</b> {escape(example["verdict"])}</p>',
             '<dl class="place-card">',
             f'<dt>Need</dt><dd>{escape(need)} = {score}, wants rung {wanted}</dd>',
             f'<dt>Ceiling</dt><dd>{ceiling} (failed: {escape(failed)})</dd>']
    if example.get('tiebreak'):
        lines.append(f'<dt>Tiebreak</dt><dd>{escape(example["tiebreak"])}</dd>')
    if example.get('honest_move'):
        lines.append(f'<dt>Honest move</dt><dd>{escape(example["honest_move"])}</dd>')
    checks = ', '.join(example['checks']) or 'none'
    lines.append(f'<dt>Shape</dt><dd>{escape(shape)} (checks: {escape(checks)})</dd>')
    lines.append('<dt>Replaceability</dt><dd>' + ''.join(f'<span class="line">{escape(g)}</span>' for g in example['gaps']) + '</dd>')
    lines.append('<dt>Benchmark</dt><dd>' + ''.join(f'<span class="line">{escape(b)}</span>' for b in example['benchmark']) + '</dd>')
    lines.append(f'<dt>Question</dt><dd>{escape(example["question"] or "None. The answer would not change the verdict.")}</dd></dl>')
    return ''.join(lines)


def panel(example, r, first):
    score, wanted, ceiling, shape = place(example, r)
    hidden = '' if first else ' hidden'
    outcome = f'Rung {example["rung"]} · {r["ladder"][example["rung"]][1]}'
    return outcome, (f'<div class="example-content" data-example="{escape(example["id"])}" data-outcome="{escape(outcome)}"{hidden}>'
                     f'<p class="example-brief">“{escape(example["brief"])}”</p>'
                     + ladder_svg(example, r, score, wanted, ceiling) + card(example, r, score, wanted, ceiling, shape) + '</div>')


def calculator(r):
    dims = ''.join(
        f'<div class="dim"><label for="n{i + 1}">{escape(name)} <output id="o{i + 1}">0</output></label>'
        f'<input type="range" id="n{i + 1}" min="0" max="3" value="{(2, 2, 1, 0)[i]}" data-hints="{escape(json.dumps(levels))}">'
        f'<p class="hint" id="h{i + 1}"></p></div>'
        for i, (name, *levels) in enumerate(r['need']))
    gates = ''.join(
        f'<label class="gate"><input type="checkbox" data-gate="{escape(g.split()[0])}" data-cap="{cap}" checked>'
        f'<span><b>{escape(g)}</b><em>{escape(q)}. Fails cap at {cap}.</em></span></label>'
        for g, q, cap in r['gates'])
    checks = ''.join(
        f'<label class="gate"><input type="checkbox" data-check="{escape(c.split()[0])}">'
        f'<span><b>{escape(c)}</b><em>{escape(q)}</em></span></label>'
        for c, q in r['checks'])
    bands = json.dumps([[low, high, rung] for low, high, rung in r['bands']])
    names = json.dumps([row[1] for row in r['ladder']])
    return (f'<div class="calc" data-bands="{escape(bands)}" data-names="{escape(names)}">'
            f'<div class="calc-inputs"><h3>Score the need</h3>{dims}<h3>Which gates pass?</h3>{gates}<h3>Shape checks</h3>{checks}</div>'
            f'<div class="calc-out" aria-live="polite"><p class="calc-label">Placement</p><p class="calc-big" id="calc-rung">Rung 3</p>'
            f'<p class="calc-meta" id="calc-meta"></p><p id="calc-msg"></p><p class="calc-shape" id="calc-shape"></p></div></div>')


def build(output):
    site = ROOT / 'site'
    config = json.loads((site / 'site.json').read_text(encoding='utf-8'))
    skill = (SKILL_DIR / 'SKILL.md').read_text(encoding='utf-8')
    rubric = (SKILL_DIR / 'references/rubric.md').read_text(encoding='utf-8')
    benchmark = (ROOT / 'docs/BENCHMARK.md').read_text(encoding='utf-8')
    r = read_rubric(rubric, benchmark)
    examples = config['examples']
    if len(examples) < 2 or len({e['id'] for e in examples}) != len(examples):
        raise ValueError('At least two distinct fictional examples are required')
    panels = [panel(e, r, i == 0) for i, e in enumerate(examples)]
    choices = config['choices']
    shape_names = {row[0] for row in r['shapes']}
    if {c['name'] for c in choices['shapes']} != shape_names - {'Package'}:
        raise ValueError('site.json choices must explain every rubric shape except Package')
    if [e['name'] for e in choices['engines']] != [row[0] for row in r['engines']]:
        raise ValueError('site.json engines must match the rubric engines, in order')
    replacements = {
        'NAME': escape(config['name']),
        'DESCRIPTION': escape(config['description']),
        'FIRST_OUTCOME': escape(panels[0][0]),
        'EXAMPLE_OPTIONS': ''.join(f'<option value="{escape(e["id"])}">{escape(e["label"])}</option>' for e in examples),
        'EXAMPLE_PANELS': ''.join(p for _, p in panels),
        'QUESTIONS': ''.join(f'<li>{escape(q)}</li>' for q in r['questions']),
        'SHAPES': ''.join(f'<li><b>{escape(n)}</b> {escape(d)}</li>' for n, d in r['shapes']),
        'LADDER': ''.join(f'<li><span class="rung-badge">{escape(n)}</span><div><b>{escape(name)}</b><span class="rung-role">{escape(role)}</span><span>{escape(what)}</span></div></li>' for n, name, role, what in r['ladder']),
        'NEED': ''.join(f'<tr><th scope="row">{escape(row[0])}</th>' + ''.join(f'<td>{escape(c)}</td>' for c in row[1:]) + '</tr>' for row in r['need']),
        'GATES': ''.join(f'<tr><th scope="row">{escape(g)}</th><td>{escape(q)}</td><td class="return-to">{escape(c)}</td></tr>' for g, q, c in r['gates']),
        'CHECKS': ''.join(f'<li><b>{escape(c)}</b> {escape(q)}</li>' for c, q in r['checks']),
        'ENGINES': ''.join(f'<article><h3>{escape(e)}</h3><p>{escape(m)}</p><p class="note">Benchmarked by: {escape(b)}</p></article>' for e, m, b in r['engines']),
        'REPLACE': ''.join(f'<li><b>{escape(c)}</b> {escape(q)}</li>' for c, q in r['replace']),
        'EVALS': ''.join(f'<tr><th scope="row">{escape(a)}</th><td>{escape(b)}</td><td>{escape(c)}</td></tr>' for a, b, c in r['evals']),
        'CONTRACT': escape(r['contract'].rstrip()),
        'DISPOSITIONS': ''.join(f'<tr><th scope="row">{escape(a)}</th><td>{escape(b)}</td></tr>' for a, b in r['dispositions']),
        'DIAGNOSIS': ''.join(f'<tr><td>{escape(a)}</td><td>{escape(b)}</td><td class="return-to">{escape(c)}</td></tr>' for a, b, c in r['diagnosis']),
        'BENCHMARK': ''.join(f'<tr><th scope="row">{escape(a)}</th><td>{escape(b)}</td><td>{escape(c)}</td></tr>' for a, b, c in r['tests']),
        'CALCULATOR': calculator(r),
        'CHOICE_SHAPES': ''.join(
            f'<li class="choice-card"><h3>{escape(c["label"])}</h3><p class="choice-plain">{escape(c["plain"])}</p><dl>'
            f'<dt>Like</dt><dd>{escape(c["like"])}</dd><dt>Pick it when</dt><dd>{escape(c["when"])}</dd>'
            f'<dt>Example</dt><dd>{escape(c["example"])}</dd><dt>Who is in charge</dt><dd>{escape(c["control"])}</dd></dl></li>'
            for c in choices['shapes']),
        'CHOICE_FREEDOM': ''.join(f'<li><b>{escape(f["name"])}</b><span class="rung-role">{"Rungs" if " to " in f["rungs"] else "Rung"} {escape(f["rungs"])}</span><span>{escape(f["plain"])}</span></li>' for f in choices['freedom']),
        'CHOICE_ENGINES': ''.join(f'<li><b>{escape(e["label"])}</b><span class="rung-role">{escape(e["name"])}</span><span>{escape(e["plain"])}</span></li>' for e in choices['engines']),
        'CHOICE_SHAPE_LIST': ''.join(f'<li><b>{escape(c["label"])}</b><span>{escape(c["like"])}</span></li>' for c in choices['shapes']),
        'GLOSSARY': ''.join(f'<dt>{escape(t)}</dt><dd>{escape(d)}</dd>' for t, d in config['glossary']),
        'SKILL_SOURCE': escape(skill),
    }
    page = (site / 'template.html').read_text(encoding='utf-8')
    for key, value in replacements.items():
        page = page.replace('@@' + key + '@@', value)
    if re.search(r'@@[A-Z_]+@@', page):
        raise ValueError('Unresolved template placeholder')
    if output.exists():
        shutil.rmtree(output)
    assets = output / 'assets'
    assets.mkdir(parents=True)
    (output / 'index.html').write_text(page, encoding='utf-8')
    shutil.copy2(site / 'theme/style.css', assets / 'family.css')
    shutil.copy2(site / 'style.css', assets / 'style.css')
    shutil.copy2(site / 'site.js', assets / 'site.js')
    shutil.copy2(site / 'theme/LICENSE', assets / 'family-LICENSE.txt')
    for asset in sorted((site / 'assets').iterdir()):
        if asset.is_file():
            shutil.copy2(asset, assets / asset.name)
    # Publish the skill at the site root (stable download links) and at its source
    # path (so README links work both on GitHub and on the site).
    for name in SKILL_FILES:
        for target in (output / name, output / SKILL_DIR.relative_to(ROOT) / name):
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SKILL_DIR / name, target)
    documentation = ['README.md', 'LICENSE', 'CHANGELOG.md', 'site/README.md', 'site/theme/LICENSE']
    documentation.extend(str(path.relative_to(ROOT)) for path in sorted((ROOT / 'docs').glob('*.md')))
    for name in documentation:
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)
    (output / '.nojekyll').touch()
    # Fixed archive metadata makes download contents reproducible across builds.
    with ZipFile(output / 'right-shape.zip', 'w', ZIP_DEFLATED) as bundle:
        for name in SKILL_FILES:
            info = ZipInfo('right-shape/' + name, ARCHIVE_DATE)
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            bundle.writestr(info, (SKILL_DIR / name).read_bytes())
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / '_site', help='Static output directory (default: _site)')
    args = parser.parse_args()
    print(f'Built {build(args.output.resolve())}')
