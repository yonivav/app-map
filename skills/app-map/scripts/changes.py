"""Keeps an App map current.

  changes.py changes <map dir> <repo root>   what changed in the code since the map was synced
  changes.py sync <map dir> <repo root>      record the repo's HEAD as the map's synced commit
  changes.py where <map dir> <repo root> <Class | path>   where the map draws a class or a file's classes

The synced commit lives in <map dir>/app-map.json ({"synced": {"commit", "date"}}).
`changes` lists, per module page: classes the page draws whose file changed (review the page),
names the page draws that no longer exist (fix the page), and new classes in a module's key
files that no page draws yet (consider adding them).
"""
import datetime
import glob
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from facts import TYPE_KINDS  # noqa: E402
from index_code import load_declarations, names_in, where_drawn  # noqa: E402

DRAWABLE_KINDS = TYPE_KINDS + ('enum', 'composable function')


def git(root, *args):
    return subprocess.run(['git', '-C', root, *args], capture_output=True, text=True).stdout


def config_path(map_dir):
    return os.path.join(map_dir, 'app-map.json')


def load_config(map_dir):
    try:
        with open(config_path(map_dir)) as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {}


def module_pages(map_dir):
    return sorted(page for page in glob.glob(os.path.join(map_dir, '*.html'))
                  if os.path.basename(page) != 'index.html')


def key_files(map_dir, module):
    """Paths listed in a module's "Key files" section (its Markdown source)."""
    source = os.path.join(map_dir, module + '.md')
    if not os.path.exists(source):
        return []
    with open(source, encoding='utf-8') as handle:
        text = handle.read()
    section = re.search(r'^## Key files[^\n]*\n([\s\S]*?)(?=^## |\Z)', text, re.M)
    return re.findall(r'^- `([^`]+)`', section.group(1), re.M) if section else []


def changes(map_dir, root):
    config = load_config(map_dir)
    commit = (config.get('synced') or {}).get('commit')
    if not commit:
        sys.exit('No synced commit yet: run `app-map sync <map> <repo>` once the map is current.')
    changed = set(git(root, 'diff', '--name-only', commit, '--').split()) | \
        set(git(root, 'ls-files', '--others', '--exclude-standard').split())
    log = git(root, 'log', '--oneline', f'{commit}..HEAD').strip().splitlines()
    by_name, _, _ = load_declarations(root)
    file_of = {name: found[0]['file'] for name, found in by_name.items()}
    in_changed = {}
    for name, found in by_name.items():
        for decl in found:
            if decl['file'] in changed and decl['kind'] in DRAWABLE_KINDS \
                    and not name.endswith('State'):
                in_changed.setdefault(decl['file'], []).append(name)
    drawn_anywhere = set(where_drawn(module_pages(map_dir)))
    print(f'Synced at {commit[:10]}; {len(log)} commit(s) and {len(changed)} changed file(s) since.\n')
    for page in module_pages(map_dir):
        module = os.path.splitext(os.path.basename(page))[0]
        with open(page, encoding='utf-8') as handle:
            sources = re.findall(r'<script type="text/plain"[^>]*>([\s\S]*?)</script>', handle.read())
        drawn = set().union(*[names_in(source) for source in sources] or [set()])
        review = sorted(name for name in drawn if file_of.get(name) in changed)
        # "external" in app-map.json: framework, native or actor names drawn on purpose.
        known = set(config.get('external') or []) | {'User'}
        gone = sorted(name for name in drawn if name not in by_name and name not in known)
        keys = key_files(map_dir, module)
        new = sorted({name for path, names in in_changed.items() for name in names
                      if any(path == key or path.startswith(key.rstrip('/') + '/') for key in keys)
                      and name not in drawn_anywhere and not name.startswith('_')})
        if not (review or gone or new):
            continue
        print(module)
        if review:
            print('  review (file changed): ' + ', '.join(f'{name} ({file_of[name]})' for name in review))
        if gone:
            print('  not in the code (renamed, deleted or framework): ' + ', '.join(gone))
        if new:
            print('  new or changed, not drawn yet: ' + ', '.join(new))
    print('\nUpdate those pages\' Markdown, run `app-map build`, `app-map verify`, then `app-map sync`.')


def sync(map_dir, root):
    config = load_config(map_dir)
    commit = git(root, 'rev-parse', 'HEAD').strip()
    config['synced'] = {'commit': commit, 'date': datetime.date.today().isoformat()}
    with open(config_path(map_dir), 'w') as handle:
        json.dump(config, handle, indent=2)
        handle.write('\n')
    print(f'Map synced to {commit[:10]}.')


def where(map_dir, root, query):
    spots = where_drawn(module_pages(map_dir))
    by_name, _, _ = load_declarations(root)
    if query in by_name or query in spots:
        names = [query]
    else:
        rel = os.path.relpath(os.path.realpath(os.path.join(root, query)), root) if not os.path.isabs(query) \
            else os.path.relpath(query, root)
        names = sorted({decl['name'] for found in by_name.values() for decl in found if decl['file'] == rel})
        if not names:
            sys.exit(f'{query}: not a class or a file in {root}')
    for name in names:
        places = spots.get(name)
        file = by_name[name][0]['file'] if name in by_name else 'not in the code'
        if places:
            print(f'{name} ({file})')
            for page, section_id, title in places:
                print(f'  {page}.html#{section_id} · {title}')
        else:
            print(f'{name} ({file}): not drawn on the map')


def main():
    command, map_dir, root = sys.argv[1], sys.argv[2], os.path.realpath(sys.argv[3])
    if command == 'changes':
        changes(map_dir, root)
    elif command == 'sync':
        sync(map_dir, root)
    elif command == 'where':
        where(map_dir, root, sys.argv[4])
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main()
