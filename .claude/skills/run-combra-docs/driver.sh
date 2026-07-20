#!/usr/bin/env bash
# driver.sh — build, serve, and screenshot the combra Sphinx docs site.
#
# This is the agent-facing handle on the docs. The site is a static Sphinx
# build (pydata-sphinx-theme); there is no application server, so "driving" it
# means: build the HTML, serve it over http, and screenshot pages with headless
# Chrome. Every command here was run in a headless Linux container.
#
# Run from the combra_docs unit root (the dir that contains docs/).
#
#   ./.claude/skills/run-combra-docs/driver.sh build            # build docs -> public/
#   ./.claude/skills/run-combra-docs/driver.sh shot             # build + screenshot index.html
#   ./.claude/skills/run-combra-docs/driver.sh shot api/angles.html get_started.html
#   ./.claude/skills/run-combra-docs/driver.sh serve            # build + serve foreground (Ctrl-C to stop)
#
# Env overrides:
#   SPHINX_PY   python interpreter that has the docs toolchain (default: python3)
#   PORT        http port for serve/shot (default: 8347)
#   SHOT_DIR    where screenshots land (default: ./_shots)
#   CHROME      chrome/chromium binary (default: first of google-chrome/chromium)
set -euo pipefail

SPHINX_PY="${SPHINX_PY:-python3}"
PORT="${PORT:-8347}"
SHOT_DIR="${SHOT_DIR:-$PWD/_shots}"
OUT="${OUT:-public}"

CHROME="${CHROME:-}"
if [ -z "$CHROME" ]; then
  for c in google-chrome chromium chromium-browser google-chrome-stable; do
    command -v "$c" >/dev/null 2>&1 && { CHROME="$c"; break; }
  done
fi

[ -d docs ] || { echo "ERROR: run from the combra_docs unit root (no ./docs here)"; exit 1; }

build() {
  # Same invocation as .github/workflows/pages.yaml: warnings are errors.
  "$SPHINX_PY" -m sphinx -b html -W --keep-going -j auto docs "$OUT"
  echo "built -> $OUT/index.html"
}

serve_bg() {
  "$SPHINX_PY" -m http.server "$PORT" --directory "$OUT" --bind 127.0.0.1 \
    >/tmp/combra_docs_http.log 2>&1 &
  SRV_PID=$!
  trap 'kill "$SRV_PID" 2>/dev/null || true' EXIT
  for _ in $(seq 1 40); do
    curl -sf -o /dev/null "http://127.0.0.1:$PORT/index.html" && return 0
    sleep 0.25
  done
  echo "ERROR: server did not come up; log:"; cat /tmp/combra_docs_http.log; exit 1
}

case "${1:-shot}" in
  build)
    build
    ;;
  serve)
    build
    echo "serving http://127.0.0.1:$PORT/  (Ctrl-C to stop)"
    exec "$SPHINX_PY" -m http.server "$PORT" --directory "$OUT" --bind 127.0.0.1
    ;;
  shot)
    shift || true
    pages=("$@"); [ ${#pages[@]} -eq 0 ] && pages=("index.html")
    [ -n "$CHROME" ] || { echo "ERROR: no chrome/chromium found; set CHROME=..."; exit 1; }
    [ -f "$OUT/index.html" ] || build
    mkdir -p "$SHOT_DIR"
    serve_bg
    for page in "${pages[@]}"; do
      name="$(echo "$page" | sed 's#[/.]#_#g').png"
      "$CHROME" --headless=new --no-sandbox --disable-gpu --hide-scrollbars \
        --window-size=1440,1400 --screenshot="$SHOT_DIR/$name" \
        "http://127.0.0.1:$PORT/$page" 2>/dev/null
      echo "shot -> $SHOT_DIR/$name  ($(wc -c <"$SHOT_DIR/$name") bytes)"
    done
    ;;
  *)
    echo "usage: driver.sh {build|serve|shot [page.html ...]}"; exit 2
    ;;
esac
