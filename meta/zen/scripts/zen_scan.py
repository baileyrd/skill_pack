#!/usr/bin/env python3
"""Read-only scan of a Claude Code setup: what is installed, what actually ran, what is broken.

Feeds the zen skill. It gathers facts so Claude can judge them; it never changes
anything outside its own run folder. Each run writes findings.json, report.md,
summary.json and corrections.jsonl into a dated folder and appends one line to the
history file beside it, so the next run (or a dashboard) can show the trend.

Privacy: connector URLs are reduced to a host, never printed (some carry API keys).
Transcripts are read for names, counts and timings. Prompt snippets used to judge
misfiring skills and outdated rules stay in the local run folder.

Usage:
  python3 zen_scan.py [--project-dir DIR] [--days 30] [--out DIR]
                       [--context-dir DIR ...] [--skip-mcp] [--quick] [--find-app]
"""
import argparse
import base64
import collections
import hashlib
import json
import os
import platform
import plistlib
import re
import shutil
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

HOME = Path.home()
CLAUDE = HOME / '.claude'
NOW = time.time()
DAY = 86400
SKIP_DIRS = {'.git', 'node_modules', '.venv', 'venv', '__pycache__', '.mypy_cache',
             '.pytest_cache', 'archive', '.next', 'dist', '.cache'}
TEXT_EXT = {'.md', '.json', '.yaml', '.yml', '.py', '.sh', '.txt', '.toml', '.js', '.ts', '.html'}
WRITE_VERBS = re.compile(
    r'(send|create|delete|remove|update|edit|write|post|publish|deploy|upload|transfer|pay|'
    r'merge|push|cancel|revoke|archive|move|share|invite|bulk|apply|execute|reply|unsubscribe)',
    re.I)
CORRECTION_CUES = re.compile(
    r"(^no[,. ]|\bdon'?t\b|\bdo not\b|\bstop\b|\bnever\b|\binstead\b|\bwrong\b|\bnot what\b|"
    r"\bi said\b|\bi told you\b|\bfrom now on\b|\bactually\b|\bwhy did you\b)", re.I)
MODEL_ID = re.compile(r'claude-(?:opus|sonnet|haiku|fable)-[0-9][0-9a-z.-]*')
# Paths a skill writes to at runtime, so a missing one is not a broken reference.
OUTPUT_SEGS = {'.tmp', 'tmp', 'deliverables', 'data', 'logs', 'output', 'outputs', 'out', 'build',
               'dist', 'scratch', 'exports'}
TRANSIENT = ('~/Downloads', '~/Desktop', str(HOME / 'Downloads'), str(HOME / 'Desktop'))
# Raw material that is not meant to be linked from an index.
RAW_DIRS = {'evidence', 'sources', 'source', 'raw', 'research', '_reference', 'reference',
            'examples', 'assets', '_retired', 'retired', '_archive', 'archive'}

FINDINGS = []
NOT_CHECKED = []
INTERFACE = []  # desktop chats, written to interface.json
TWICE = []  # plugins installed at more than one scope


# ---------- small helpers ----------

def read_text(p, limit=2_000_000):
    try:
        with open(p, 'r', encoding='utf-8', errors='replace') as f:
            return f.read(limit)
    except OSError:
        return ''


def read_json(p):
    try:
        with open(p, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def toks(chars):
    return int(round(chars / 4))


def tilde(p):
    s, h = str(p), str(HOME)
    if os.name == 'nt' and s:  # the desktop app can write c:\users\me or C:/Users/me for C:\Users\Me
        s = os.path.normpath(s)
        if os.path.normcase(s).startswith(os.path.normcase(h)):
            s = h + s[len(h):]
    s = '~' + s[len(h):] if s.startswith(h) else s
    return s.replace(os.sep, '/')  # Windows: show and match paths with / like everywhere else


def rel(p, base):
    try:
        return Path(p).relative_to(base).as_posix()
    except ValueError:
        return tilde(p)


def age_days(ts):
    return int((NOW - ts) / DAY) if ts else None


def fmt_when(ts):
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d') if ts else 'never'


def parse_ts(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(str(s).replace('Z', '+00:00')).timestamp()
    except ValueError:
        return None


def frontmatter(text):
    if not text.startswith('---'):
        return {}
    end = text.find('\n---', 3)
    if end == -1:
        return {}
    fm, key = {}, None
    for line in text[3:end].splitlines():
        m = re.match(r'^([A-Za-z0-9_-]+):\s*(.*)$', line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            fm[key] = '' if val in ('>', '>-', '|', '|-', '>+', '|+') else val.strip('"\'')
        elif key and line[:1] in (' ', '\t'):
            fm[key] = (fm[key] + ' ' + line.strip()).strip()
    return fm


def run(cmd, cwd=None, timeout=60):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='replace',
                           timeout=timeout)
        return r.returncode, r.stdout
    except (OSError, subprocess.TimeoutExpired):
        return None, ''


def dir_size_kb(p):
    code, out = run(['du', '-sk', str(p)], timeout=120)
    try:
        return int(out.split()[0])
    except (IndexError, ValueError):
        pass
    total = 0  # no du (Windows without Git Bash): add it up here
    for dp, _dns, fns in os.walk(p):
        for fn in fns:
            try:
                total += os.lstat(os.path.join(dp, fn)).st_size
            except OSError:
                pass
    return total // 1024


def gb(kb):
    return round(kb / 1024 / 1024, 1)


def add(area, item, evidence, action, risk='low', reversible=True, kind='', undo='', source=''):
    FINDINGS.append({'area': area, 'kind': kind, 'item': item, 'source': source,
                     'evidence': evidence, 'action': action, 'risk': risk,
                     'reversible': reversible, 'undo': undo})


def project_slug(P):
    return re.sub(r'[^A-Za-z0-9]', '-', str(P))


def norm_key(s):
    return re.sub(r'_+', '_', re.sub(r'[^a-z0-9]', '_', s.lower())).strip('_')


# ---------- settings and plugins ----------

def load_settings(P):
    out = []
    for scope, p in (('user', CLAUDE / 'settings.json'),
                     ('project', P / '.claude' / 'settings.json'),
                     ('local', P / '.claude' / 'settings.local.json')):
        d = read_json(p)
        if isinstance(d, dict):
            out.append((scope, p, d))
    return out


def plugin_name(install_dir, fallback):
    d = read_json(Path(install_dir) / '.claude-plugin' / 'plugin.json')
    return (d or {}).get('name') or fallback


def plugin_sources(P, settings):
    """Plugins that load in this project: CLI installs that are enabled, plus account-synced ones."""
    enabled = {}
    for _scope, _p, d in settings:  # user < project < local
        for k, v in (d.get('enabledPlugins') or {}).items():
            enabled[k] = bool(v)
    plugins = []
    reg = read_json(CLAUDE / 'plugins' / 'installed_plugins.json') or {}
    for key, entries in (reg.get('plugins') or {}).items():
        for e in entries if isinstance(entries, list) else [entries]:
            scope, proj = e.get('scope'), e.get('projectPath')
            if scope in ('project', 'local') and proj and Path(proj) != P:
                continue
            path = e.get('installPath')
            if not path or not Path(path).is_dir():
                continue
            plugins.append({'key': key, 'name': plugin_name(path, key.split('@')[0]),
                            'origin': 'installed', 'marketplace': key.split('@')[-1],
                            'enabled': enabled.get(key, False), 'path': Path(path), 'scope': scope,
                            'updated': e.get('lastUpdated') or e.get('installedAt')})
    for acct in (CLAUDE / 'plugins' / 'synced').glob('*'):
        man = read_json(acct / 'manifest.json') or {}
        for m in man.get('plugins') or []:
            name = m.get('name', '')
            cands = [acct / name] + sorted(acct.glob(name + '~g*'))
            path = next((c for c in cands if c.is_dir()), None)
            if not path:
                continue
            real = plugin_name(path, name)
            # `claude plugin disable <name>@synced` turns one off on this machine only
            off_here = enabled.get(real + '@synced') is False or enabled.get(name + '@synced') is False
            plugins.append({'key': real + '@synced', 'name': real, 'origin': 'account',
                            'marketplace': m.get('marketplaceName', ''),
                            'enabled': m.get('installationPreference') != 'disabled' and not off_here,
                            'path': path, 'updated': m.get('updatedAt')})
    seen = collections.defaultdict(list)
    for pl in plugins:
        if pl['origin'] == 'installed':
            seen[pl['key']].append(pl)
    for key, copies in seen.items():
        if len(copies) > 1:
            TWICE.append((key, sorted({c.get('scope', '?') for c in copies})))
    return plugins


# ---------- transcripts: what actually ran ----------

def desktop_app_dirs():
    """The Claude desktop app's data folder, where Code-tab and Cowork chats and task runs live.
    Windows has two, depending on the installer, so read both (Claude Code docs, HIPAA setup page)."""
    system = platform.system()
    if system == 'Darwin':
        found = [HOME / 'Library' / 'Application Support' / 'Claude']
    elif system == 'Windows':
        found = [Path(os.environ.get('APPDATA') or HOME / 'AppData' / 'Roaming') / 'Claude']
        local = Path(os.environ.get('LOCALAPPDATA') or HOME / 'AppData' / 'Local')
        found += sorted(local.glob('Packages/Claude_*/LocalCache/Roaming/Claude'))
    else:  # Linux desktop app (beta): Electron's default
        found = [Path(os.environ.get('XDG_CONFIG_HOME') or HOME / '.config') / 'Claude']
    return [d for d in found if d.is_dir()]


APPS = desktop_app_dirs()
APP_SEARCH = None  # set when --find-app ran: 'found', 'none' or 'timed-out'
SESSION_DIRS = ('claude-code-sessions', 'local-agent-mode-sessions')
FIND_SKIP = SKIP_DIRS | {'.Trash', '$Recycle.Bin', 'Backups', 'backup', 'backups', 'Caches', 'Temp',
                         'Mail', 'Developer', 'Mobile Documents', 'Pictures', 'Music', 'Movies', 'site-packages'}


def find_app_dirs(limit_s=90):
    """Search the home folder for the app's data: a folder holding Code-tab or Cowork session folders.
    Only after the owner says yes. Backups, caches and media folders are skipped; it stops after limit_s."""
    found, start, timed_out = [], time.time(), False
    for dp, dns, _fns in os.walk(HOME):
        if any(d in SESSION_DIRS for d in dns):
            found.append(Path(dp))
            dns[:] = []
            continue
        timed_out = timed_out or time.time() - start > limit_s
        depth = len(Path(dp).relative_to(HOME).parts)
        dns[:] = [] if timed_out or depth >= 8 else [
            d for d in dns if d not in FIND_SKIP and (not d.startswith('.') or d == '.config')]
    return found, timed_out


def app_sessions(sub):
    """Session files the desktop app keeps for one surface (claude-code-sessions or local-agent-mode-sessions)."""
    for app in APPS:
        yield from app.glob(sub + '/*/*/local_*.json')


def transcript_files(since):
    """Claude Code session logs plus Cowork's audit logs, both in the same message format."""
    root = CLAUDE / 'projects'
    if root.is_dir():
        for f in root.rglob('*.jsonl'):
            yield f, 'code', f.relative_to(root).parts[0]
    for app in APPS:
        cw = app / 'local-agent-mode-sessions'
        if cw.is_dir():
            for f in cw.rglob('audit.jsonl'):
                yield f, 'cowork', 'cowork'


def scan_transcripts(days):
    since = NOW - days * DAY
    use = {
        'skill': collections.defaultdict(lambda: {'n': 0, 'model': 0, 'user': 0, 'last': 0, 'cowork': 0,
                                                  'samples': collections.deque(maxlen=3)}),
        'agent': collections.defaultdict(lambda: {'n': 0, 'last': 0}),
        'mcp': collections.defaultdict(lambda: {'n': 0, 'last': 0, 'errors': 0, 'cowork': 0,
                                                'tools': collections.Counter()}),
        'hook': collections.defaultdict(lambda: {'n': 0, 'fail': 0, 'ms': [], 'out': []}),
        'read': collections.defaultdict(lambda: {'n': 0, 'last': 0}),
        'cwd': collections.defaultdict(set),
    }
    corrections = []
    earliest, files = None, 0
    if not (CLAUDE / 'projects').is_dir():
        NOT_CHECKED.append('Session history: no ~/.claude/projects folder')
    for f, surface, project in transcript_files(since):
        try:
            if f.stat().st_mtime < since:
                continue
        except OSError:
            continue
        files += 1
        last_user, tool_server = '', {}
        try:
            fh = open(f, encoding='utf-8', errors='replace')
        except OSError:
            continue
        with fh:
            for line in fh:
                hit_tool = '"tool_use"' in line
                hit_cmd = 'command-name' in line
                hit_hook = '"hook_' in line
                hit_err = '"is_error":true' in line
                hit_user = ('"type":"user"' in line or '"type": "user"' in line) and len(line) < 20000
                if not (hit_tool or hit_cmd or hit_hook or hit_err or hit_user):
                    continue
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                ts = parse_ts(r.get('timestamp') or r.get('_audit_timestamp'))
                if not ts or ts < since:
                    continue
                earliest = ts if earliest is None else min(earliest, ts)
                if r.get('cwd') and r.get('sessionId'):
                    use['cwd'][r['cwd']].add(r['sessionId'])
                att = r.get('attachment')
                if isinstance(att, dict) and str(att.get('type', '')).startswith('hook'):
                    h = use['hook'][(att.get('hookName') or att.get('hookEvent') or '?',
                                     str(att.get('command') or '')[:160])]
                    h['n'] += 1
                    code = str(att.get('exitCode'))
                    if code == '2' or 'blocking_error' in str(att.get('type')) and 'non_blocking' not in str(att.get('type')):
                        h['blocked'] = h.get('blocked', 0) + 1  # a deliberate block is the hook working
                    elif 'error' in str(att.get('type')) or code not in ('None', '0'):
                        h['fail'] += 1
                        h['last_fail'] = max(h.get('last_fail', 0), ts)
                        h.setdefault('codes', collections.Counter())[code] += 1
                    if att.get('durationMs') is not None:
                        try:
                            h['ms'].append(float(att['durationMs']))
                        except (TypeError, ValueError):
                            pass
                    h['out'].append(len(str(att.get('stdout') or '')) + len(str(att.get('content') or '')))
                    continue
                msg = r.get('message') or {}
                content = msg.get('content')
                if r.get('type') == 'user':
                    text = content if isinstance(content, str) else ''
                    if isinstance(content, list):
                        for b in content:
                            if not isinstance(b, dict):
                                continue
                            if b.get('type') == 'tool_result' and b.get('is_error'):
                                srv = tool_server.get(b.get('tool_use_id'))
                                if srv:
                                    use['mcp'][srv]['errors'] += 1
                            if b.get('type') == 'text' and not text:
                                text = b.get('text', '')
                    for name in re.findall(r'<command-name>/?([^<\s]+)</command-name>', text):
                        s = use['skill'][name]
                        s['n'] += 1
                        s['user'] += 1
                        s['last'] = max(s['last'], ts)
                    if text and not text.lstrip().startswith('<') and not r.get('isSidechain'):
                        last_user = text.strip()
                        if CORRECTION_CUES.search(text[:600]) and len(text) < 1500:
                            corrections.append({'when': fmt_when(ts), 'project': project,
                                                'text': text.strip()[:280]})
                    continue
                if not isinstance(content, list):
                    continue
                for b in content:
                    if not isinstance(b, dict) or b.get('type') != 'tool_use':
                        continue
                    name, inp = b.get('name', ''), b.get('input') or {}
                    if name == 'Skill' and inp.get('skill'):
                        s = use['skill'][inp['skill']]
                        s['n'] += 1
                        s['model'] += 1
                        s['cowork'] += surface == 'cowork'
                        s['last'] = max(s['last'], ts)
                        s['samples'].append({'when': fmt_when(ts), 'asked': last_user[:200]})
                    elif name == 'Read' and inp.get('file_path'):
                        rd = use['read'][os.path.normpath(inp['file_path'])]
                        rd['n'] += 1
                        rd['last'] = max(rd['last'], ts)
                    elif name in ('Agent', 'Task') and inp.get('subagent_type'):
                        a = use['agent'][inp['subagent_type']]
                        a['n'] += 1
                        a['last'] = max(a['last'], ts)
                    elif name.startswith('mcp__'):
                        parts = name.split('__')
                        if len(parts) >= 3:
                            srv = parts[1]
                            m = use['mcp'][srv]
                            m['n'] += 1
                            m['cowork'] += surface == 'cowork'
                            m['last'] = max(m['last'], ts)
                            m['tools']['__'.join(parts[2:])] += 1
                            tool_server[b.get('id')] = srv
    corrections.sort(key=lambda c: c['when'], reverse=True)
    return use, corrections[:150], earliest, files


def skill_use(use, name, plugin=None, origin='project'):
    """Usage for one copy of a skill. Plugin copies are invoked as plugin:skill."""
    if plugin:
        return use['skill'].get(plugin + ':' + name)
    if origin == 'account':
        return use['skill'].get('anthropic-skills:' + name) or use['skill'].get(name)
    return use['skill'].get(name)


# ---------- skills, commands, agents ----------

def collect_skills(P, plugins):
    skills = []

    def take(path, origin, plugin=None, kind='skill'):
        text = read_text(path, 200_000)
        fm = frontmatter(text)
        name = fm.get('name') or (path.parent.name if kind == 'skill' else path.stem)
        desc = fm.get('description', '')
        hidden = fm.get('disable-model-invocation', '').lower() == 'true'
        skills.append({'name': name, 'origin': origin, 'plugin': plugin, 'kind': kind,
                       'path': path, 'dir': path.parent if kind == 'skill' else path,
                       'desc': desc, 'hidden': hidden,
                       'tokens': 0 if hidden else toks(len(name) + len(desc) + 8),
                       'model': fm.get('model', ''), 'body': text})

    origin_of = {pl['name']: pl['origin'] for pl in plugins}
    for p in sorted((P / '.claude' / 'skills').glob('*/SKILL.md')):
        take(p, 'project')
    for p in sorted((CLAUDE / 'skills').glob('*/SKILL.md')):
        if p.parent.name != 'synced':
            take(p, 'user')
    for p in sorted((CLAUDE / 'skills' / 'synced').glob('*/*/SKILL.md')):
        take(p, 'account')
    for d, origin in ((P / '.claude' / 'commands', 'project'), (CLAUDE / 'commands', 'user')):
        for p in sorted(d.glob('**/*.md')):
            take(p, origin, kind='command')
    for pl in plugins:
        if not pl['enabled']:
            continue
        for p in sorted(pl['path'].glob('skills/*/SKILL.md')):
            take(p, 'plugin', pl['name'])
        for p in sorted(pl['path'].glob('commands/**/*.md')):
            take(p, 'plugin', pl['name'], kind='command')
    for s in skills:
        s['upload'] = s['origin'] == 'account' or origin_of.get(s['plugin']) == 'account'
    return skills


def collect_agents(P, plugins):
    agents = []
    srcs = [(P / '.claude' / 'agents', 'project', None), (CLAUDE / 'agents', 'user', None)]
    srcs += [(pl['path'] / 'agents', 'plugin', pl['name']) for pl in plugins if pl['enabled']]
    for d, origin, plugin in srcs:
        for p in sorted(d.glob('*.md')):
            fm = frontmatter(read_text(p, 100_000))
            name = fm.get('name') or p.stem
            agents.append({'name': name, 'origin': origin, 'plugin': plugin, 'path': p,
                           'desc_chars': len(fm.get('description', '')), 'model': fm.get('model', '')})
    return agents


def where(s, P):
    if s['origin'] == 'plugin':
        return 'plugin ' + s['plugin']
    if s['origin'] == 'account':
        return 'your claude.ai account'
    return rel(s['path'], P) if s['origin'] == 'project' else tilde(s['path'])


def build_corpus(P):
    """Text of files that might call a skill by name or path: skills, agents, rules, scripts, plists."""
    corpus = {}
    roots = [P / '.claude', P / 'scripts', CLAUDE / 'agents', CLAUDE / 'skills', CLAUDE / 'hooks']
    for name in ('CLAUDE.md', 'AGENTS.md'):
        if (P / name).exists():
            corpus[P / name] = read_text(P / name)
    for root in roots:
        if not root.is_dir():
            continue
        for dp, dns, fns in os.walk(root):
            dns[:] = [d for d in dns if d not in SKIP_DIRS and d != 'synced']
            for fn in fns:
                fp = Path(dp) / fn
                if fp.suffix in TEXT_EXT:
                    corpus[fp] = read_text(fp, 400_000)
    la = HOME / 'Library' / 'LaunchAgents'
    if la.is_dir():
        for fp in la.glob('*.plist'):
            corpus[fp] = read_text(fp, 100_000)
    return corpus


def callers(name, own_dir, corpus):
    pat = re.compile(r'(?:/|`|skills/|\bskill[: ]+)' + re.escape(name) + r'(?:\b|/|`)')
    hits = []
    for fp, text in corpus.items():
        try:
            if own_dir and Path(fp).is_relative_to(own_dir):
                continue
        except AttributeError:  # Python < 3.9
            if own_dir and str(fp).startswith(str(own_dir)):
                continue
        if name in text and pat.search(text):
            hits.append(fp)
    return hits


WORD = re.compile(r'[a-z]{4,}')
STOP = set('when with this that from your into used uses user asks wants like want also only '
           'what them they their have then than does each every make makes skill skills claude '
           'says said trigger triggers use triggered should would could about which other'.split())


def words(s):
    return {w for w in WORD.findall(s.lower()) if w not in STOP}


def skill_overrides(settings):
    out = {}
    for _scope, _p, d in settings:
        out.update(d.get('skillOverrides') or {})
    return out


def check_listing(P, skills, settings, servers):
    """The skill listing loads every session; past its budget, descriptions get dropped."""
    ov = skill_overrides(settings)
    listed, total, capped = set(), 0, []
    for s in skills:
        state = ov.get(s['name'], 'on')
        if s['hidden'] or state in ('off', 'user-invocable-only'):
            s['tokens'] = 0
            continue
        chars = len(s['name']) + 8 + (0 if state == 'name-only' else min(len(s['desc']), 1536))
        if state == 'name-only':
            s['tokens'] = toks(chars)
        total += chars
        listed.add(s['name'])
        if len(s['desc']) > 1536 and state != 'name-only':
            capped.append(s['name'])
    frac = 0.01
    for _scope, _p, d in settings:
        if isinstance(d.get('skillListingBudgetFraction'), (int, float)):
            frac = d['skillListingBudgetFraction']
    small, large = int(200_000 * frac * 4), int(1_000_000 * frac * 4)
    if total > small:
        add('skills', 'skill listing', 'About %s characters of skill names and descriptions load every session. '
            'Claude Code keeps %s%% of the context window for this list (roughly %s chars on a 200K model, %s on 1M) '
            'and drops descriptions of your least-used skills first, so those stop triggering.' % (
                '{:,}'.format(total), round(frac * 100, 2), '{:,}'.format(small), '{:,}'.format(large)),
            'Cut duplicates and unused skills first, then set rarely used ones to "name-only". '
            'Run /context to see what survived.', risk='high' if total > large else 'med', kind='budget')
    if capped:
        add('skills', '%d descriptions over 1,536 chars' % len(capped), 'Cut off at the cap: %s.' % ', '.join(capped[:10]),
            'Put the key use case first and shorten.', kind='heavy')
    names = {s['name'] for s in skills}
    for name, state in sorted(ov.items()):
        if name not in names:
            add('skills', name, 'skillOverrides sets it to "%s" but no skill by that name loads.' % state,
                'Delete the stale entry.', kind='stale-override')
    # retired here, still shipped from somewhere else
    live_here = {s['name'] for s in skills if s['origin'] in ('project', 'user')}
    retired = {p.parent.name for p in P.glob('archive/**/SKILL.md')} - live_here
    for s in skills:  # an official plugin replacing an archived copy is fine; your own uploads are not
        if s['name'] in retired and s['upload']:
            add('skills', s['name'], 'Archived in this project but still loaded from %s.' % where(s, P),
                'Remove it at that source too.', risk='med', kind='retired-still-loaded')
    # skills that lean on a connector that is off or broken here
    if servers:
        down = {s['key']: s for s in servers if s['state'] in ('disabled', 'needs_auth', 'failed')}
        for s in skills:
            if s['origin'] not in ('project', 'user'):
                continue
            hits = {norm_key(k) for k in re.findall(r'mcp__([A-Za-z0-9_-]+?)__', s['body'])}
            bad = [down[k]['name'] + ' (' + down[k]['state'].replace('_', ' ') + ')' for k in hits if k in down]
            if bad:
                add('skills', s['name'], 'Calls connector(s) that are not usable here: %s.' % ', '.join(sorted(bad)),
                    'Reconnect the connector, or retire the skill if you no longer run it.', kind='needs-connector')


def check_skills(P, skills, use, corpus, days):
    by_name = collections.defaultdict(list)
    for s in skills:
        by_name[s['name']].append(s)
    # same skill loaded from more than one place
    for name, copies in sorted(by_name.items()):
        if len(copies) < 2:
            continue
        rows = []
        for c in copies:
            u = skill_use(use, name, c['plugin'], c['origin']) or {}
            rows.append('%s (%s runs, edited %s)' % (where(c, P), u.get('n', 0), fmt_when(c['path'].stat().st_mtime)))
        bodies = {hashlib.sha1(re.sub(r'\s+', ' ', c['body']).encode()).hexdigest() for c in copies}
        drift = ' The copies differ, so an older one can trigger instead of the one you maintain.' if len(bodies) > 1 else ''
        add('skills', name, 'Loaded %d times: %s.%s' % (len(copies), '; '.join(rows), drift),
            'Keep the copy you use and remove the others at their source (plugin, account upload or folder).',
            risk='med' if drift else 'low', kind='duplicate',
            source=', '.join(sorted({c['origin'] for c in copies})))
    # unused, heavy, dead references: per skill for copies you own; account copies as one group
    acct_idle, acct_n = [], 0
    for s in skills:
        if s['kind'] != 'skill':
            continue
        u = skill_use(use, s['name'], s['plugin'], s['origin']) or {}
        owned = s['origin'] in ('project', 'user')
        if s['origin'] == 'account':
            acct_n += 1
            if not u.get('n'):
                acct_idle.append(s['name'])
        if owned and not u.get('n') and not s['hidden'] and s['tokens']:
            refs = callers(s['name'], s['dir'], corpus)
            ev = 'No recorded run in the last %d days. Listing costs about %d tokens in every session.' % (
                days, s['tokens'])
            if refs:
                ev += ' Referenced by %d file(s), e.g. %s.' % (len(refs), ', '.join(rel(r, P) for r in refs[:3]))
            add('skills', s['name'], ev, 'Set it to "name-only" or "user-invocable-only" in skillOverrides, or archive it.',
                risk='med' if refs else 'low', kind='unused', source=where(s, P),
                undo='Set it back to "on" in skillOverrides, or move the folder back from the archive.')
    if acct_idle:
        add('skills', '%d of %d skills synced from your claude.ai account' % (len(acct_idle), acct_n),
            'No recorded run in Claude Code in the last %d days: %s.' % (days, ', '.join(sorted(acct_idle))),
            'If they exist for the claude.ai app, hide them here with skillOverrides; if not, remove them on claude.ai.',
            kind='account-unused')
    picked = {k: v for k, v in use['skill'].items() if v['model']}
    if picked:
        add('skills', '%d skills Claude chose on its own' % len(picked),
            'The prompts each one fired on are in corrections.jsonl (type "fired_on"): %s.' % ', '.join(
                '%s %d' % (k, v['model']) for k, v in sorted(picked.items(), key=lambda kv: -kv[1]['model'])[:15]),
            'Read the prompts. Where a skill fired on work it was not meant for, make it slash-only or tighten '
            'its description.', kind='review-firing')
    for s in skills:
        if s['kind'] != 'skill':
            continue
        owned = s['origin'] in ('project', 'user')
        if owned and len(s['desc']) > 900:
            add('skills', s['name'], 'Description is %d characters, loaded into every session.' % len(s['desc']),
                'Shorten the description to the triggering conditions.', kind='heavy', source=where(s, P))
        if owned:
            dead = dead_refs(s['body'], s['dir'], P)
            if dead:
                add('skills', s['name'], 'Mentions %d path(s) that do not exist here: %s. Some may be files '
                    'another step creates.' % (len(dead), ', '.join(sorted(dead)[:5])),
                    'Fix the ones it reads; leave the ones it creates.', kind='dead-ref', source=where(s, P))
    # overlapping skills (different names, similar job)
    owned = [s for s in skills if s['kind'] == 'skill' and s['desc']]
    seen_pairs = set()
    names = {}
    for s in owned:
        names.setdefault(s['name'], s)
    uniq = list(names.values())
    wsets = {s['name']: words(s['desc']) for s in uniq}
    for i, a in enumerate(uniq):
        for b in uniq[i + 1:]:
            wa, wb = wsets[a['name']], wsets[b['name']]
            if not wa or not wb or (a['plugin'] and a['plugin'] == b['plugin']):
                continue  # one vendor's variants overlap by design
            jac = len(wa & wb) / len(wa | wb)
            same_name_words = set(a['name'].split('-')) == set(b['name'].split('-'))
            if jac >= 0.42 or same_name_words:
                key = tuple(sorted((a['name'], b['name'])))
                if key in seen_pairs:
                    continue
                seen_pairs.add(key)
                ua = skill_use(use, a['name'], a['plugin'], a['origin']) or {}
                ub = skill_use(use, b['name'], b['plugin'], b['origin']) or {}
                add('skills', '%s + %s' % key,
                    'Descriptions overlap (%d%% shared words). Runs: %s %d, %s %d.' % (
                        round(jac * 100), a['name'], ua.get('n', 0), b['name'], ub.get('n', 0)),
                    'Decide which one owns the job; merge or retire the other (a planned change, not a quick fix).',
                    kind='overlap', reversible=True)


def check_agents(P, agents, use, days, corpus=None):
    for a in agents:
        key = (a['plugin'] + ':' + a['name']) if a['plugin'] else a['name']
        u = use['agent'].get(key) or use['agent'].get(a['name']) or {}
        if a['origin'] in ('project', 'user') and not u.get('n'):
            refs = callers(a['name'], a['path'], corpus) if corpus else []
            named = [r for r in refs if Path(r).name in ('CLAUDE.md', 'AGENTS.md')]
            ev = 'No recorded run in the last %d days. Its description (%d chars) is listed in every session.' % (
                days, a['desc_chars'])
            if named:
                ev += ' Named in %s, so it is part of how this workspace routes work.' % ', '.join(rel(r, P) for r in named)
            elif refs:
                ev += ' Referenced by %d file(s), e.g. %s.' % (len(refs), ', '.join(rel(r, P) for r in refs[:3]))
            add('agents', a['name'], ev,
                'Keep it; it is on call by design.' if named else 'Archive it, or keep it if it is seasonal.',
                kind='on-call' if named else 'unused', source=rel(a['path'], P))
        if a['desc_chars'] > 1500:
            add('agents', a['name'], 'Description is %d characters and loads into every session.' % a['desc_chars'],
                'Shorten it, or turn off the plugin that ships it.', kind='heavy',
                source=a['plugin'] and 'plugin ' + a['plugin'] or rel(a['path'], P))


def check_plugins(plugins, skills, agents, use, days):
    for key, scopes in TWICE:
        add('plugins', key, 'Installed at more than one scope (%s), so its skills list twice.' % ', '.join(scopes),
            'Keep one: claude plugin uninstall %s --scope project (or the scope you do not want).' % key,
            risk='med', kind='twice', undo='claude plugin install %s --scope project' % key)
    for pl in plugins:
        if not pl['enabled']:
            continue
        mine = [s for s in skills if s['plugin'] == pl['name']]
        ags = [a for a in agents if a['plugin'] == pl['name']]
        runs = sum((skill_use(use, s['name'], s['plugin']) or {}).get('n', 0) for s in mine)
        runs += sum((use['agent'].get(pl['name'] + ':' + a['name']) or {}).get('n', 0) for a in ags)
        cost = sum(s['tokens'] for s in mine)
        if (mine or ags) and runs == 0:
            where_ = 'your claude.ai account (%s)' % pl['marketplace'] if pl['origin'] == 'account' else pl['key']
            add('plugins', pl['name'], 'Ships %d skill(s) and %d agent(s); none ran in the last %d days. '
                'Listing costs about %d tokens per session. Source: %s.' % (len(mine), len(ags), days, cost, where_),
                'Disable it (claude.ai Customize for account plugins, /plugin for installed ones).',
                kind='unused', undo='Re-enable it in the same place.')


# ---------- connectors ----------

def claude_bin():
    """The claude CLI. The desktop app's shell may not have it on PATH, so try where the app says it is."""
    for c in (shutil.which('claude'), os.environ.get('CLAUDE_CODE_EXECPATH'), str(HOME / '.local' / 'bin' / 'claude'),
              str(HOME / '.local' / 'bin' / 'claude.exe')):
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    return None


def mcp_list(P, skip):
    if skip:
        NOT_CHECKED.append('Connector status (--skip-mcp)')
        return None
    exe = claude_bin()
    if not exe:
        NOT_CHECKED.append('Connector status: the claude command is not on PATH; run /mcp in a session')
        return None
    code, out = run([exe, 'mcp', 'list'], cwd=P, timeout=240)
    if code is None:
        NOT_CHECKED.append('Connector status: claude mcp list timed out')
        return None
    servers = []
    for line in out.splitlines():
        if ': ' not in line or ' - ' not in line:
            continue
        name, rest = line.split(': ', 1)
        target, status = rest.rsplit(' - ', 1)
        st = status.lower()
        if 'needs authentication' in st:
            state = 'needs_auth'
        elif 'failed' in st or '✘' in status:
            state = 'failed'
        elif 'disabled' in st or '⊘' in status:
            state = 'disabled'
        elif 'fetch failed' in st or 'timed out' in st:
            state = 'degraded'
        elif 'connected' in st:
            state = 'connected'
        else:
            state = 'unknown'
        t = target.strip().split(' ')[0]
        host, secret = 'local', False
        if t.startswith('http'):
            u = urlparse(t)
            host = u.hostname or '?'
            tail = u.path + '?' + u.query
            secret = bool(re.search(r'(fc-|sk-|pk_|key=|token=|apikey|api_key)', tail, re.I) or
                          re.search(r'/[A-Za-z0-9_-]*(?=[A-Za-z0-9_-]*\d)(?=[A-Za-z0-9_-]*[a-zA-Z])[A-Za-z0-9_-]{28,}', u.path))
        if name.startswith('claude.ai '):
            kind, key = 'account', 'claude_ai_' + name[len('claude.ai '):]
        elif name.startswith('plugin:'):
            kind, key = 'plugin', name.replace(':', '_')
        else:
            kind, key = 'local', name
        servers.append({'name': name, 'kind': kind, 'state': state, 'host': host,
                        'secret_in_url': secret, 'key': norm_key(key), 'detail': status.strip()[:90]})
    return servers


def vendor_of(name):
    n = name.lower()
    n = re.sub(r'^claude\.ai\s+', '', n)
    if n.startswith('plugin:'):
        n = n.split(':')[-1]
    n = re.sub(r'\s*\(\d+\)$', '', n)
    n = re.sub(r'[^a-z0-9]', '', n)
    return re.sub(r'(mcp|server)$', '', n)


def check_connectors(servers, use, settings, days):
    if servers is None:
        return
    used = {norm_key(k): v for k, v in use['mcp'].items()}
    by_vendor = collections.defaultdict(list)
    for s in servers:
        by_vendor[vendor_of(s['name'])].append(s)
        u = used.get(s['key'], {})
        runs = u.get('n', 0)
        if s['state'] in ('needs_auth', 'failed', 'degraded'):
            label = {'needs_auth': 'needs signing in again', 'failed': 'fails to connect',
                     'degraded': 'connects but its tools did not load'}[s['state']]
            add('connectors', s['name'], '%s (%s). %d call(s) in the last %d days.' % (
                label.capitalize(), s['detail'], runs, days),
                'Reconnect it with /mcp if you use it; otherwise remove it.' if runs else
                'Remove it, or disable it for this project with /mcp. Nothing used it recently.',
                risk='med', kind='broken', reversible=True)
        elif s['state'] == 'connected' and runs == 0:
            add('connectors', s['name'], 'Connected and loaded into every session here, but no calls in the '
                'last %d days.' % days,
                'Disable it for this project with /mcp disable (reversible), or remove it.',
                kind='unused', undo='/mcp enable')
        if s['state'] == 'connected' and u.get('errors') and u['errors'] >= 3:
            add('connectors', s['name'], '%d of %d calls returned an error in the last %d days.' % (
                u['errors'], runs, days),
                'Check the error type before blaming the connector (expired login, quota, bad input).',
                risk='med', kind='errors')
        if s['secret_in_url']:
            add('connectors', s['name'], 'Its URL appears to carry an API key (the URL is not shown here).',
                'Treat the connector URL as a secret: keep it off screen recordings and rotate the key if it has been shown.',
                risk='high', kind='secret', reversible=True)
    disabled = [s for s in servers if s['state'] == 'disabled' and not used.get(s['key'], {}).get('n')]
    if disabled:
        add('connectors', '%d switched-off connectors' % len(disabled),
            'Installed but disabled for this project: %s.' % ', '.join(s['name'] for s in disabled),
            'Leave them off here. If you use them in no project, remove them from claude.ai Customize > Connectors.',
            kind='disabled')
    for v, group in by_vendor.items():
        live = [s for s in group if s['state'] != 'disabled']
        if len(group) > 1 and live:
            add('connectors', '%s (%d copies)' % (v, len(group)),
                'Same service connected more than once: %s.' % '; '.join(
                    '%s [%s, %d calls]' % (s['name'], s['state'], used.get(s['key'], {}).get('n', 0)) for s in group),
                'Keep one (usually the one that works and is used) and remove the rest.',
                kind='duplicate')
    # write-capable tools that are pre-approved
    for scope, p, d in settings:
        for rule in (d.get('permissions') or {}).get('allow') or []:
            if not rule.startswith('mcp__'):
                continue
            parts = rule.split('__')
            tool = '__'.join(parts[2:]) if len(parts) > 2 else ''
            if tool in ('', '*') or WRITE_VERBS.search(tool):
                add('permissions', rule, 'Allowed without asking in %s settings%s.' % (
                    scope, ' (covers every tool on that server, including ones that send, change or delete)'
                    if tool in ('', '*') else ''),
                    'Narrow it to read tools, or move it to "ask".', risk='high', kind='write-allowed')


# ---------- scheduled work ----------

plugins_cache = []


def log_tail(paths):
    """Last change and error lines in a job's log files. Normal output after the last error means a later run worked."""
    log_m, errs, err_line, recovered, last_ok = 0, 0, '', False, ''
    for lp in filter(None, paths):
        lp = Path(os.path.expanduser(lp))
        if lp.exists():
            log_m = max(log_m, lp.stat().st_mtime)
            tail = read_text(lp, 5_000_000).splitlines()[-120:]
            bad_at = [i for i, l in enumerate(tail) if re.search(r'(Traceback|Error|ERROR|FAILED|failed)', l)]
            errs += len(bad_at)
            err_line = err_line or (tail[bad_at[-1]].strip()[:140] if bad_at else '')
            if bad_at:
                later = [l for l in tail[bad_at[-1] + 1:] if l.strip() and not re.match(
                    r'(\s|File |Traceback|During handling|raise |[A-Za-z_.]*(Error|Exception)\b)', l)]
                recovered = recovered or bool(later)
                last_ok = later[-1].strip()[:100] if later else last_ok
    return log_m, errs, err_line, recovered, last_ok


def job_findings(label, every, seen, unseen, tail, models, catalog):
    """What every scheduled job is checked for, whatever runs it. `seen` is the last sign it ran."""
    _log_m, errs, err_line, recovered, last_ok = tail
    if errs and recovered:
        add('scheduled', label, '%d error line(s) in the last 120 log lines, but the output after them looks '
            'normal ("%s"), so a later run worked.' % (errs, last_ok.replace(str(HOME), '~')),
            'Nothing to do unless it starts failing again.', kind='recovered')
    elif errs:
        add('scheduled', label, '%d error line(s) in the last 120 log lines, latest: "%s".' % (
            errs, err_line.replace(str(HOME), '~')),
            'Read the log and fix the cause, or pause it.', risk='med', kind='errors')
    if every and seen and (NOW - seen) > 2 * every + DAY:
        add('scheduled', label, 'Should run about every %s but %s %d days.' % (
            ('%dh' % (every // 3600)) if every < 2 * DAY else ('%dd' % (every // DAY)), unseen, age_days(seen)),
            'Check it is still doing its job; pause it if nobody reads its output.', risk='med', kind='stale')
    for m in models:
        st = model_status(m, catalog) if catalog[0] else None
        if st:
            add('scheduled', label, 'Runs on %s, which is %s.' % (m, st),
                'Move it to a current model; simple jobs can use a smaller one.', kind='old-model')


# Every task outside \Microsoft\, as JSON. Encoded so no quoting survives the trip through the shell.
PS_TASKS = r"""
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$ErrorActionPreference = 'SilentlyContinue'
$epoch = [datetime]'1970-01-01'
$rows = @(Get-ScheduledTask | Where-Object { $_.TaskPath -notlike '\Microsoft\*' } | ForEach-Object {
  $i = $_ | Get-ScheduledTaskInfo
  [pscustomobject]@{
    name = $_.TaskPath + $_.TaskName
    state = [string]$_.State
    run = (@($_.Actions | ForEach-Object { ([string]$_.Execute + ' ' + [string]$_.Arguments).Trim() }) -join ' | ')
    triggers = @($_.Triggers | ForEach-Object { $_.CimClass.CimClassName })
    repeat = @($_.Triggers | ForEach-Object { [string]$_.Repetition.Interval })
    last = if ($i -and $i.LastRunTime -and $i.LastRunTime.Year -gt 2000) { [int64](($i.LastRunTime.ToUniversalTime() - $epoch).TotalSeconds) } else { 0 }
    result = if ($i) { [int64]$i.LastTaskResult } else { $null }
  }
})
ConvertTo-Json -InputObject $rows -Compress -Depth 4
"""
# Last results that are not failures: success, ready, running, disabled, not run yet, no more runs, triggers unset.
TASK_OK = {0, 0x41300, 0x41301, 0x41302, 0x41303, 0x41304, 0x41305}


def iso_seconds(s):
    m = re.fullmatch(r'P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?', s or '')
    if not m or not any(m.groups()):
        return None
    d, h, mi, se = (int(x or 0) for x in m.groups())
    return d * DAY + h * 3600 + mi * 60 + se


def check_task_scheduler(catalog):
    """Windows: Task Scheduler tasks that run Claude or something in the home folder. Read-only."""
    ps = shutil.which('powershell') or shutil.which('pwsh')
    if not ps:
        NOT_CHECKED.append('Windows Task Scheduler: PowerShell not found')
        return []
    script = base64.b64encode(PS_TASKS.encode('utf-16-le')).decode('ascii')
    _code, out = run([ps, '-NoProfile', '-NonInteractive', '-EncodedCommand', script], timeout=180)
    try:
        tasks = json.loads(out.strip().lstrip('﻿') or '[]')
    except ValueError:
        NOT_CHECKED.append('Windows Task Scheduler: could not read the task list')
        return []
    if isinstance(tasks, dict):
        tasks = [tasks]
    jobs, other, home = [], [], str(HOME).lower()
    for t in tasks:
        label, cmd = (t.get('name') or '?').strip('\\'), t.get('run') or ''
        if 'claude' not in cmd.lower() and home not in cmd.lower():
            other.append(label)
            continue
        trig = ' '.join(t.get('triggers') or [])
        every = min(filter(None, (iso_seconds(x) for x in t.get('repeat') or [])), default=None) or (
            DAY if 'Daily' in trig else 7 * DAY if 'Weekly' in trig else 30 * DAY if 'Monthly' in trig else None)
        logs = [a or b for a, b in re.findall(r'\d?>>?\s*(?:"([^"]+)"|([^\s"|&<>]+))', cmd)]
        tail = log_tail(logs)
        last = t.get('last') or 0
        job = {'label': label, 'where': 'Task Scheduler', 'state': t.get('state'), 'last': fmt_when(last),
               'last_result': t.get('result'), 'every_s': every, 'log_age_days': age_days(tail[0]),
               'errors_in_log_tail': tail[1], 'models': sorted(set(MODEL_ID.findall(cmd)))}
        jobs.append(job)
        if t.get('state') == 'Disabled':
            add('scheduled', label, 'Set up in Task Scheduler but disabled, so it never runs.',
                'Delete the task if it is retired; enable it again if it should run.',
                kind='switched-off', undo='Enable it again in Task Scheduler.')
            continue
        res = t.get('result')
        if isinstance(res, int) and res not in TASK_OK:
            add('scheduled', label, 'Last run ended with result 0x%X.' % (res & 0xFFFFFFFF),
                'Read its log and fix the cause, or pause it.', risk='med', kind='failing')
        job_findings(label, every, max(last, tail[0]), 'it has not run in', tail, job['models'], catalog)
    if other:
        add('scheduled', '%d other scheduled tasks' % len(other),
            'Not part of your AI setup (app updaters and helpers): %s.' % ', '.join(other[:12]),
            'Nothing to do here; listed so you know they exist.', kind='info')
    return jobs


def check_scheduled(P, catalog, skills):
    jobs = []
    if platform.system() == 'Darwin':
        _code, out = run(['launchctl', 'list'])
        loaded = {}
        for line in out.splitlines()[1:]:
            parts = line.split('\t')
            if len(parts) == 3:
                loaded[parts[2]] = (parts[0], parts[1])
        _code, out = run(['launchctl', 'print-disabled', 'gui/%d' % os.getuid()])
        switched_off = set(re.findall(r'"([^"]+)"\s*=>\s*(?:true|disabled)', out))
        other = []
        for plist in sorted((HOME / 'Library' / 'LaunchAgents').glob('*.plist')):
            try:
                with open(plist, 'rb') as fh:
                    d = plistlib.load(fh)
            except Exception:
                continue
            label = d.get('Label', plist.stem)
            args = [str(a) for a in (d.get('ProgramArguments') or ([d['Program']] if d.get('Program') else []))]
            argstr = ' '.join(args)
            mine = ('claude' in argstr.lower()) or (str(HOME) in argstr and '/Library/' not in argstr)
            if not mine:
                other.append(label)
                continue
            every = d.get('StartInterval')
            cal = d.get('StartCalendarInterval')
            if not every and cal:
                c = cal[0] if isinstance(cal, list) else cal
                every = 7 * DAY if 'Weekday' in c else (30 * DAY if 'Day' in c else DAY)
            tail = log_tail([d.get('StandardOutPath'), d.get('StandardErrorPath')])
            log_m, errs = tail[0], tail[1]
            state = loaded.get(label)
            job = {'label': label, 'loaded': bool(state), 'last_exit': state[1] if state else None,
                   'every_s': every, 'keepalive': bool(d.get('KeepAlive')), 'log_age_days': age_days(log_m),
                   'errors_in_log_tail': errs, 'models': sorted(set(MODEL_ID.findall(argstr)))}
            jobs.append(job)
            if not state:
                why = 'switched off (launchctl disabled)' if label in switched_off else 'not loaded'
                add('scheduled', label, 'Installed in LaunchAgents but %s, so it never runs.' % why,
                    'Archive the plist if it is retired; load it again if it should run.',
                    kind='switched-off', undo='Move the plist back and launchctl bootstrap it.')
                continue
            if state[1] not in ('0', '-') and not job['keepalive']:
                add('scheduled', label, 'Last run exited with status %s.' % state[1],
                    'Read its log and fix the cause, or pause it.', risk='med', kind='failing')
            job_findings(label, every, log_m, 'its log has not changed in', tail, job['models'], catalog)
        if other:
            add('scheduled', '%d app background jobs' % len(other),
                'Not part of your AI setup (app updaters and helpers): %s.' % ', '.join(other[:12]),
                'Nothing to do here; listed so you know they exist.', kind='info')
    elif platform.system() == 'Windows':
        jobs += check_task_scheduler(catalog)
    else:
        NOT_CHECKED.append('macOS LaunchAgents (not a Mac)')
        if shutil.which('systemctl'):
            code, out = run(['systemctl', '--user', 'list-timers', '--all', '--no-pager'])
            if out.strip():
                add('scheduled', 'systemd user timers', out.strip()[:600], 'Review each timer.', kind='info')
    code, out = run(['crontab', '-l']) if platform.system() != 'Windows' else (None, '')
    cron = [l for l in out.splitlines() if l.strip() and not l.lstrip().startswith('#')]
    if cron:
        add('scheduled', 'crontab (%d lines)' % len(cron),
            'Cron jobs cannot report success or failure here: %s' % ' | '.join(l[:90] for l in cron[:6]),
            'Check each still has a job to do and someone reads its output.', kind='info')
    # Desktop app tasks: one folder per task; each run is a session file carrying scheduledTaskId.
    runs = collections.defaultdict(list)
    for sub in ('claude-code-sessions', 'local-agent-mode-sessions'):
        for f in app_sessions(sub):
            d = read_json(f) or {}
            if d.get('scheduledTaskId'):
                try:
                    last = float(d.get('lastActivityAt') or d.get('createdAt') or 0) / 1000
                except (TypeError, ValueError):
                    last = 0
                runs[d['scheduledTaskId']].append((last, d.get('model') or ''))
    loaded = {s['name'] for s in skills} | {'%s:%s' % (s['plugin'], s['name']) for s in skills if s['plugin']}
    uploads = {s['plugin']: s for s in skills if s['plugin'] and s['upload']}
    docs = [HOME / 'Documents'] + ([Path(os.environ['OneDrive']) / 'Documents'] if os.environ.get('OneDrive') else [])
    for where_, base in [('Code tab', CLAUDE / 'scheduled-tasks')] + [('Cowork', d / 'Claude' / 'Scheduled') for d in docs]:
        for d in sorted(base.glob('*/')) if base.is_dir() else []:
            body = read_text(d / 'SKILL.md', 50_000)
            r = sorted(runs.get(d.name, []), reverse=True)
            last = r[0][0] if r else 0
            models = sorted({m.split('[')[0] for _t, m in r[:10] if m})
            jobs.append({'label': d.name, 'where': where_, 'runs': len(r), 'last': fmt_when(last), 'models': models})
            label = '%s (%s task)' % (d.name, where_)
            if not r or NOW - last > 30 * DAY:
                add('scheduled', label, 'Last run %s (%d run(s) on record).' % (fmt_when(last), len(r)),
                    'Pause or delete it in the app if it is retired; if it should run, find out why it stopped.',
                    kind='stale')
            for m in models:
                st = model_status(m, catalog) if catalog[0] else None
                if st:
                    add('scheduled', label, 'Recent runs used %s, which is %s.' % (m, st),
                        'Move it to a current model; simple jobs can use a smaller one.', kind='old-model')
            for ref in re.findall(r'(?<![\w/])/([a-z0-9][a-z0-9-]*(?::[a-z0-9-]+)?)', body):
                plugin = ref.split(':')[0] if ':' in ref else None
                if ':' in ref and ref not in loaded:
                    add('scheduled', label, 'Runs /%s, which does not load any more.' % ref,
                        'Point it at the current skill or retire the task.', risk='med', kind='missing-skill')
                elif plugin in uploads:
                    add('scheduled', label, 'Runs /%s from your own upload "%s" (updated %s), not the copy you '
                        'maintain.' % (ref, plugin, str(next((p['updated'] for p in plugins_cache if p['name'] == plugin), '?'))[:10]),
                        'Point it at the current skill.', risk='med', kind='old-copy')
    NOT_CHECKED.append('Cloud routines: ask Claude to list them (RemoteTrigger list) or run /schedule list')
    return jobs


# ---------- hooks and permissions ----------

def check_hooks(P, settings, use, days=30):
    configured = 0
    configured_cmds = set()
    for scope, p, d in settings:
        for event, groups in (d.get('hooks') or {}).items():
            for g in groups or []:
                for h in g.get('hooks') or []:
                    configured += 1
                    cmd = str(h.get('command') or '')
                    configured_cmds.add(cmd)
                    if 'CLAUDE_PLUGIN_ROOT' in cmd:
                        continue
                    # Spaces inside quotes and in the two folders stay \0 until the script paths are split
                    # out, so "C:\...\Client Projects" stays one path; function replacements keep \ literal.
                    keep = lambda s: s.replace(' ', '\0')
                    cmd = re.sub(r'"([^"]*)"|\'([^\']*)\'', lambda m: keep(m.group(1) or m.group(2) or ''), cmd)
                    cmd = re.sub(r'\$\{?CLAUDE_PROJECT_DIR\}?', lambda _m: keep(str(P)), cmd)
                    cmd = re.sub(r'\$\{?HOME\}?', lambda _m: keep(str(HOME)), cmd).replace('"', '').replace("'", '')
                    for tok in re.findall(r'[^\s;|&()]+\.(?:py|sh|js|mjs|ts|rb)(?=\s|$)', cmd):
                        tok = tok.replace('\0', ' ')
                        tp = Path(os.path.expanduser(tok))
                        if not tp.is_absolute():
                            tp = P / tp
                        if not tp.exists():
                            add('hooks', '%s hook (%s settings)' % (event, scope),
                                'Runs a script that does not exist: %s.' % tilde(tok),
                                'Remove the hook or restore the script.', risk='med', kind='missing-script')
    merged = {}
    for (name, cmd), h in use['hook'].items():  # one hook reports under several event names
        key = cmd or name
        m = merged.setdefault(key, {'n': 0, 'fail': 0, 'ms': [], 'out': [], 'names': set(),
                                    'codes': collections.Counter(), 'last_fail': 0})
        m['last_fail'] = max(m['last_fail'], h.get('last_fail', 0))
        for k in ('n', 'fail'):
            m[k] += h[k]
        m['codes'].update(h.get('codes') or {})
        m['ms'] += h['ms']
        m['out'] += h['out']
        m['names'].add(name.split(':')[0])
    for cmd, h in merged.items():
        name = '/'.join(sorted(h['names']))
        cmd = cmd if cmd != name else ''
        ms = sorted(h['ms'])
        p50 = ms[len(ms) // 2] if ms else 0
        mx = ms[-1] if ms else 0
        avg_out = sum(h['out']) / len(h['out']) if h['out'] else 0
        label = name + ((' · ' + cmd.split('/')[-1][:50]) if cmd else '')
        script = re.findall(r'[^\s/"\']+\.(?:py|sh|js|mjs|ts|rb)', cmd)
        fixed = script and cmd not in configured_cmds and any(script[0] in c for c in configured_cmds)
        if h['fail'] and fixed:
            add('hooks', label, 'Failed %d times, last on %s; the command has changed since and its script now '
                'resolves. The old failures age out of the %d-day window.' % (h['fail'], fmt_when(h['last_fail']), days),
                'Nothing to do; check it stays clean on the next scan.', kind='fixed')
            continue
        if h['fail']:
            why = ''
            if h['codes'].get('127'):
                why = (' Exit 127 means the script was not found, usually a relative path that breaks once the '
                       'shell moves to another folder, so the hook silently stops guarding there.')
            add('hooks', label, 'Failed %d times in the window (exit codes: %s). Successful runs are not logged, so '
                'this is a floor.%s' % (h['fail'], ', '.join('%s x%d' % kv for kv in h['codes'].most_common(3)), why),
                'Fix the path (use $CLAUDE_PROJECT_DIR) or remove the hook. A safety hook that fails open is worse '
                'than none, because you think you are covered.', risk='high' if 'guard' in label.lower() else 'med',
                kind='failing')
        if p50 > 1000 or mx > 8000:
            add('hooks', label, 'Typical run %.1fs, slowest %.1fs over %d runs.' % (p50 / 1000, mx / 1000, h['n']),
                'Make it faster or narrow its matcher.', kind='slow')
        if avg_out > 4000 and 'SessionStart' in name:
            add('hooks', label, 'Adds about %d tokens to the start of every session.' % toks(avg_out),
                'Inject less; point at files Claude can read on demand.', kind='heavy')
    return configured


def check_permissions(settings):
    for scope, p, d in settings:
        perm = d.get('permissions') or {}
        if d.get('skipDangerousModePermissionPrompt'):
            add('permissions', '%s settings' % scope, 'skipDangerousModePermissionPrompt is on.',
                'Turn it off unless you run fully sandboxed.', risk='high', kind='bypass')
        if perm.get('defaultMode') == 'bypassPermissions':
            add('permissions', '%s settings' % scope, 'Default permission mode is bypassPermissions.',
                'Use auto mode instead.', risk='high', kind='bypass')
        for rule in perm.get('allow') or []:
            if rule in ('Bash', 'Bash(*)', 'Bash(*:*)', 'mcp__*', '*'):
                add('permissions', rule, 'Allowed without asking in %s settings.' % scope,
                    'Replace with the specific commands you run often (/fewer-permission-prompts helps).',
                    risk='high', kind='broad-allow')


# ---------- instructions, memory, context layer ----------

def first_seg_exists(ref, base, P):
    seg = ref.split('/')[0]
    if seg in ('', '.', '..', '~'):
        return True
    return (base / seg).exists() or (P / seg).exists()


def dead_refs(text, base, P, skill_dirs=()):
    """Paths a file points at that do not exist. Skips runtime outputs and placeholders."""
    out = set()
    cands = set(m.group(1) for m in re.finditer(r'\]\(([^)\s]+)\)', text))
    stripped = re.sub(r'```.*?```', ' ', text, flags=re.S)
    for m in re.finditer(r'`([^`\n]{2,200})`', stripped):
        s = m.group(1).strip()
        if ' ' not in s and '/' in s:
            cands.add(s)
    for block in re.findall(r'```.*?```', text, flags=re.S):
        for tok in re.findall(r'(?<![\w$])((?:\./|\.claude/|~/|[A-Za-z0-9_.-]+/)[A-Za-z0-9_./-]+\.[A-Za-z0-9]{1,5})\b', block):
            cands.add(tok)
    for ref in cands:
        r = ref.split('#')[0].split('?')[0]
        r = re.sub(r':\d+(-\d+)?$', '', r).rstrip('.,;:)\'"')
        r = r.replace('%20', ' ')
        if not r or re.match(r'^[a-z][a-z0-9+.-]*:', r) or any(c in r for c in '<>{}$*|[]'):
            continue
        if r.startswith(TRANSIENT) or r.lstrip('./').split('/')[0] in OUTPUT_SEGS:
            continue
        if r.startswith('~'):
            paths = [Path(os.path.expanduser(r))]
        elif r.startswith('/'):
            if not r.startswith(str(HOME)):
                continue
            paths = [Path(r)]
        else:
            if not first_seg_exists(r, base, P):
                continue
            paths = [base / r, P / r] + [d / r for d in skill_dirs]
        if not any(p.exists() for p in paths):
            out.add(r)
    return out


def instruction_files(P):
    files = []
    for name, always in (('CLAUDE.md', True), ('CLAUDE.local.md', True), ('AGENTS.md', False)):
        if (P / name).exists():
            files.append((P / name, always))
    if (CLAUDE / 'CLAUDE.md').exists():
        files.append((CLAUDE / 'CLAUDE.md', True))
    for d in (P / '.claude' / 'rules', CLAUDE / 'rules'):
        for f in sorted(d.glob('**/*.md')):
            files.append((f, not frontmatter(read_text(f, 20_000)).get('paths')))
    for root, dns, fns in os.walk(P):
        if Path(root) != P and ('.git' in dns or '.git' in fns):
            dns[:] = []  # a repo cloned inside the workspace keeps its own instructions
            continue
        dns[:] = [x for x in dns if x not in SKIP_DIRS and not x.startswith('.')]
        if Path(root) != P and 'CLAUDE.md' in fns:
            files.append((Path(root) / 'CLAUDE.md', False))
    # @imports from always-loaded files load too
    for f, always in list(files):
        if not always:
            continue
        for imp in re.findall(r'(?m)^\s*@([^\s]+)', read_text(f)):
            ip = Path(os.path.expanduser(imp)) if imp.startswith('~') else (f.parent / imp)
            if ip.exists() and all(ip != x for x, _ in files):
                files.append((ip, True))
    return files


def check_instructions(P):
    files = instruction_files(P)
    skill_dirs = [d for d in (P / '.claude' / 'skills').glob('*') if d.is_dir()]
    always_chars = 0
    paras = collections.defaultdict(set)
    for f, always in files:
        text = read_text(f)
        lines = text.count('\n') + 1
        if always:
            always_chars += len(text)
            for para in re.split(r'\n\s*\n', text):
                n = re.sub(r'\s+', ' ', para).strip()
                if len(n) > 140:
                    paras[n].add(f)
        if always and lines > 200:
            add('instructions', rel(f, P), '%d lines, loaded into every session (guidance: under 200).' % lines,
                'Move detail that only some tasks need into path-scoped rules, skills or files read on demand.',
                kind='long')
        dead = dead_refs(text, f.parent, P, skill_dirs)
        if dead:
            add('instructions', rel(f, P), 'Points at %d path(s) that do not exist: %s.' % (
                len(dead), ', '.join(sorted(dead)[:6])),
                'Fix or remove each reference.', risk='med', kind='dead-ref')
    root = P / 'CLAUDE.md'
    if root.exists():
        text = read_text(root)
        for d in sorted(P.iterdir()):
            if d.is_dir() and not d.name.startswith('.') and d.name not in SKIP_DIRS:
                if not re.search(r'(?<![\w-])' + re.escape(d.name) + r'(?![\w-])', text):
                    add('instructions', 'CLAUDE.md', 'Top-level folder "%s/" is not mentioned.' % d.name,
                        'Say what it is for in one line, or archive the folder if nothing uses it.',
                        kind='unmapped-folder')
    for para, owners in paras.items():
        if len(owners) > 1:
            add('instructions', 'repeated text', 'The same paragraph loads from %d files: %s. "%s..."' % (
                len(owners), ', '.join(rel(o, P) for o in owners), para[:90]),
                'Keep it in one place.', kind='duplicate')
    return always_chars


def check_memory(P):
    d = CLAUDE / 'projects' / project_slug(P) / 'memory'
    idx = d / 'MEMORY.md'
    if not idx.exists():
        return 0
    text = read_text(idx)
    lines, size = text.count('\n') + 1, len(text.encode())
    if lines > 180 or size > 22_000:
        add('memory', 'MEMORY.md', '%d lines / %d KB. Only the first 200 lines or 25 KB load.' % (lines, size // 1024),
            'Merge or drop stale entries so nothing important falls past the cut.', risk='med', kind='near-limit')
    linked = set()
    for target in re.findall(r'\]\(([^)\s]+\.md)\)', text):
        tp = (d / target).resolve()
        linked.add(tp)
        if not tp.exists():
            add('memory', target, 'The index links to an entry that does not exist.', 'Remove the index line.',
                kind='dead-link')
    real = d.resolve()
    old = 0
    entries = [f for f in real.glob('*.md')] + [f for f in real.glob('entries/*.md')]
    for f in entries:
        if f.name == 'MEMORY.md':
            continue
        if f.resolve() not in linked:
            add('memory', rel(f, real), 'Entry exists but the index does not link to it, so it is never recalled.',
                'Link it from the index or archive it.', kind='orphan')
        body = read_text(f, 50_000)
        m = re.search(r'(?m)^created:\s*(\d{4}-\d{2}-\d{2})', body)
        ts = time.mktime(time.strptime(m.group(1), '%Y-%m-%d')) if m else f.stat().st_mtime
        if NOW - ts > 90 * DAY:
            old += 1
        dead = dead_refs(body, f.parent, P)
        if dead:
            add('memory', rel(f, real), 'Names path(s) that no longer exist: %s.' % ', '.join(sorted(dead)[:4]),
                'Update or remove the stale claim.', kind='dead-ref')
    if old:
        add('memory', '%d entries over 90 days old' % old, 'Older memories describe a past moment.',
            'Re-check them against the current setup before relying on them.', kind='stale')
    return toks(min(size, 25_000))


INDEX_NAMES = {'readme.md', 'index.md', '_index.md', 'claude.md', 'agents.md'}
RETIRED_BITS = {'_retired', 'retired', '_archive', 'archive'}
FACT_TOPICS = [
    ('price', re.compile(r'([$£€]\s?\d|\bpric(e|ing)\b|per month|/mo\b|\bfee\b)', re.I)),
    ('offer', re.compile(r'\b(offer|tier|package|membership|guarantee|community)\b', re.I)),
    ('audience', re.compile(r'\b(icp|audience|buyer|customer|persona|niche)\b', re.I)),
    ('brand', re.compile(r'\b(brand|colou?r|font|palette|logo|theme)\b', re.I)),
    ('models and tools', re.compile(r'\b(claude-|opus|sonnet|haiku|fable|gpt-|gemini|connector|mcp)\b', re.I)),
]
FACT_CUE = re.compile(r'(\bdefault\b|\bcurrent(ly)?\b|\bnow\b|\bretired?\b|\breplaced?\b|\bmoved to\b|'
                      r'\bno longer\b|\binstead of\b|\balways\b|\bnever\b|\bis the\b|[$£€]\s?\d|\d+%)', re.I)


def folder_verdict(f):
    if f['retired']:
        return 'retired'
    if f['raw']:
        return 'raw'
    if f['reads'] >= 3 or (f['age_days'] is not None and f['age_days'] <= 14):
        return 'live'
    if f['reads'] == 0 and f['inbound'] == 0 and not f['routed'] and (f['age_days'] or 0) > 60:
        return 'cold'
    return 'reference'


def audit_context_layer(P, dirs, use, days):
    """Every file in the context layer, with the signals that decide what to do with it.

    Coverage is total: each file gets a row in context_inventory.json. Findings come from signals
    (read by Claude, linked, routed, changed) and are raised per folder first, so a layer of
    hundreds of files stays reviewable. Fact lines go to facts.jsonl for a targeted contradiction check.
    """
    if not dirs:
        dirs = [P / n for n in ('context', 'wiki', 'knowledge', 'notes', 'vault', 'second-brain')
                if (P / n).is_dir()]
    if not dirs:
        NOT_CHECKED.append('Context layer: no context/ or wiki/ folder found (pass --context-dir)')
        return {'coverage': None, 'files': [], 'folders': [], 'facts': []}
    files = []
    for d in dirs:
        for f in d.rglob('*'):
            if f.is_file() and f.name != '.DS_Store' and not (set(f.relative_to(d).parts[:-1]) & SKIP_DIRS):
                files.append((d, f))
    # Inbound links can come from anywhere (skills, CLAUDE.md, other notes). One pass pulls the
    # path-like tokens out of every text file; each file then counts once per referrer.
    # The lookbehind starts a match only at the edge of a path-like run, which keeps this linear.
    token_rx = re.compile(r'(?<![\w./~-])[\w./~-]+\.(?:md|json|ya?ml|py)(?!\w)|\[\[[^\]|#\n]{1,120}')
    refs_by = collections.defaultdict(set)
    for dp, dns, fns in os.walk(P):
        dns[:] = [x for x in dns if x not in SKIP_DIRS and not x.startswith('.git')]
        for fn in fns:
            fp = Path(dp) / fn
            if fp.suffix not in TEXT_EXT:
                continue
            try:
                if fp.stat().st_size >= 1_500_000:
                    continue
            except OSError:
                continue
            for tok in set(token_rx.findall(read_text(fp))):
                if tok.startswith('[['):
                    refs_by['[[' + tok[2:].strip()].add(fp)
                else:
                    t = tok.lstrip('./~')
                    refs_by[t].add(fp)
                    refs_by[t.rsplit('/', 1)[-1]].add(fp)
    man = next((d / 'manifest.json' for d in dirs if (d / 'manifest.json').exists()), None)
    mtext = read_text(man) if man else ''
    # Old-name aliases ("legacy", "alias", "redirect" sections) point from a path that is gone on purpose.
    aliases = set()

    def walk(node, under_alias=False):
        if isinstance(node, dict):
            for k, v in node.items():
                alias = under_alias or bool(re.search(r'legacy|alias|redirect|deprecat|retired|old_', k, re.I))
                if alias and isinstance(k, str) and '/' in k:
                    aliases.add(k)
                walk(v, alias)
        elif isinstance(node, list):
            for v in node:
                walk(v, under_alias)
    walk(read_json(man) if man else None)  # alias keys are the old paths; their values still get checked
    routes = set(re.findall(r'"([^"\s]+\.(?:md|json|ya?ml|py))"', mtext)) - aliases
    route_dirs = {r for r in re.findall(r'"([^"\s]+/)"', mtext)}
    names = collections.Counter(f.name for _d, f in files)
    rows, hashes, texts = [], collections.defaultdict(list), {}
    for root, f in files:
        r = rel(f, P)
        st = f.stat()
        rd = use['read'].get(str(f)) or {}
        parts = set(f.relative_to(root).parts[:-1])
        text = read_text(f, 400_000) if f.suffix in TEXT_EXT else ''
        needles = [r, '[[' + f.stem] + ([f.name] if names[f.name] == 1 and f.name.lower() not in INDEX_NAMES else [])
        referrers = set()
        for n in needles:
            referrers |= refs_by.get(n, set())
        referrers.discard(f)
        inbound = len(referrers)
        routed = bool(man) and (r in routes or rel(f, man.parent) in routes or
                                any(r.startswith(x.rstrip('/') + '/') for x in route_dirs))
        row = {'path': r, 'ext': f.suffix.lower(), 'bytes': st.st_size, 'modified': fmt_when(st.st_mtime),
               'age_days': age_days(st.st_mtime), 'reads': rd.get('n', 0), 'last_read': fmt_when(rd.get('last')),
               'inbound': inbound, 'routed': routed, 'raw': bool(parts & RAW_DIRS - RETIRED_BITS),
               'retired': bool(parts & RETIRED_BITS), 'folder': str(Path(r).parent)}
        rows.append(row)
        if row['ext'] == '.md':
            texts[r] = text

    note = lambda x: x['ext'] == '.md' and not x['retired']
    for x in rows:
        if not note(x):
            continue
        text = texts[x['path']]
        if len(text) > 200:
            hashes[hashlib.sha1(re.sub(r'\s+', ' ', text).strip().encode()).hexdigest()].append(x['path'])
        if x['raw']:
            continue
        dead = dead_refs(text, (P / x['path']).parent, P)
        if dead:
            add('context', x['path'], 'Broken link(s): %s.' % ', '.join(sorted(dead)[:5]),
                'Fix or remove each link.', risk='med', kind='dead-ref')
        heads = collections.Counter(h.strip().lower() for h in re.findall(r'(?m)^#{1,3} .+$', text))
        rep = [h for h, n in heads.items() if n > 1 and len(h) > 6]
        if len(rep) >= 2:
            add('context', x['path'], 'Headings repeat inside the file (%s): usually versions pasted on top of '
                'each other, which Claude reads as conflicting facts.' % ', '.join(rep[:3]),
                'Keep the current version and drop the rest.', risk='med', kind='stacked-versions')
        if Path(x['path']).name.lower() in INDEX_NAMES:
            continue
        if x['reads'] >= 5 and x['bytes'] > 20_000:
            add('context', x['path'], 'Opened %d times in %d days; the file is %d KB (about %s tokens), so each '
                'open costs a large read or several partial ones.' % (
                    x['reads'], days, x['bytes'] // 1024, '{:,}'.format(toks(x['bytes']))),
                'Put a short summary first, or split it so the common case reads a small file.',
                risk='med' if x['reads'] * x['bytes'] > 2_000_000 else 'low', kind='hot-heavy')
        if x['inbound'] == 0 and not x['routed'] and x['reads']:
            add('context', x['path'], 'Claude found it %d time(s) by searching, but nothing links or routes to it.'
                % x['reads'], 'Link it from its folder index or the manifest.', kind='found-by-search')
    unrouted = sorted((x for x in rows if note(x) and not x['raw'] and man and x['reads'] >= 3 and not x['routed']
                       and (P / x['path']).is_relative_to(man.parent)
                       and Path(x['path']).name.lower() not in INDEX_NAMES), key=lambda r: -r['reads'])
    if unrouted:
        add('context', '%d notes read often but not routed' % len(unrouted),
            'Claude keeps finding these by searching; %s has no route to them: %s.' % (
                rel(man, P), ', '.join('%s (%d reads)' % (x['path'], x['reads']) for x in unrouted[:12])),
            'Route the ones skills depend on, so they are found without a search.', kind='read-unrouted')
    for dup in hashes.values():
        if len(dup) > 1:
            add('context', ' = '.join(dup), 'Identical files.', 'Keep one and link the rest to it.', kind='duplicate')
    if man:
        for r in sorted(routes):
            if not any(p.exists() for p in (man.parent / r, P / r)):
                add('context', rel(man, P), 'Routes to a file that does not exist: %s.' % r,
                    'Fix the route.', risk='med', kind='dead-route')
        never = [x for x in rows if note(x) and x['routed'] and x['reads'] == 0 and (P / x['path']).name in mtext]
        if never and days >= 30:
            add('context', '%d routed notes never read' % len(never),
                'The manifest routes to them but Claude never opened one in %d days (scripts that read files '
                'directly do not show up here): %s.' % (days, ', '.join(x['path'] for x in never[:10])),
                'Check the skills that should read them still do; drop routes for retired facts.', kind='routed-unread')

    folders = collections.OrderedDict()
    for x in sorted(rows, key=lambda r: r['folder']):
        f = folders.setdefault(x['folder'], {'folder': x['folder'], 'files': 0, 'notes': 0, 'bytes': 0, 'reads': 0,
                                             'inbound': 0, 'routed': False, 'age_days': None, 'raw': x['raw'],
                                             'retired': x['retired'], 'cold_notes': [], 'has_index': False})
        f['files'] += 1
        f['bytes'] += x['bytes']
        f['reads'] += x['reads']
        f['inbound'] += x['inbound']
        f['routed'] = f['routed'] or x['routed']
        f['age_days'] = x['age_days'] if f['age_days'] is None else min(f['age_days'], x['age_days'])
        if x['ext'] == '.md':
            f['notes'] += 1
            f['has_index'] = f['has_index'] or Path(x['path']).name.lower() in INDEX_NAMES
            if x['reads'] == 0 and x['inbound'] == 0 and not x['routed'] and Path(x['path']).name.lower() not in INDEX_NAMES:
                f['cold_notes'].append(x['path'])
    for f in folders.values():
        f['verdict'] = folder_verdict(f)
        if f['verdict'] == 'cold':
            add('context', f['folder'] + '/', '%d file(s), none read in %d days, nothing links or routes here, last '
                'changed %d days ago.' % (f['files'], days, f['age_days'] or 0),
                'Archive the folder, or link it from an index if it still holds live facts.', kind='cold-folder',
                undo='Move it back from the archive.')
        elif f['verdict'] in ('live', 'reference') and f['cold_notes']:
            add('context', f['folder'] + '/', '%d note(s) here are never read or linked: %s.' % (
                len(f['cold_notes']), ', '.join(Path(c).name for c in f['cold_notes'][:8])),
                'Merge what is still true into a live note, link it, or archive it.', kind='orphans')
        if f['notes'] >= 5 and not f['has_index'] and f['verdict'] not in ('raw', 'retired'):
            add('context', f['folder'] + '/', '%d notes and no README or index.' % f['notes'],
                'Add a short index saying what each file is for.', kind='no-index')
    retired = [x for x in rows if x['retired']]
    if retired:
        add('context', '%d retired files inside the context layer' % len(retired),
            '%d MB in _retired or archive folders under %s. Claude can still find them by searching.' % (
                sum(x['bytes'] for x in retired) // 1048576, ', '.join(rel(d, P) for d in dirs)),
            'Move them to the workspace archive so search only finds live facts.', kind='retired-inside')
    media = [x for x in rows if x['ext'] in ('.png', '.jpg', '.jpeg', '.gif', '.mp4', '.mov', '.webm', '.pdf', '.zip', '.mp3', '.wav')]
    mb = sum(x['bytes'] for x in media) // 1048576
    if mb >= 10:
        add('context', '%d media files (%d MB)' % (len(media), mb),
            'Images, video and archives in the context layer. Claude reads text here; media mostly belongs with the work it supports.',
            'Keep brand assets renderers need; move the rest out.', kind='media')

    facts = []
    hot = sorted((x for x in rows if note(x) and not x['raw'] and (x['reads'] or x['routed'])),
                 key=lambda r: -r['reads'])
    sources = [x['path'] for x in hot] + [rel(f, P) for f in (P / 'CLAUDE.md',) if f.exists()]
    per_topic = collections.Counter()
    for path in sources:
        text = texts.get(path) or read_text(P / path)
        for i, ln in enumerate(text.splitlines(), 1):
            s = ln.strip().lstrip('-*>| ').strip()
            if not (20 <= len(s) <= 260) or not FACT_CUE.search(s):
                continue
            for topic, rx in FACT_TOPICS:
                if rx.search(s) and per_topic[topic] < 40:
                    per_topic[topic] += 1
                    facts.append({'topic': topic, 'file': path, 'line': i, 'text': s})
                    break
    if facts:
        add('context', '%d fact lines from %d files Claude reads' % (len(facts), len({f['file'] for f in facts})),
            'Grouped by topic in facts.jsonl: %s.' % ', '.join('%s %d' % kv for kv in per_topic.most_common()),
            'Compare the lines within each topic and flag any two files that disagree, quoting both.',
            kind='contradiction-check')
    coverage = {'dirs': [rel(d, P) for d in dirs], 'files': len(rows), 'notes': sum(1 for x in rows if x['ext'] == '.md'),
                'folders': len(folders), 'read_in_window': sum(1 for x in rows if x['reads'])}
    return {'coverage': coverage, 'files': rows, 'folders': list(folders.values()), 'facts': facts}


def workspace_map(P, use, quick):
    """Folder-level map of the workspace: size, last change, how often Claude read inside it."""
    if quick:
        NOT_CHECKED.append('Workspace map and large files (--quick)')
        return [], []
    reads = collections.Counter()
    pre = str(P) + os.sep
    for path, rd in use['read'].items():
        if path.startswith(pre):
            parts = Path(path[len(pre):]).parts
            if len(parts) > 1:
                reads[parts[0]] += rd['n']
                if len(parts) > 2:
                    reads[parts[0] + '/' + parts[1]] += rd['n']
    stats = collections.defaultdict(lambda: {'files': 0, 'bytes': 0, 'newest': 0})
    big = []
    for dp, dns, fns in os.walk(P):
        dns[:] = [x for x in dns if x not in ('.git', 'node_modules', '.venv', 'venv', '__pycache__')]
        relp = Path(dp).relative_to(P).parts
        if not relp:
            continue
        keys = [relp[0]] + (['%s/%s' % relp[:2]] if len(relp) > 1 else [])
        for fn in fns:
            fp = Path(dp) / fn
            try:
                st = fp.lstat()
            except OSError:
                continue
            for k in keys:
                s = stats[k]
                s['files'] += 1
                s['bytes'] += st.st_size
                s['newest'] = max(s['newest'], st.st_mtime)
            if st.st_size > 200 * 1024 * 1024 and not fp.is_symlink():
                big.append((st.st_size, fp))
    root_md = read_text(P / 'CLAUDE.md')
    rows = []
    for k, s in sorted(stats.items()):
        top = '/' not in k
        rows.append({'folder': k, 'level': 1 if top else 2, 'files': s['files'], 'mb': round(s['bytes'] / 1048576, 1),
                     'changed_days_ago': age_days(s['newest']), 'reads': reads.get(k, 0),
                     'in_claude_md': bool(re.search(r'(?<![\w-])' + re.escape(k.split('/')[-1]) + r'(?![\w-])', root_md)) if top else None})
    cold_heavy = [r for r in rows if r['level'] == 2 and r['reads'] == 0 and (r['changed_days_ago'] or 0) > 60
                  and r['mb'] >= 50 and not (set(r['folder'].split('/')) & RETIRED_BITS)]
    for r in sorted(cold_heavy, key=lambda r: -r['mb'])[:15]:
        add('disk', r['folder'] + '/', '%s MB in %d files, untouched for %d days and never read by Claude in the window.' % (
            r['mb'], r['files'], r['changed_days_ago']),
            'Archive it or move it to cold storage if nothing needs it.', kind='cold-heavy',
            undo='Move it back from the archive.')
    big.sort(reverse=True)
    return rows, big


# ---------- interface, disk, models ----------

def check_cowork(use, skills, days):
    """The Cowork tab loads its own skills and plugins and switches connectors on separately."""
    bases = [app / 'local-agent-mode-sessions' for app in APPS if (app / 'local-agent-mode-sessions').is_dir()]
    if not bases:
        return
    base = max(bases, key=lambda b: b.stat().st_mtime)  # two Windows installs: the one in use
    names, latest = {}, {}
    for sub in ('claude-code-sessions', 'local-agent-mode-sessions'):
        for f in app_sessions(sub):
            d = read_json(f) or {}
            for s in d.get('remoteMcpServersConfig') or []:
                if s.get('uuid') and s.get('name'):
                    names[s['uuid']] = s['name']
            try:
                t = float(d.get('lastActivityAt') or 0)
            except (TypeError, ValueError):
                t = 0
            if d.get('remoteMcpServersConfig') and t > latest.get(sub, (0, None))[0]:
                latest[sub] = (t, d)
    cw_calls = collections.Counter()
    for key, v in use['mcp'].items():
        if v.get('cowork'):
            cw_calls[names.get(key, key)] += v['cowork']

    def cw_runs(name):
        return sum(v.get('cowork', 0) for k, v in use['skill'].items() if k == name or k.endswith(':' + name))

    cw_skills = sorted({p.parent.name for p in base.glob('skills-plugin/*/*/skills/*/SKILL.md')})
    plugins = {}
    for pj in base.glob('*/*/rpm/plugin_*/.claude-plugin/plugin.json'):
        root = pj.parent.parent
        plugins[(read_json(pj) or {}).get('name') or root.name] = [p.parent.name for p in root.glob('skills/*/SKILL.md')]
    # Cowork projects ("spaces") live only on this computer: folders, instructions, links, memory.
    for sp in base.glob('*/*/spaces.json'):
        sessions = [read_json(f) or {} for f in sp.parent.glob('local_*.json')]
        for s in (read_json(sp) or {}).get('spaces') or []:
            runs = [x for x in sessions if x.get('spaceId') == s.get('id')]
            try:
                last = max([float(x.get('lastActivityAt') or 0) / 1000 for x in runs] or
                           [float(s.get('updatedAt') or 0) / 1000])
            except (TypeError, ValueError):
                last = 0
            gone = [f.get('path') for f in s.get('folders') or [] if f.get('path') and not os.path.isdir(f['path'])]
            label = '%s (Cowork project)' % s.get('name', '?')
            if gone:
                add('cowork', label, 'Points at folder(s) that no longer exist: %s.' % ', '.join(tilde(g) for g in gone),
                    'Re-point it, or archive it in the sidebar. Archiving deletes its instructions, links and memory; '
                    'your files are untouched.', risk='med', kind='project-missing-folder', reversible=False)
            elif NOW - last > 60 * DAY:
                add('cowork', label, 'No session in %d days (%d on record).' % (age_days(last), len(runs)),
                    'Archive it if the work is done. Archiving deletes its instructions, links and memory; your '
                    'files are untouched.', kind='project-idle', reversible=False)
    last_used = max((f.stat().st_mtime for f in base.rglob('audit.jsonl')), default=0)
    cw_on = latest.get('local-agent-mode-sessions', (0, None))[1]
    if NOW - last_used > days * DAY:
        add('cowork', 'Cowork unused for %s' % ('ever' if not last_used else '%d days' % age_days(last_used)),
            'Last Cowork activity: %s. It still loads %d skills and %d plugins, with %d connectors switched on.' % (
                fmt_when(last_used), len(cw_skills), len(plugins),
                len((cw_on or {}).get('remoteMcpServersConfig') or [])),
            'If you have moved to the Code tab, switch Cowork\'s connectors off and leave it; nothing there '
            'costs you in Code-tab sessions.', kind='idle-tab')
        cw_skills, plugins = [], {}
    idle = [s for s in cw_skills if not cw_runs(s)]
    if idle:
        add('cowork', '%d of %d Cowork skills' % (len(idle), len(cw_skills)),
            'No recorded run in Cowork in the last %d days: %s.' % (days, ', '.join(idle)),
            'Cowork skills come from your claude.ai account: hide or remove the ones you never use there.',
            kind='unused')
    for pname, sk in sorted(plugins.items()):
        if sk and not sum(cw_runs(s) for s in sk):
            add('cowork', pname, 'Loads in Cowork with %d skill(s); none ran there in %d days.' % (len(sk), days),
                'Turn it off for Cowork if you only use it in the Code tab.', kind='unused-plugin')
    cw = cw_on
    code = latest.get('claude-code-sessions', (0, None))[1]
    on = lambda d: sorted({s.get('name') for s in (d or {}).get('remoteMcpServersConfig') or [] if s.get('name')})
    if cw and NOW - last_used <= days * DAY:
        quiet = [n for n in on(cw) if not cw_calls.get(n)]
        if quiet:
            add('cowork', '%d of %d connectors on in Cowork' % (len(quiet), len(on(cw))),
                'Switched on in your latest Cowork session with no Cowork calls in %d days: %s.' % (days, ', '.join(quiet)),
                'Switch them off in Cowork; they stay available in the Code tab.', kind='unused-connectors')
    project = sum(1 for s in skills if s['origin'] == 'project')
    only_code = sorted(set(on(code)) - set(on(cw))) if code and cw else []
    only_cw = sorted(set(on(cw)) - set(on(code))) if code and cw else []
    n_skills = len({p.parent.name for p in base.glob('skills-plugin/*/*/skills/*/SKILL.md')})
    n_plugins = len(list(base.glob('*/*/rpm/plugin_*/.claude-plugin/plugin.json')))
    add('cowork', 'how the two tabs differ',
        'Cowork loads %d skills and %d plugins from your account; the %d skills in this project load only in the '
        'Code tab. Connectors are one account pool switched on per tab%s%s.' % (
            n_skills, n_plugins, project,
            ('; on in the Code tab only: ' + ', '.join(only_code)) if only_code else '',
            ('; on in Cowork only: ' + ', '.join(only_cw)) if only_cw else ''),
        'Nothing to do; decide per tab what each one needs.', kind='info')


def check_interface(settings, use, P):
    temp = ('/tmp', '/private/tmp', '/private/var', '/var/folders', tempfile.gettempdir())
    others = sorted(((len(s), c) for c, s in use['cwd'].items()
                     if len(s) >= 2 and Path(c) != P and P not in Path(c).parents and not c.startswith(temp)
                     and Path(c).exists()), reverse=True)
    if others:
        add('interface', 'other active folders', 'You also worked in: %s.' % '; '.join(
            '%s (%d sessions)' % (tilde(c), n) for n, c in others[:8]),
            'Run the tidy in each one too; their CLAUDE.md and project skills are only checked from inside.',
            kind='other-folders')
    # Desktop chats (Code tab and Cowork): every open one is classified here, so the review can't skip them.
    # interface.json in the run folder keeps the session ids the desktop tools need to archive or move them.
    INTERFACE.clear()
    if not APPS:
        NOT_CHECKED.append('Desktop app chats, Cowork and desktop task runs: ' + {
            None: "the Claude app's folder isn't where it usually is. If you use the desktop app, Claude can "
                  "search your user folder for it",
            'none': "searched your user folder and found no Claude app folder (fine if you only use Claude "
                    "Code in a terminal or editor)",
            'timed-out': "the search of your user folder stopped after 90 seconds without finding the Claude "
                         "app folder"}[APP_SEARCH])
    elif APP_SEARCH == 'found':
        add('interface', "Claude app folder", "Not in the usual place, so Zen searched for it and read: %s." % (
            '; '.join(tilde(a) for a in APPS)), 'Nothing to do; if that is an old copy, say so and ignore '
            'the chats it lists.', kind='info')
    for kind, sub in (('Code tab', 'claude-code-sessions'), ('Cowork', 'local-agent-mode-sessions')):
        for f in app_sessions(sub):
            d = read_json(f) or {}
            try:
                last = float(d.get('lastActivityAt') or d.get('createdAt') or 0) / 1000
            except (TypeError, ValueError):
                last = 0
            cwd = tilde(d.get('cwd') or d.get('originCwd') or '')
            turns = d.get('completedTurns')
            s = {'id': d.get('sessionId'), 'surface': kind, 'title': d.get('title') or '(untitled)',
                 'last': fmt_when(last), 'idle_days': age_days(last), 'folder': cwd if cwd.startswith('~') else '',
                 'turns': turns, 'archived': bool(d.get('isArchived')), 'scheduled': bool(d.get('scheduledTaskId')),
                 'cowork_project': bool(d.get('spaceId'))}
            open_ = not s['archived'] and not s['scheduled']
            quiet = (s['idle_days'] or 0) >= 3  # never pick a chat that is still in use
            s['one_off'] = open_ and quiet and (turns or 0) <= 2
            # Only a folder Zen can read counts: an unreadable one is not proof the chat started outside a project.
            s['stray_folder'] = open_ and quiet and bool(re.search(r'/scratch-|^~$|/sandbox', s['folder']))
            s['idle'] = open_ and (s['idle_days'] or 0) >= 30
            INTERFACE.append(s)
    for kind in ('Code tab', 'Cowork'):
        mine = [s for s in INTERFACE if s['surface'] == kind and not s['archived'] and not s['scheduled']]
        if not mine:
            continue
        picks = sorted({s['id']: s for s in mine if s['one_off'] or s['stray_folder'] or s['idle']}.values(),
                       key=lambda s: -(s['idle_days'] or 0))
        if picks:
            add('interface', '%d of %d open %s chats to archive' % (len(picks), len(mine), kind),
                'One-off (two turns or fewer), started outside a project, or idle 30+ days: %s.' % '; '.join(
                    '"%s" (%s)' % (s['title'][:48], s['last']) for s in picks[:30]),
                'Archive them (desktop app: ccd_session_mgmt archive_session with the ids in interface.json; '
                'otherwise the sidebar). Archived chats can be brought back.',
                kind='archive-chats', undo='Unarchive in the app.')
        keep = [s for s in mine if s not in picks]
        by_folder = collections.Counter(('scratch' if '/scratch-' in s['folder'] else Path(s['folder']).name or '~')
                                        if s['folder'] else 'no folder' for s in keep)
        if len(keep) >= 6:
            add('interface', '%d open %s chats to group' % (len(keep), kind),
                'By folder: %s. Titles are in interface.json.' % ', '.join('%s %d' % kv for kv in by_folder.most_common(6)),
                'Propose a few sidebar sections by topic from the titles (desktop app: ccd_sidebar create_section, '
                'then move_sessions).', kind='group-chats', undo='Move them back.')
    switches = read_json(CLAUDE / 'mods' / 'switches.json') or {}
    mods = ['%s (%s)' % (p.name, 'on' if switches.get(p.name, True) else 'off')
            for p in (CLAUDE / 'mods').glob('*') if p.is_dir()]
    mods += ['%s (dev)' % p.name for p in (CLAUDE / 'dev-mods').glob('*/*') if p.is_dir()]
    if mods:
        add('interface', '%d mod(s)' % len(mods), 'Installed: %s. Mods keep no usage log.' % ', '.join(mods),
            'Keep the ones you look at; switch off or remove the rest.', kind='mods')
    keep = 30
    for _s, _p, d in settings:
        if d.get('cleanupPeriodDays') is not None:
            keep = d['cleanupPeriodDays']
    proj = CLAUDE / 'projects'
    if proj.is_dir():
        kb = dir_size_kb(proj)
        if kb > 2 * 1024 * 1024:
            add('disk', 'session history', '%s GB in ~/.claude/projects; cleanupPeriodDays is %s.' % (gb(kb), keep),
                'Lower cleanupPeriodDays if you do not need that much history. Usage reports, /insights and '
                'reviews read it, and Claude Code deletes older sessions at the next start, so this one is not '
                'reversible.', kind='history', reversible=False)
    NOT_CHECKED.append('Artifacts, pinned items and claude.ai chats/projects/memory: ask Claude to list artifacts; '
                       'claude.ai chats and memory are only visible in the web app')


def check_disk(P, big):
    for name in ('.tmp', 'tmp', 'scratch', 'temp'):
        d = P / name
        if not d.is_dir():
            continue
        entries = list(d.iterdir())
        old = [e for e in entries if NOW - e.stat().st_mtime > 30 * DAY]
        kb = dir_size_kb(d)
        if old or kb > 1024 * 1024:
            add('disk', name + '/', '%d entries (%d untouched 30+ days), %s GB.' % (len(entries), len(old), gb(kb)),
                'Archive or delete the old entries.', kind='scratch', undo='Move them back from the archive.')
    logs = P / 'logs'
    if logs.is_dir():
        for f in logs.glob('*'):
            if f.is_file() and f.stat().st_size > 50 * 1024 * 1024:
                add('disk', rel(f, P), '%d MB log.' % (f.stat().st_size // 1024 // 1024),
                    'Rotate or trim it.', kind='log')
    if big:
        add('disk', '%d files over 200 MB' % len(big),
            '; '.join('%s (%d MB)' % (rel(fp, P), s // 1024 // 1024) for s, fp in big[:10]),
            'Move media and exports out of the working folder if Claude never needs to read them.', kind='big-files')


def model_catalog():
    """Current models (the picker's main section) and every model the catalog still lists."""
    best, main, every = 0, set(), set()
    for f in (CLAUDE / 'cache' / 'model-catalog').glob('*-cc.json'):
        d = read_json(f) or {}
        if d.get('fetchedAt', 0) >= best:
            models = ((d.get('catalog') or {}).get('config') or {}).get('models') or []
            if models:
                best = d.get('fetchedAt', 0)
                every = {m['id'] for m in models if m.get('id')}
                main = {m['id'] for m in models if m.get('id') and m.get('section') == 'main'} or every
    return main, every


def model_status(m, catalog):
    main, every = catalog
    if m in main or any(c.startswith(m + '-') for c in main):
        return None
    return 'an older model' if (m in every or any(c.startswith(m + '-') for c in every)) else 'no longer listed'


def check_models(P, settings, skills, agents, catalog):
    if not catalog[0]:
        NOT_CHECKED.append('Outdated model IDs: no local model catalog found')
        return
    seen = collections.defaultdict(set)
    for scope, p, d in settings:
        for m in MODEL_ID.findall(json.dumps({'model': d.get('model'), 'ms': d.get('modelSettings'),
                                              'env': d.get('env')})):
            seen[m].add('%s settings' % scope)
    for s in skills:
        if s['origin'] in ('project', 'user'):
            for m in MODEL_ID.findall(s['model']):
                seen[m].add('skill ' + s['name'])
    for a in agents:
        if a['origin'] in ('project', 'user'):
            for m in MODEL_ID.findall(a['model']):
                seen[m].add('agent ' + a['name'])
    for m, where_ in sorted(seen.items()):
        st = model_status(m, catalog)
        if st:
            add('models', m, 'This is %s. Used in: %s.' % (st, ', '.join(sorted(where_))),
                'Point it at a current model (or the plain alias), unless you pinned it on purpose.',
                kind='old-model')


# ---------- output ----------

AREAS = ['connectors', 'skills', 'agents', 'plugins', 'scheduled', 'hooks', 'permissions',
         'instructions', 'memory', 'context', 'cowork', 'interface', 'disk', 'models']
TITLES = {'connectors': 'Connectors', 'skills': 'Skills', 'agents': 'Agents', 'plugins': 'Plugins',
          'scheduled': 'Scheduled work', 'hooks': 'Hooks', 'permissions': 'Permissions',
          'instructions': 'Instruction files', 'memory': 'Memory', 'context': 'Context layer',
          'cowork': 'Cowork tab', 'interface': 'Sessions and interface', 'disk': 'Disk', 'models': 'Models'}
RISK = {'high': 0, 'med': 1, 'low': 2}


def write_outputs(out, summary, corrections, firing, ctx, wmap):
    FINDINGS.sort(key=lambda f: (AREAS.index(f['area']) if f['area'] in AREAS else 99,
                                 RISK.get(f['risk'], 3), f['kind'], f['item']))
    for i, f in enumerate(FINDINGS, 1):
        f['id'] = 'T-%03d' % i
    out.mkdir(parents=True, exist_ok=True)
    (out / 'findings.json').write_text(json.dumps(FINDINGS, indent=1, default=str), encoding='utf-8')
    (out / 'summary.json').write_text(json.dumps(summary, indent=1, default=str), encoding='utf-8')
    (out / 'context_inventory.json').write_text(json.dumps(
        {'coverage': ctx['coverage'], 'folders': ctx['folders'], 'files': ctx['files']}, indent=1, default=str), encoding='utf-8')
    (out / 'workspace_map.json').write_text(json.dumps(wmap, indent=1), encoding='utf-8')
    (out / 'interface.json').write_text(json.dumps(INTERFACE, indent=1), encoding='utf-8')
    with open(out / 'facts.jsonl', 'w', encoding='utf-8') as fh:
        for f in ctx['facts']:
            fh.write(json.dumps(f) + '\n')
    with open(out / 'corrections.jsonl', 'w', encoding='utf-8') as fh:
        for c in corrections:
            fh.write(json.dumps(dict(c, type='correction')) + '\n')
        for name, samples in firing.items():
            for s in samples:
                fh.write(json.dumps({'type': 'fired_on', 'skill': name, **s}) + '\n')

    def line(f):
        flag = {'high': ' ⚠️', 'med': ' •'}.get(f['risk'], '')
        return '- [ ] **%s**%s `%s`: %s Suggested: %s%s' % (
            f['id'], flag, f['item'], f['evidence'], f['action'],
            '' if f['reversible'] else ' *(not reversible)*')

    def table(items):
        rows = ['| ID | Item | Evidence | Decision |', '|---|---|---|---|']
        for f in items:
            rows.append('| %s | `%s` | %s | |' % (f['id'], f['item'], f['evidence'].replace('|', '/')[:220]))
        return rows + ['', '*Suggested for all of these:* %s' % items[0]['action'], '']

    L = ['# Setup tidy: %s' % summary['date'], '',
         'Project: `%s` · history window: %s days (records from %s) · %d findings' % (
             summary['project'], summary['days'], summary['history_from'], len(FINDINGS)), '',
         '**Baseline per session (estimate, characters / 4):** about %s tokens before you type: '
         'skill listings %s, agent list %s, always-loaded instruction files %s, memory index %s. '
         'Connectors add their instructions and tool names on top: %s connected here.' % (
             '{:,}'.format(summary['baseline']['total']), '{:,}'.format(summary['baseline']['skills']),
             '{:,}'.format(summary['baseline']['agents']), '{:,}'.format(summary['baseline']['instructions']),
             '{:,}'.format(summary['baseline']['memory']), summary['counts'].get('connectors_connected', '?')), '',
         'Mark each item: **keep**, **do it**, **change** (say how) or **ask**. Nothing changes until you decide.', '']
    for area in AREAS:
        items = [f for f in FINDINGS if f['area'] == area]
        if not items:
            continue
        L += ['## %s (%d)' % (TITLES[area], len(items)), '']
        if area == 'context' and ctx['coverage']:
            c = ctx['coverage']
            L += ['Covered **%d of %d files** in %s (%d notes, %d folders); Claude read %d of them in the window. '
                  'Every file has a row in `context_inventory.json`.' % (
                      c['files'], c['files'], ', '.join(c['dirs']), c['notes'], c['folders'], c['read_in_window']), '',
                  '| Folder | Verdict | Files | Reads | Last change | Linked / routed |', '|---|---|---|---|---|---|']
            for f in ctx['folders']:
                if f['folder'].count('/') <= 2 and f['verdict'] not in ('retired',):
                    L.append('| `%s` | %s | %d | %d | %s days | %s |' % (
                        f['folder'], f['verdict'], f['files'], f['reads'], f['age_days'],
                        'routed' if f['routed'] else ('linked' if f['inbound'] else 'no')))
            L.append('')
        groups = collections.OrderedDict()
        for f in items:
            groups.setdefault(f['kind'], []).append(f)
        for kind, group in groups.items():
            if len(group) > 6:
                L += ['**%s** (%d)' % (kind.replace('-', ' '), len(group)), ''] + table(group)
            else:
                L += [line(f) for f in group]
        L.append('')
    tops = [r for r in wmap if r['level'] == 1]
    if tops:
        L += ['## Workspace map', '', 'Top-level folders. Second-level detail is in `workspace_map.json`.', '',
              '| Folder | Files | MB | Last change | Reads | In CLAUDE.md |', '|---|---|---|---|---|---|']
        for r in sorted(tops, key=lambda r: -r['mb']):
            L.append('| `%s/` | %d | %s | %s days | %d | %s |' % (
                r['folder'], r['files'], r['mb'], r['changed_days_ago'], r['reads'], 'yes' if r['in_claude_md'] else 'no'))
        L.append('')
    if NOT_CHECKED:
        L += ['## Not checked by the script', ''] + ['- ' + n for n in NOT_CHECKED] + ['']
    (out / 'report.md').write_text('\n'.join(L), encoding='utf-8')


def main():
    ap = argparse.ArgumentParser(description='Read-only scan of a Claude Code setup for zen.')
    ap.add_argument('--project-dir', default=os.getcwd())
    ap.add_argument('--days', type=int, default=30)
    ap.add_argument('--out')
    ap.add_argument('--context-dir', action='append', default=[])
    ap.add_argument('--skip-mcp', action='store_true')
    ap.add_argument('--quick', action='store_true', help='skip the workspace walk (folder map, large files)')
    ap.add_argument('--find-app', action='store_true',
                    help="search the home folder for the Claude app's data when it isn't in the usual place")
    a = ap.parse_args()
    global APPS, APP_SEARCH
    if a.find_app and not APPS:
        found, timed_out = find_app_dirs()
        APPS = found
        APP_SEARCH = 'found' if found else ('timed-out' if timed_out else 'none')
    P = Path(a.project_dir).resolve()
    base = CLAUDE / 'zen' / project_slug(P)
    out = Path(a.out) if a.out else base / datetime.now().strftime('%Y-%m-%d-%H%M')
    t0 = time.time()

    settings = load_settings(P)
    plugins = plugin_sources(P, settings)
    plugins_cache.extend(plugins)
    use, corrections, earliest, nfiles = scan_transcripts(a.days)
    skills = collect_skills(P, plugins)
    agents = collect_agents(P, plugins)
    corpus = build_corpus(P)
    catalog = model_catalog()
    servers = mcp_list(P, a.skip_mcp)

    check_connectors(servers, use, settings, a.days)
    check_listing(P, skills, settings, servers)
    check_skills(P, skills, use, corpus, a.days)
    check_agents(P, agents, use, a.days, corpus)
    check_plugins(plugins, skills, agents, use, a.days)
    jobs = check_scheduled(P, catalog, skills)
    hooks_n = check_hooks(P, settings, use, a.days)
    check_permissions(settings)
    instr = check_instructions(P)
    mem = check_memory(P)
    ctx = audit_context_layer(P, [Path(d).resolve() for d in a.context_dir], use, a.days)
    check_interface(settings, use, P)
    check_cowork(use, skills, a.days)
    wmap, big = workspace_map(P, use, a.quick)
    check_disk(P, big)
    check_models(P, settings, skills, agents, catalog)
    ctx_n = (ctx['coverage'] or {}).get('notes', 0)

    listed = [s for s in skills if s['kind'] == 'skill']
    base_tokens = {'skills': sum(s['tokens'] for s in listed),
                   'agents': sum(toks(x['desc_chars'] + len(x['name']) + 8) for x in agents),
                   'instructions': toks(instr), 'memory': mem}
    base_tokens['total'] = sum(base_tokens.values())
    counts = collections.Counter(f['area'] for f in FINDINGS)
    used_skills = {s['name'] for s in listed if (skill_use(use, s['name'], s['plugin'], s['origin']) or {}).get('n')}
    summary = {
        'date': datetime.now().strftime('%Y-%m-%d %H:%M'), 'project': tilde(P), 'days': a.days,
        'history_from': fmt_when(earliest), 'transcript_files': nfiles,
        'claude_version': run([claude_bin(), '--version'])[1].strip() if claude_bin() else None,
        'baseline': base_tokens,
        'counts': dict(counts, findings=len(FINDINGS),
                       high=sum(1 for f in FINDINGS if f['risk'] == 'high'),
                       skills_listed=len(listed), skill_names=len({s['name'] for s in listed}),
                       skills_used=len(used_skills), agents=len(agents),
                       plugins_enabled=sum(1 for p in plugins if p['enabled']),
                       connectors=len(servers or []),
                       connectors_connected=sum(1 for s in servers or [] if s['state'] == 'connected'),
                       connectors_broken=sum(1 for s in servers or [] if s['state'] in ('needs_auth', 'failed', 'degraded')),
                       scheduled_jobs=len(jobs), hooks=hooks_n, context_notes=ctx_n),
        'context_coverage': ctx['coverage'],
        'not_checked': NOT_CHECKED, 'seconds': round(time.time() - t0, 1),
    }
    firing = {k: list(v['samples']) for k, v in use['skill'].items() if v['model'] and v['samples']}
    write_outputs(out, summary, corrections, firing, ctx, wmap)
    base.mkdir(parents=True, exist_ok=True)
    with open(base / 'history.jsonl', 'a', encoding='utf-8') as fh:
        fh.write(json.dumps({'date': summary['date'], 'run': str(out), 'baseline': base_tokens,
                             'counts': summary['counts']}) + '\n')
    print(json.dumps({'run_folder': str(out), 'report': str(out / 'report.md'),
                      'findings': len(FINDINGS), 'by_area': dict(counts), 'high_risk': summary['counts']['high'],
                      'baseline_tokens': base_tokens, 'not_checked': NOT_CHECKED,
                      'seconds': summary['seconds']}, indent=1))


if __name__ == '__main__':
    main()
