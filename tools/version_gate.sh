#!/usr/bin/env bash
set -euo pipefail

CORE_VERSION_FILE="spec/core/VERSION"

die() { echo "[VERSION_GATE] FAIL: $*" >&2; exit 63; }

parse_major() {
  # "12.3.4" -> 12
  echo "$1" | awk -F. '{print $1}'
}

# Resolve base ref/sha if present (PR context)
base_ref="${GITHUB_BASE_REF:-}"
base_sha="${GITHUB_BASE_SHA:-}"

# Ensure we have remote refs even in shallow CI clones
git fetch --no-tags --prune origin +refs/heads/*:refs/remotes/origin/* >/dev/null 2>&1 || true

# Base selection:
# - Prefer explicit PR base SHA
# - Else PR base ref
# - Else origin/main
# - Fallback to HEAD~1
base=""
if [ -n "$base_sha" ]; then
  base="$base_sha"
elif [ -n "$base_ref" ] && git show -q "origin/$base_ref" >/dev/null 2>&1; then
  base="origin/$base_ref"
elif git show -q "origin/main" >/dev/null 2>&1; then
  base="origin/main"
else
  base="HEAD~1"
fi

# Detect spec/core changes from:
# 1) commit range (base...HEAD)
# 2) staged changes
# 3) working tree changes
core_changed=0
if git diff --name-only "$base"...HEAD -- spec/core | grep -q .; then core_changed=1; fi
if git diff --name-only --cached -- spec/core | grep -q .; then core_changed=1; fi
if git diff --name-only -- spec/core | grep -q .; then core_changed=1; fi

if [ "$core_changed" -eq 1 ]; then
  prev_version="$(git show "$base:$CORE_VERSION_FILE" 2>/dev/null || echo "")"
  [ -n "$prev_version" ] || die "spec/core changed but $CORE_VERSION_FILE is missing in base ($base). Add it on main first."

  prev_major="$(parse_major "$prev_version" || true)"
  [ -n "$prev_major" ] || die "invalid semver in base $CORE_VERSION_FILE: $prev_version"

  [ -f "$CORE_VERSION_FILE" ] || die "spec/core changed but $CORE_VERSION_FILE is missing in the working tree"
  current_version="$(cat "$CORE_VERSION_FILE")"
  current_major="$(parse_major "$current_version" || true)"
  [ -n "$current_major" ] || die "invalid semver in current $CORE_VERSION_FILE: $current_version"

  # Strict rule: if spec/core changes, MAJOR must increase
  if [ "$current_major" -le "$prev_major" ]; then
    die "spec/core changed but MAJOR not bumped. base=$prev_version current=$current_version"
  fi

  echo "[VERSION_GATE] OK: spec/core changed, major bumped ($prev_version -> $current_version)"
else
  echo "[VERSION_GATE] OK: no spec/core change detected"
fi
