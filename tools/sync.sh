#!/usr/bin/env bash
#
# Safe sync for two rooms working the same repository.
#
#   tools/sync.sh start          before you begin work
#   tools/sync.sh save "message" when you finish a piece of work
#
# The two rooms own different directories, so conflicts should be rare. This script
# makes them rarer by always rebasing onto the other room's work rather than creating
# merge commits, and by refusing to push anything that fails the tests.

set -uo pipefail
cd "$(dirname "$0")/.."

die() { printf '\n%s\n' "$*" >&2; exit 1; }

case "${1:-}" in
  start)
    echo "=== pulling the other room's work ==="
    git stash list | grep -q . && echo "note: you have stashes"
    if ! git diff --quiet || ! git diff --cached --quiet; then
      die "You have uncommitted changes. Commit or stash them before syncing:
  git status
  tools/sync.sh save \"what you did\""
    fi
    git pull --rebase origin main || die "Rebase hit a conflict. Resolve it, then:
  git rebase --continue"
    echo "=== running tests on the merged state ==="
    python3 -m unittest discover -s tests -t . 2>&1 | tail -3
    echo
    echo "Up to date. Working tree clean."
    ;;

  save)
    msg="${2:-}"
    [ -n "$msg" ] || die "usage: tools/sync.sh save \"commit message\""

    echo "=== tests ==="
    python3 -m unittest discover -s tests -t . 2>&1 | tail -3
    python3 -m unittest discover -s tests -t . >/dev/null 2>&1 \
      || die "Tests fail. Not committing."

    # Anything touching MQL5 must still compile before it can be pushed.
    if git status --porcelain | grep -qE '\.(mq5|mqh)$'; then
      echo "=== MQL5 changed, compiling ==="
      ./tools/mql5_compile.sh DEPLOYMENTS/NeoFL_CandleRevisit_v3_86 2>&1 | grep -E "Result|BUILD"
      ./tools/mql5_compile.sh DEPLOYMENTS/NeoFL_CandleRevisit_v3_86 >/dev/null 2>&1 \
        || die "MQL5 does not compile. Not committing."
    fi

    echo "=== secret scan ==="
    if git status --porcelain | awk '{print $2}' \
        | grep -iE '\.env|secret|credential|\.key$|\.pem$|assistant\.ini' ; then
      die "Refusing to commit: a file name looks like it carries secrets."
    fi

    git add -A
    git commit -q -m "$msg" || die "Nothing to commit."
    echo "=== rebasing onto the other room before pushing ==="
    git pull --rebase origin main || die "Rebase hit a conflict. Resolve, then:
  git rebase --continue && git push origin main"
    git push -q origin main
    echo
    echo "Pushed. The other room will pick this up on its next 'sync.sh start'."
    ;;

  *)
    echo "usage: tools/sync.sh {start|save \"message\"}"
    exit 1
    ;;
esac
