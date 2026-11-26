#!/usr/bin/env bash
# Runs an App map screenshot scenario on a React Native app (bare or Expo), in a debug build.
#
#   run_shots.sh android <app dir> <map dir> <Scenario.kt> <out dir> [--minutes 20]
#
# 1. Copies appMapShots.js into the app and imports it first from the entry file (restored when
#    the run ends; the copy is listed in .git/info/exclude).
# 2. Starts the relay (relay.py) with the class names the map draws, and Metro.
# 3. Runs the Android adapter on <app dir>/android/app with --relay: each snap takes the
#    screenshot natively and gets the components' rects from the helper through the relay.
# Expo apps without an android/ folder get one from `npx expo prebuild --platform android`.
set -uo pipefail

platform="${1:?usage: run_shots.sh android <app dir> <map dir> <Scenario.kt> <out dir>}"
app="$(cd "${2:?app dir}" && pwd)"
map="$(cd "${3:?map dir}" && pwd)"
scenario="$(cd "$(dirname "${4:?scenario}")" && pwd)/$(basename "$4")"
out="${5:?out dir}"; shift 5
here="$(cd "$(dirname "$0")" && pwd)"
port=8765
[ "$platform" = android ] || { echo "only android is supported so far" >&2; exit 2; }

# The entry file: package.json "main", else index.js/ts/tsx.
entry="$(cd "$app" && node -p "require('./package.json').main || ''" 2>/dev/null)"
case "$entry" in
  ''|expo-router/entry|node_modules/*) entry="" ;;
esac
for candidate in "$entry" index.tsx index.ts index.js; do
  [ -n "$candidate" ] && [ -f "$app/$candidate" ] && { entry="$candidate"; break; }
done
if [ -z "$entry" ] || [ ! -f "$app/$entry" ]; then
  # Expo Router apps start at expo-router/entry: give them an entry that imports it after the helper.
  entry="index.app-map.js"
  printf "import 'expo-router/entry'\n" >"$app/$entry"
  created_entry=yes
fi
echo "entry: $entry"

cp "$here/appMapShots.js" "$app/appMapShots.js"
backup="$(mktemp)"; cp "$app/$entry" "$backup"
{ printf "import './appMapShots'\n"; cat "$backup"; } >"$app/$entry"
if git -C "$app" rev-parse --git-dir >/dev/null 2>&1; then
  exclude="$(git -C "$app" rev-parse --path-format=absolute --git-common-dir)/info/exclude"
  prefix="$(git -C "$app" rev-parse --show-prefix)"
  grep -qxF "${prefix}appMapShots.js" "$exclude" 2>/dev/null || echo "${prefix}appMapShots.js" >>"$exclude"
fi

cleanup() {
  cp "$backup" "$app/$entry"; rm -f "$backup" "$app/appMapShots.js"
  [ "${created_entry:-}" = yes ] && rm -f "$app/$entry"
  [ -n "${relay_pid:-}" ] && { kill "$relay_pid" 2>/dev/null; wait "$relay_pid" 2>/dev/null; }
  # Metro runs under npx: stop what listens on its port, not just the wrapper.
  [ -n "${metro_pid:-}" ] && { lsof -ti tcp:8081 -sTCP:LISTEN | xargs kill 2>/dev/null; kill "$metro_pid" 2>/dev/null; }
}
trap cleanup EXIT

mkdir -p "$out"; out="$(cd "$out" && pwd)"
# The Android runner empties <out> when it starts: these logs sit next to it, copied in at the end.
logs="$out.react-native"; mkdir -p "$logs"
python3 "$here/relay.py" "$map" --port "$port" >"$logs/relay.log" 2>&1 &
relay_pid=$!

if [ "$platform" = android ] && [ ! -d "$app/android" ]; then
  echo "no android/ folder: npx expo prebuild --platform android…"
  (cd "$app" && CI=1 npx expo prebuild --platform android --no-install >"$logs/prebuild.log" 2>&1) ||
    { echo "prebuild failed, see $logs/prebuild.log" >&2; exit 1; }
fi

if lsof -ti tcp:8081 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "something already listens on port 8081 (another Metro?): stop it first" >&2; exit 1
fi
if grep -q '"expo"' "$app/package.json"; then metro=(npx expo start --port 8081)
else metro=(npx react-native start --port 8081); fi
(cd "$app" && CI=1 "${metro[@]}" >"$logs/metro.log" 2>&1) &
metro_pid=$!
for _ in $(seq 60); do curl -s localhost:8081/status 2>/dev/null | grep -q running && break; sleep 2; done
echo "metro: $(curl -s localhost:8081/status)"

APP_MAP_EXTRA_INIT="$here/react-native.init.gradle" \
  "$here/../android/run_shots.sh" "$app/android/app" "$scenario" "$out" --real-app --relay "http://localhost:$port" "$@"
status=$?
cp "$logs"/*.log "$out"/ 2>/dev/null; rm -rf "$logs"
echo "relay: $(grep -c ' components$' "$out/relay.log") snap(s) answered by the app"
exit $status
