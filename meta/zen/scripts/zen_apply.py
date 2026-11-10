#!/usr/bin/env python3
"""Apply one approved tidy change at a time, reversibly, and log it so the whole run can be undone.

Every action writes a line to <run>/changes.jsonl with what it changed and how to put it back.
Nothing here deletes: archive moves things to a mirror folder, override flips a settings key,
pause-job stops a scheduled job but keeps it (a launch agent on a Mac, a Task Scheduler task on Windows).

Usage:
  python3 zen_apply.py --run RUN_DIR override SKILL STATE [--scope local|project|user]
  python3 zen_apply.py --run RUN_DIR archive PATH [--archive-root DIR]
  python3 zen_apply.py --run RUN_DIR pause-job LABEL     (launch agent label, or Task Scheduler task name)
  python3 zen_apply.py --run RUN_DIR backup FILE        (before Claude edits a settings or instruction file)
  python3 zen_apply.py --run RUN_DIR plugin-off KEY     (name@marketplace, or name@synced for an account plugin)
  python3 zen_apply.py --run RUN_DIR mcp-off NAME       (a server in this project's .mcp.json)
  python3 zen_apply.py --run RUN_DIR undo
Add --dry-run before the action to see what would happen.
"""
import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HOME = Path.home()
CLAUDE = HOME / '.claude'
AGENTS = HOME / 'Library' / 'LaunchAgents'
WINDOWS = platform.system() == 'Windows'
STATES = ('on', 'name-only', 'user-invocable-only', 'off')


def log(run, entry):
    run.mkdir(parents=True, exist_ok=True)
    entry['when'] = datetime.now().isoformat(timespec='seconds')
    with open(run / 'changes.jsonl', 'a', encoding='utf-8') as fh:
        fh.write(json.dumps(entry) + '\n')


def settings_path(scope, project):
    return {'local': project / '.claude' / 'settings.local.json',
            'project': project / '.claude' / 'settings.json',
            'user': CLAUDE / 'settings.json'}[scope]


def set_override(path, skill, state):
    data = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    ov = data.setdefault('skillOverrides', {})
    before = ov.get(skill)
    if state is None:
        ov.pop(skill, None)
        if not ov:
            data.pop('skillOverrides')
    else:
        ov[skill] = state
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    return before


def archive_target(src, project, root):
    src = src.resolve()
    for base, dest in ((project, root or project / 'archive'),
                       (CLAUDE, CLAUDE / 'zen' / 'archive' / 'claude'),
                       (AGENTS, CLAUDE / 'zen' / 'archive' / 'LaunchAgents')):
        try:
            return dest / src.relative_to(base)
        except ValueError:
            continue
    sys.exit('Refusing: %s is outside the project, ~/.claude and ~/Library/LaunchAgents.' % src)


def launchctl(verb, target):
    r = subprocess.run(['launchctl', verb, 'gui/%d' % os.getuid(), str(target)], capture_output=True, text=True)
    return r.returncode == 0, (r.stderr or r.stdout).strip()


def schtasks(name, switch):
    """Windows: /DISABLE or /ENABLE a Task Scheduler task. It stays in place either way."""
    r = subprocess.run(['schtasks', '/Change', '/TN', name, switch], capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    return r.returncode == 0, (r.stderr or r.stdout).strip()


def claude_bin():
    exe = HOME / '.local' / 'bin' / ('claude.exe' if WINDOWS else 'claude')
    return shutil.which('claude') or os.environ.get('CLAUDE_CODE_EXECPATH') or str(exe)


def main():
    ap = argparse.ArgumentParser(description='Apply one approved tidy change, reversibly.')
    ap.add_argument('--run', required=True, help='the tidy run folder the change belongs to')
    ap.add_argument('--project-dir', default=os.getcwd())
    ap.add_argument('--dry-run', action='store_true')
    sub = ap.add_subparsers(dest='action', required=True)
    o = sub.add_parser('override')
    o.add_argument('skill')
    o.add_argument('state', choices=STATES)
    o.add_argument('--scope', choices=('local', 'project', 'user'), default='local')
    a = sub.add_parser('archive')
    a.add_argument('path')
    a.add_argument('--archive-root')
    j = sub.add_parser('pause-job')
    j.add_argument('label')
    bk = sub.add_parser('backup')
    bk.add_argument('file')
    po = sub.add_parser('plugin-off')
    po.add_argument('key')
    mo = sub.add_parser('mcp-off')
    mo.add_argument('name')
    sub.add_parser('undo')
    args = ap.parse_args()
    run, project = Path(args.run), Path(args.project_dir).resolve()

    if args.action == 'override':
        path = settings_path(args.scope, project)
        if args.dry_run:
            return print('Would set skillOverrides["%s"] = "%s" in %s' % (args.skill, args.state, path))
        before = set_override(path, args.skill, args.state)
        log(run, {'action': 'override', 'file': str(path), 'skill': args.skill, 'before': before,
                  'after': args.state})
        print('Set %s to "%s" in %s (was %s).' % (args.skill, args.state, path, before or 'unset'))

    elif args.action == 'archive':
        src = Path(os.path.expanduser(args.path))
        if not src.is_absolute():
            src = project / src
        if not src.exists():
            sys.exit('Nothing at %s.' % src)
        dest = archive_target(src, project, Path(args.archive_root) if args.archive_root else None)
        if dest.exists():
            sys.exit('Refusing: %s already exists in the archive.' % dest)
        label = None
        if src.suffix == '.plist' and src.parent.resolve() == AGENTS.resolve():
            label = src.stem
        if args.dry_run:
            return print('Would move %s -> %s%s' % (src, dest, ' (after stopping %s)' % label if label else ''))
        if label:
            launchctl('bootout', src)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))
        log(run, {'action': 'archive', 'from': str(src), 'to': str(dest), 'launchd': bool(label)})
        print('Archived %s -> %s' % (src, dest))

    elif args.action == 'pause-job' and WINDOWS:
        if args.dry_run:
            return print('Would disable the Task Scheduler task %s (it stays in place).' % args.label)
        ok, msg = schtasks(args.label, '/DISABLE')
        if not ok:
            sys.exit('schtasks could not disable %s: %s' % (args.label, msg))
        log(run, {'action': 'pause-task', 'label': args.label})
        print('Disabled %s in Task Scheduler. Undo enables it again.' % args.label)

    elif args.action == 'pause-job':
        plist = AGENTS / (args.label + '.plist')
        if not plist.exists():
            sys.exit('No plist for %s in %s.' % (args.label, AGENTS))
        if args.dry_run:
            return print('Would stop %s (plist stays in place).' % args.label)
        ok, msg = launchctl('bootout', plist)
        if not ok:
            sys.exit('launchctl could not stop %s: %s' % (args.label, msg))
        log(run, {'action': 'pause-job', 'label': args.label, 'plist': str(plist)})
        print('Stopped %s. The plist is still there; undo starts it again.' % args.label)

    elif args.action == 'backup':
        src = Path(os.path.expanduser(args.file))
        if not src.is_absolute():
            src = project / src
        if not src.is_file():
            sys.exit('No file at %s.' % src)
        dest = run / 'backups' / re.sub(r'[\\/:]+', '__', str(src)).strip('_')
        if args.dry_run:
            return print('Would copy %s -> %s' % (src, dest))
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        log(run, {'action': 'backup', 'file': str(src), 'copy': str(dest)})
        print('Backed up %s. Edit it now; undo puts this copy back.' % src)

    elif args.action == 'plugin-off':
        claude = claude_bin()
        if args.dry_run:
            return print('Would run: claude plugin disable %s' % args.key)
        r = subprocess.run([claude, 'plugin', 'disable', args.key], capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit('claude plugin disable failed: %s' % (r.stderr or r.stdout).strip()[:300])
        log(run, {'action': 'plugin-off', 'key': args.key})
        print('Turned off %s on this machine (your claude.ai account keeps it).' % args.key)

    elif args.action == 'mcp-off':
        if not (project / '.mcp.json').exists() or args.name not in (json.loads((project / '.mcp.json').read_text(encoding='utf-8')).get('mcpServers') or {}):
            sys.exit('%s is not in this project\'s .mcp.json; use /mcp disable %s instead.' % (args.name, args.name))
        path = settings_path('local', project)
        if args.dry_run:
            return print('Would add %s to disabledMcpjsonServers in %s' % (args.name, path))
        data = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
        off = data.setdefault('disabledMcpjsonServers', [])
        if args.name not in off:
            off.append(args.name)
        path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
        log(run, {'action': 'mcp-off', 'file': str(path), 'name': args.name})
        print('Switched off %s for this project.' % args.name)

    elif args.action == 'undo':
        f = run / 'changes.jsonl'
        if not f.exists():
            sys.exit('No changes logged in %s.' % run)
        entries = [json.loads(l) for l in f.read_text(encoding='utf-8').splitlines() if l.strip()]
        for e in reversed(entries):
            if e.get('undone'):
                continue
            if args.dry_run:
                print('Would undo', json.dumps(e))
                continue
            if e['action'] == 'override':
                set_override(Path(e['file']), e['skill'], e['before'])
            elif e['action'] == 'archive':
                if Path(e['from']).exists():
                    print('Skipped: %s is back already.' % e['from'])
                    continue
                Path(e['from']).parent.mkdir(parents=True, exist_ok=True)
                shutil.move(e['to'], e['from'])
                if e.get('launchd'):
                    launchctl('bootstrap', e['from'])
            elif e['action'] == 'pause-job':
                launchctl('bootstrap', e['plist'])
            elif e['action'] == 'pause-task':
                schtasks(e['label'], '/ENABLE')
            elif e['action'] == 'backup':
                shutil.copy2(e['copy'], e['file'])
            elif e['action'] == 'plugin-off':
                subprocess.run([claude_bin(), 'plugin', 'enable', e['key']], capture_output=True)
            elif e['action'] == 'mcp-off':
                data = json.loads(Path(e['file']).read_text(encoding='utf-8'))
                data['disabledMcpjsonServers'] = [x for x in data.get('disabledMcpjsonServers', []) if x != e['name']]
                Path(e['file']).write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
            e['undone'] = datetime.now().isoformat(timespec='seconds')
            print('Undid', e['action'], e.get('skill') or e.get('from') or e.get('label') or e.get('key') or e.get('name') or e.get('file'))
        if not args.dry_run:
            f.write_text(''.join(json.dumps(e) + '\n' for e in entries), encoding='utf-8')


if __name__ == '__main__':
    main()
