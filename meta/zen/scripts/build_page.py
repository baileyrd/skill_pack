#!/usr/bin/env python3
"""Build the Zen review page from a scan's run folder, so every review has the same shape.

    python3 build_page.py --run RUN_DIR [--review review.json] [--artifacts artifacts.txt]
                          [--results results.json] [--out RUN_DIR/review.html]

With only --run it makes a complete page: headline numbers, the six sections grouped from the
scan's findings, and a Declutter section built from interface.json (Code-tab chats to archive or
group, Cowork chats and projects marked as things the owner does in the app). Optional inputs:
  --artifacts  the saved text of an Artifact tool `list` call; grouped into repeated titles,
               untitled pages and pages not updated in 60+ days.
  --review     Claude's judgement: better-worded sections, questions, extra findings, a sidebar
               group per kept chat (see references/review-page.md for the shape).
  --results    the before-and-after block, added after the changes are applied.
Publish the output with the Artifact tool and capabilities {"db": {}}; rulings save to the page's
"rulings" collection. Write what was applied to an "applied" collection, never over "rulings".
"""
import argparse
import collections
import html
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / 'assets' / 'review.html'

BROKEN = {('connectors', 'broken'), ('hooks', 'failing'), ('hooks', 'missing-script'), ('scheduled', 'failing'),
          ('scheduled', 'errors'), ('scheduled', 'missing-skill'), ('scheduled', 'old-copy'), ('scheduled', 'stale'),
          ('cowork', 'project-missing-folder'), ('context', 'dead-route'), ('skills', 'needs-connector')}
LOADS = {'skills', 'agents', 'plugins', 'connectors'}
SUGG = {'duplicate': 'do', 'unused': 'keep', 'broken': 'do', 'failing': 'do', 'missing-script': 'do', 'stale': 'do',
        'missing-skill': 'do', 'old-copy': 'do', 'retired-still-loaded': 'do', 'secret': 'keep', 'write-allowed': 'ask',
        'broad-allow': 'ask', 'bypass': 'ask', 'dead-ref': 'do', 'dead-route': 'do', 'stale-override': 'do',
        'switched-off': 'do', 'old-model': 'do', 'heavy': 'ask', 'overlap': 'ask', 'budget': 'do', 'review-firing': 'ask',
        'account-unused': 'ask', 'disabled': 'keep', 'info': 'keep', 'contradiction-check': 'ask', 'hot-heavy': 'ask'}


TITLE = {
    ('connectors', 'broken'): '%d connectors signed out or failing', ('connectors', 'unused'): '%d connectors never called',
    ('connectors', 'duplicate'): '%d services connected more than once', ('connectors', 'errors'): '%d connectors returning errors',
    ('hooks', 'failing'): '%d hooks failing', ('hooks', 'missing-script'): '%d hooks whose script is missing',
    ('hooks', 'slow'): '%d slow hooks', ('hooks', 'heavy'): '%d hooks that add a lot to every session',
    ('scheduled', 'stale'): '%d scheduled tasks that stopped running', ('scheduled', 'errors'): '%d scheduled jobs with errors in their logs',
    ('scheduled', 'missing-skill'): '%d scheduled tasks calling skills that no longer load',
    ('scheduled', 'old-model'): '%d scheduled tasks on older models', ('scheduled', 'switched-off'): '%d launch agents installed but switched off',
    ('permissions', 'broad-allow'): '%d permission rules that skip asking for everything',
    ('permissions', 'write-allowed'): '%d send, change or delete tools pre-approved',
    ('skills', 'duplicate'): '%d skills loaded more than once', ('skills', 'unused'): '%d of your skills with no recorded run',
    ('skills', 'dead-ref'): '%d skills mentioning files that do not exist', ('skills', 'overlap'): '%d pairs of skills that overlap',
    ('skills', 'retired-still-loaded'): '%d archived skills still loading from your uploads', ('skills', 'heavy'): '%d skills with long descriptions',
    ('plugins', 'unused'): '%d plugins with no recorded use', ('plugins', 'twice'): '%d plugins installed twice',
    ('agents', 'unused'): '%d agents with no recorded run', ('agents', 'heavy'): '%d agents with long descriptions',
    ('context', 'dead-route'): '%d manifest routes point at missing files', ('context', 'dead-ref'): '%d notes with broken links',
    ('context', 'no-index'): '%d folders with no index', ('context', 'hot-heavy'): '%d big notes Claude opens often',
    ('context', 'orphans'): '%d folders with notes nothing links to', ('context', 'unrouted'): '%d folders the manifest never routes into',
    ('memory', 'dead-ref'): '%d memory entries naming files that are gone', ('memory', 'orphan'): '%d memory entries the index never links',
    ('instructions', 'dead-ref'): '%d instruction files pointing at missing paths', ('instructions', 'unmapped-folder'): '%d folders CLAUDE.md never mentions',
    ('disk', 'cold-heavy'): '%d big folders nothing has touched', ('models', 'old-model'): '%d older model IDs in your settings',
}
NAV = {'broken': 'Broken', 'risky': 'Risky', 'loads': 'Loads', 'context': 'Context', 'else': 'Other'}


def label(area, kind, n):
    return TITLE.get((area, kind), '%d ' + area + ': ' + kind.replace('-', ' ')) % n


def one_title(f):
    """A single finding's title: its item, plus what is wrong when the item alone says little."""
    if len(f['item']) > 22:
        return f['item']
    first = re.split(r'(?<=[.;:])\s', f['evidence'])[0].rstrip('.;:')
    return '%s: %s' % (f['item'], first[:70])


def short(f):
    return {'id': f['id'], 'a': f['area'], 'k': f['kind'], 't': f['item'], 'e': f['evidence'], 's': f['action'],
            'r': f['risk']}


def auto_sections(findings):
    by = collections.defaultdict(list)
    for f in findings:
        if f['kind'] in ('info', 'fixed', 'recovered', 'other-folders'):
            continue  # nothing to rule on; they stay in report.md and the full list
        if (f['area'], f['kind']) in BROKEN:
            sec = 'broken'
        elif f['risk'] == 'high' or f['area'] == 'permissions':
            sec = 'risky'
        elif f['area'] == 'interface' or f['area'] == 'cowork':
            continue  # these become Declutter rows
        elif f['area'] in LOADS:
            sec = 'loads'
        elif f['area'] == 'context':
            sec = 'context'
        else:
            sec = 'else'
        by[(sec, f['area'], f['kind'])].append(f)
    meta = [('broken', 'Broken', 'var(--crit)', 'These fail today. Fix them first.'),
            ('risky', 'Risky', 'var(--warn)', 'Working, but exposing you to more than you probably want.'),
            ('loads', 'What loads every chat', 'var(--accent)', 'Copies and leftovers that load into every session.'),
            ('context', 'Context layer', 'var(--ask)', 'What Claude reads to know the business: links, routes, heavy and stale notes.'),
            ('else', 'Everything else', 'var(--muted)', 'Disk, models, instruction files and memory.')]
    out = []
    for key, title, tone, lede in meta:
        items = []
        for (sec, area, kind), fs in sorted(by.items(), key=lambda kv: -len(kv[1])):
            if sec != key:
                continue
            if len(fs) == 1:
                f = fs[0]
                items.append({'id': f['id'], 'title': one_title(f), 'sugg': SUGG.get(kind, 'ask'),
                              'body': html.escape(f['evidence'] + ' Suggested: ' + f['action'])})
            else:
                items.append({'id': 'G-%s-%s' % (area, kind), 'title': label(area, kind, len(fs)),
                              'sugg': SUGG.get(kind, 'ask'), 'body': html.escape(fs[0]['action']),
                              'members': [f['id'] for f in fs]})
        out.append({'key': key, 'nav': NAV[key], 'title': title, 'tone': tone, 'lede': lede, 'items': items})
    return out


def resolve(sections, findings):
    """Turn {"select": {"area": ..., "kind": [...]}} member specs into finding ids."""
    for s in sections:
        for it in s.get('items', []):
            m = it.get('members')
            if isinstance(m, dict):
                kinds = m.get('kind')
                kinds = [kinds] if isinstance(kinds, str) else kinds
                it['members'] = [f['id'] for f in findings if f['area'] == m.get('area')
                                 and (not kinds or f['kind'] in kinds)]
    return sections


def chats(interface, groups):
    def row(s, sugg):
        folder = Path(s['folder']).name if s.get('folder') else ''
        meta = ' · '.join(x for x in (s.get('last'), 'scratch' if '/scratch-' in (s.get('folder') or '') else folder,
                                       '%s turns' % s['turns'] if s.get('turns') is not None else '') if x)
        return {'id': 'chat:' + s['id'], 'title': s['title'], 'meta': meta, 'sugg': sugg, 'sg': groups.get(s['id'], '')}
    out = []
    code = [s for s in interface if s['surface'] == 'Code tab' and not s['archived'] and not s['scheduled']]
    if code:
        rows = [row(s, 'archive' if (s['one_off'] or s['stray_folder'] or s['idle']) else 'keep')
                for s in sorted(code, key=lambda s: s['idle_days'] or 0)]
        out.append({'key': 'dc-code', 'title': 'Code tab chats', 'kind': 'archive', 'groups': True, 'open': True,
                    'lede': '%d open chats. Archiving takes a chat out of the sidebar and can be undone; nothing is '
                            'deleted. Pick Keep to choose a sidebar group for it.' % len(rows), 'rows': rows})
    cw = [s for s in interface if s['surface'] == 'Cowork' and not s['archived'] and not s['scheduled']]
    if cw:
        rows = [row(s, 'archive' if (s['one_off'] or s['stray_folder'] or s['idle']) else 'keep')
                for s in sorted(cw, key=lambda s: -(s['idle_days'] or 0))]
        out.append({'key': 'dc-cowork', 'title': 'Cowork chats', 'kind': 'archive', 'manual': True, 'open': False,
                    'lede': '%d open chats. The desktop tools only reach Code-tab chats, so mark them here and archive '
                            'them yourself: Cowork sidebar › the chat\'s menu › Archive. Grouping Cowork chats means '
                            'moving them into a Cowork project, also done in Cowork.' % len(rows), 'rows': rows})
    return out


def projects(findings):
    rows = []
    for f in findings:
        if f['area'] == 'cowork' and f['kind'] in ('project-missing-folder', 'project-idle'):
            name = f['item'].replace(' (Cowork project)', '')
            sugg = 'archive' if f['kind'] == 'project-missing-folder' or '(0 on record)' in f['evidence'] else 'keep'
            rows.append({'id': 'proj:' + name, 'title': name, 'meta': f['evidence'], 'sugg': sugg})
    if not rows:
        return []
    return [{'key': 'dc-projects', 'title': 'Cowork projects', 'kind': 'archive', 'manual': True, 'open': True,
             'lede': 'Archiving a Cowork project deletes its instructions, links and memory; your folders are '
                     'untouched. Do it from the project\'s menu in the Cowork sidebar. That part cannot be undone, so '
                     'projects with history are set to Keep.', 'rows': rows}]


GENERIC_NAMES = {'design system', 'dashboard', 'slides', 'deck', 'document', 'doc', 'page', 'new live artifact',
                 'untitled', 'design', 'motion'}
ART = re.compile(r'^\s*-\s*\((mine|[^)]*)\)\s*(.*?)\s+—\s+(https://claude\.ai/artifact/([A-Za-z0-9]+))\s+—\s+updated\s+(\d{4}-\d{2}-\d{2})')


def artifacts(text, today):
    arts = []
    for line in text.splitlines():
        m = ART.match(line)
        if m and m.group(1) == 'mine':
            arts.append({'title': m.group(2) or 'Untitled', 'link': m.group(3), 'id': m.group(4), 'updated': m.group(5)})
    if not arts:
        return []
    def row(a, sugg, why=''):
        return {'id': 'art:' + a['id'], 'title': a['title'], 'link': a['link'],
                'meta': 'Updated ' + a['updated'] + (' · ' + why if why else ''), 'sugg': sugg}
    used, groups = set(), []
    norm = lambda t: re.sub(r'\W+', ' ', t).strip().lower()
    reviews = [a for a in arts if a['title'].startswith('Zen Review')]
    if reviews:  # every run publishes a new page; the earlier ones are superseded
        used.update(a['id'] for a in reviews)
        week = (today - timedelta(days=7)).isoformat()
        groups.append({'key': 'dc-art-reviews', 'title': 'Artifacts: earlier Zen reviews', 'kind': 'delete', 'open': True,
                       'lede': 'This page replaces them. Their rulings stay on them until you delete them, so keep a '
                               'recent one until its rulings are applied.',
                       'rows': [row(a, 'delete' if a['updated'] < week else 'keep', 'earlier review')
                                for a in sorted(reviews, key=lambda a: a['updated'], reverse=True)]})
    # Names an artifact type gives by default: different pages, not copies of one page.
    generic = [a for a in arts if norm(a['title']) in GENERIC_NAMES]
    by_title = collections.defaultdict(list)
    for a in arts:
        if norm(a['title']) not in GENERIC_NAMES and norm(a['title']) not in ('untitled', ''):
            by_title[norm(a['title'])].append(a)
    rows = []
    for t, copies in by_title.items():
        copies.sort(key=lambda a: a['updated'], reverse=True)
        if len(copies) >= 3:  # a page made again and again (a daily brief): keep the newest
            rows.append(row(copies[0], 'keep', 'newest of %d' % len(copies)))
            rows += [row(a, 'delete', 'older copy') for a in copies[1:]]
            used.update(a['id'] for a in copies)
        elif len(copies) == 2:  # two may be two different pages; let the owner compare
            rows += [row(a, 'keep', 'one of 2 with this name; open both to compare') for a in copies]
            used.update(a['id'] for a in copies)
    if rows:
        groups.append({'key': 'dc-art-copies', 'title': 'Artifacts: repeated titles', 'kind': 'delete', 'open': True,
                       'lede': 'Pages with the same name. Where one page was made again and again, keep the newest. '
                               'Deleting is permanent and breaks the link for anyone you sent it to, so open a link '
                               'first if unsure.', 'rows': rows})
    gen = [a for a in generic if a['id'] not in used and norm(a['title']) != 'untitled']
    if len(gen) >= 2:
        used.update(a['id'] for a in gen)
        groups.append({'key': 'dc-art-generic', 'title': 'Artifacts: default names', 'kind': 'delete', 'open': False,
                       'lede': 'These kept the name their type gives them, so they are hard to tell apart in the '
                               'gallery. They are usually different pages: keep them and ask Claude to rename them.',
                       'rows': [row(a, 'keep', 'default name') for a in sorted(gen, key=lambda a: a['updated'], reverse=True)]})
    cutoff_new = (today - timedelta(days=14)).isoformat()
    unt = [a for a in arts if a['title'].strip().lower() in ('untitled', '') and a['id'] not in used]
    if unt:
        used.update(a['id'] for a in unt)
        groups.append({'key': 'dc-art-untitled', 'title': 'Artifacts: untitled', 'kind': 'delete', 'open': False,
                       'lede': 'No name, so you cannot tell them apart in the gallery. Recent ones are set to Keep so '
                               'you can open them first.',
                       'rows': [row(a, 'keep' if a['updated'] >= cutoff_new else 'delete') for a in unt]})
    cutoff = (today - timedelta(days=60)).isoformat()
    stale = [a for a in arts if a['updated'] < cutoff and a['id'] not in used]
    if stale:
        groups.append({'key': 'dc-art-stale', 'title': 'Artifacts: not updated in 60+ days', 'kind': 'delete',
                       'open': False, 'lede': 'The listing has no last-opened date, only last updated. Some may be '
                       'pages you still send people, so these are set to Keep. Flip the ones you are done with.',
                       'rows': [row(a, 'keep') for a in sorted(stale, key=lambda a: a['updated'])]})
    return groups


def main():
    ap = argparse.ArgumentParser(description='Build the Zen review page.')
    ap.add_argument('--run', required=True)
    ap.add_argument('--review')
    ap.add_argument('--artifacts')
    ap.add_argument('--results')
    ap.add_argument('--out')
    a = ap.parse_args()
    run = Path(a.run)
    findings = json.loads((run / 'findings.json').read_text(encoding='utf-8'))
    summary = json.loads((run / 'summary.json').read_text(encoding='utf-8'))
    interface = json.loads((run / 'interface.json').read_text(encoding='utf-8')) if (run / 'interface.json').exists() else []
    review = json.loads(Path(a.review).read_text(encoding='utf-8')) if a.review else {}
    for f in review.get('added', []):
        findings.append({'id': f['id'], 'area': f.get('area', 'else'), 'kind': f.get('kind', 'added'),
                         'item': f['item'], 'evidence': f['evidence'], 'action': f.get('action', ''),
                         'risk': f.get('risk', 'low')})
    today = datetime.strptime(summary['date'][:10], '%Y-%m-%d').date()
    sections = resolve(review.get('sections') or auto_sections(findings), findings)
    declutter = chats(interface, review.get('chat_groups', {})) + projects(findings)
    if a.artifacts:
        declutter += artifacts(Path(a.artifacts).read_text(encoding='utf-8'), today)
    declutter += review.get('declutter_extra', [])
    b = summary['baseline']
    broken = sum(1 for f in findings if (f['area'], f['kind']) in BROKEN)
    to_clear = sum(1 for g in declutter for r in g['rows'] if r['sugg'] in ('archive', 'delete'))
    to_clear += sum(1 for f in findings if f['kind'] in ('duplicate', 'retired-still-loaded'))
    head = {'title': 'Zen Review, %d %s %s' % (today.day, today.strftime('%b'), summary['date'][11:16]),  # no %-d on Windows
            'sub': 'A tidy of the Claude setup in <code>%s</code>, scanned %s over the last %s days. Nothing has '
                   'changed yet. Mark each item; Claude applies only what you approve, one change at a time.' % (
                       html.escape(summary['project']), html.escape(summary['date']), summary['days']),
            'nums': [{'value': '~{:,}'.format(b['total']), 'label': 'tokens load before your first message (estimate)'},
                     {'value': str(broken), 'label': 'things broken right now', 'tone': 'crit' if broken else ''},
                     {'value': str(to_clear), 'label': 'copies, chats and pages to clear'}],
            'budget': [{'label': 'Skill listings', 'tokens': b['skills'], 'color': '--bar-skills'},
                       {'label': 'Memory index', 'tokens': b['memory'], 'color': '--bar-mem'},
                       {'label': 'Instruction files', 'tokens': b['instructions'], 'color': '--bar-instr'},
                       {'label': 'Agent list', 'tokens': b['agents'], 'color': '--bar-agents'}],
            'callout': 'Your rulings save as you click. When you are done, tell Claude <b>"apply my zen rulings"</b>. '
                       'A dot marks each suggestion. Token figures are estimates (characters ÷ 4); '
                       '<code>/context</code> has the exact number. <b>Hide titles</b> blurs names for screen recording.'}
    head.update(review.get('head', {}))
    data = {'head': head, 'findings': [short(f) for f in findings], 'sections': sections,
            'questions': review.get('questions', []), 'sidebar_groups': review.get('sidebar_groups', []),
            'declutter': declutter,
            'declutter_note': 'claude.ai chats and Projects live in your account, out of reach from here: claude.ai › '
                              'Chats › Select to archive; a project\'s menu › Archive.',
            'footer': 'Source: <code>%s/findings.json</code>. Connector URLs are never shown. Undo the helper\'s changes: '
                      '<code>zen_apply.py --run %s undo</code>.' % (html.escape(str(run)), html.escape(run.name))}
    if a.results:
        data['results'] = json.loads(Path(a.results).read_text(encoding='utf-8'))
    page = TEMPLATE.read_text(encoding='utf-8').replace('/*REVIEW*/{}', json.dumps(data).replace('</', '<\\/'), 1)
    assert '/*REVIEW*/' not in page
    out = Path(a.out) if a.out else run / 'review.html'
    out.write_text(page, encoding='utf-8')
    print(json.dumps({'page': str(out), 'findings': len(findings), 'sections': [s['key'] for s in sections],
                      'declutter_rows': {g['key']: len(g['rows']) for g in declutter},
                      'publish': 'Artifact publish file_path=%s capabilities={"db": {}} icon=checklist' % out}, indent=1))


if __name__ == '__main__':
    main()
