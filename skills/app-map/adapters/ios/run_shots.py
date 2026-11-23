#!/usr/bin/env python3
"""Runs an App map screenshot scenario on an iOS simulator of its own.

Usage: run_shots.py --bundle <bundle id> --map <map dir> [--app <path.app>] <Scenario.swift> <out dir> [--minutes 20]

The scenario is an XCUITest (see example_scenario.swift) that drives the app by its bundle id,
so the app's own project isn't touched. At each `shots.snap(name)` this script takes the
screenshot with simctl and reads, with lldb, every view and view controller of the app with its
frame and how much of it is uncovered. The result is `<out>/<name>.png` and `<out>/drive.log`,
the same `SHOT RECT` lines the Flutter adapter writes, for `app-map crop`: one per view whose class
(or owning view controller, or hosted SwiftUI view) the map's diagrams draw.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DRIVER = os.path.join(HERE, 'AppMapDriver')
CACHE = os.path.join(os.path.expanduser('~'), '.cache', 'app-map', 'ios-driver')
SIMULATOR = 'app-map iPhone 17'

# The lldb expression that lists the app's views: view_dump.swift on one line.
DUMP = ' ; '.join(line for line in open(os.path.join(HERE, 'view_dump.swift')).read().splitlines()
                  if line.strip() and not line.startswith('//')).replace('{ ;', '{').replace('; }', ' }')


def run(*command, **options):
    return subprocess.run(command, capture_output=True, text=True, **options)


def type_names(raw):
    """Swift and Objective-C names in a runtime class name: `App.Cell` → Cell,
    `_TtC3App4Cell` → App, Cell; a hosting controller's generic argument (a SwiftUI view) too."""
    names = []
    for part in raw.split('|'):
        if part.startswith('_Tt'):
            text, index = part[3:], 0
            while index < len(text):
                match = re.match(r'(\d+)', text[index:])
                if not match:
                    index += 1
                    continue
                length = int(match.group(1))
                start = index + len(match.group(1))
                names.append(text[start:start + length])
                index = start + length
        else:
            names += re.findall(r'[A-Za-z_]\w*', part)
    return names


def map_classes(map_dir):
    """Every class name in the map's diagrams (`class X` in its Mermaid sources)."""
    names = set()
    for name in os.listdir(map_dir):
        if name.endswith('.md'):
            names.update(re.findall(r'^\s*class ([A-Za-z_]\w*)', open(os.path.join(map_dir, name)).read(), re.M))
    return names


def simulator():
    listing = run('xcrun', 'simctl', 'list', 'devices').stdout
    match = re.search(re.escape(SIMULATOR) + r' \(([0-9A-F-]{36})\)', listing)
    if match:
        udid = match.group(1)
    else:
        runtimes = re.findall(r'(com\.apple\.CoreSimulator\.SimRuntime\.iOS-[\d-]+)', run('xcrun', 'simctl', 'list', 'runtimes').stdout)
        udid = run('xcrun', 'simctl', 'create', SIMULATOR, 'iPhone 17', runtimes[-1]).stdout.strip()
    run('xcrun', 'simctl', 'boot', udid)
    run('xcrun', 'simctl', 'bootstatus', udid, '-b')
    return udid


def app_pid(udid, bundle):
    container = run('xcrun', 'simctl', 'get_app_container', udid, bundle).stdout.strip()
    executable = run('/usr/libexec/PlistBuddy', '-c', 'Print CFBundleExecutable', os.path.join(container, 'Info.plist')).stdout.strip()
    pids = run('pgrep', '-f', os.path.join(container, executable)).stdout.split()
    return pids[0] if pids else None


def dump_views(pid):
    result = run('xcrun', 'lldb', '--batch', '-p', pid,
                 '-o', 'expr -l swift -O -- ' + DUMP, timeout=180)
    return [line for line in result.stdout.splitlines() if line.startswith(('W ', 'V '))]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('scenario')
    parser.add_argument('out')
    parser.add_argument('--bundle', required=True)
    parser.add_argument('--map', required=True)
    parser.add_argument('--app')
    parser.add_argument('--minutes', type=float, default=20)
    args = parser.parse_args()
    out = os.path.abspath(args.out)
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(os.path.join(out, 'requests'))

    classes = map_classes(args.map)
    udid = simulator()
    if args.app:
        run('xcrun', 'simctl', 'uninstall', udid, args.bundle)
        installed = run('xcrun', 'simctl', 'install', udid, args.app)
        if installed.returncode:
            sys.exit(installed.stderr)

    # The driver project with this scenario in it, built once per scenario change.
    project = os.path.join(CACHE, 'AppMapDriver')
    shutil.rmtree(project, ignore_errors=True)
    shutil.copytree(DRIVER, project)
    shutil.copy(args.scenario, os.path.join(project, 'UITests', 'AppMapScenario.swift'))
    common = ['-project', os.path.join(project, 'AppMapDriver.xcodeproj'), '-scheme', 'AppMapUITests',
              '-destination', f'id={udid}', '-derivedDataPath', os.path.join(CACHE, 'build')]
    print('building the driver…', flush=True)
    built = run('xcodebuild', 'build-for-testing', *common)
    if built.returncode:
        sys.exit('\n'.join(line for line in built.stdout.splitlines() if 'error:' in line) or built.stdout[-3000:])

    environment = dict(os.environ, TEST_RUNNER_APP_MAP_OUT=out, TEST_RUNNER_APP_MAP_BUNDLE=args.bundle)
    print(f'running the scenario on {SIMULATOR} ({args.bundle})…', flush=True)
    with open(os.path.join(out, 'xcodebuild.log'), 'w') as log:
        test = subprocess.Popen(['xcodebuild', 'test-without-building', *common], stdout=log, stderr=log, env=environment)

    requests = os.path.join(out, 'requests')
    lines, screen, taken = [], None, set()
    deadline = time.time() + args.minutes * 60
    while time.time() < deadline:
        running = test.poll() is None
        for name in sorted(os.listdir(requests)):
            if name.endswith(('.done', '.tree')) or name in ('failures', 'report') or name in taken:
                continue
            taken.add(name)
            run('xcrun', 'simctl', 'io', udid, 'screenshot', os.path.join(out, name + '.png'))
            pid = app_pid(udid, args.bundle)
            views = dump_views(pid) if pid else []
            for line in views:
                parts = line.split()
                if parts[0] == 'W' and screen is None:
                    screen = (parts[1], parts[2])
                    lines.append(f'SHOT SCREEN {parts[1]} {parts[2]}')
                elif parts[0] == 'V':
                    raw, left, top, width, height, hits = parts[1:7]
                    for type_name in dict.fromkeys(name for name in type_names(raw) if name in classes):
                        lines.append(f'SHOT RECT {name} {type_name} {left} {top} {width} {height} {hits}')
            lines.append(f'SHOT TAKEN {name} ({len(views)} views)')
            print(f'  {name}: {len(views)} views', flush=True)
            open(os.path.join(requests, name + '.done'), 'w').close()
        if not running:
            break
        time.sleep(0.3)
    if test.poll() is None:
        test.kill()
    for extra in ('failures', 'report'):
        path = os.path.join(requests, extra)
        if os.path.exists(path):
            lines += open(path).read().splitlines()
    with open(os.path.join(out, 'drive.log'), 'w') as log:
        log.write('\n'.join(lines) + '\n')
    for line in lines:
        if line.startswith(('SHOT STEP FAILED', 'SHOT DONE')):
            print(line)
    print(f'{len(taken)} screenshots in {out}')


if __name__ == '__main__':
    main()
