#!/usr/bin/env bash
set -euo pipefail

CORE_VERSION_FILE="spec/core/VERSION"

die() { echo "[VERSION_GATE] $*"; exit 23; }

# Semver parse: MAJOR.MINOR.PATCH
parse_major() {
  local v="$1"
  if [[ ! "$v" =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
    return 1
  fi
  echo "${BASH_REMATCH[1]}"
}

current_version="$(cat "$CORE_VERSION_FILE" 2>/dev/null || true)"
[ -n "$current_version" ] || die "Missing $CORE_VERSION_FILE"
current_major="$(parse_major "$current_version" || true)"
[ -n "$current_major" ] || die "Invalid semver in $CORE_VERSION_FILE: $current_version"

# CI ortamında base'i bul
base_ref="${GITHUB_BASE_REF:-}"
base_sha="${GITHUB_BASE_SHA:-}"

# fetch depth sığ ise karşılaştırma bozulur, o yüzden fetch etmeye çalış
git fetch --no-tags --prune origin +refs/heads/*:refs/remotes/origin/* >/dev/null 2>&1 || true

# Base commit seçimi:
# - PR varsa base sha/ref kullan
# - Yoksa origin/main ile kıyasla (push durumları için)
base=""
if [ -n "$base_sha" ]; then
  base="$base_sha"
elif [ -n "$base_ref" ] && git show -q "origin/$base_ref" >/dev/null 2>&1; then
  base="origin/$base_ref"
elif git show -q "origin/main" >/dev/null 2>&1; then
  base="origin/main"
else
  # En kötü senaryo: bir önceki commit
  base="HEAD~1"
fi

# Core değişmiş mi?
if git diff --name-only "$base"...HEAD -- spec/core | grep -q .; then
  # base tarafındaki VERSION'ı oku
  prev_version="$(git show "$base:$CORE_VERSION_FILE" 2>/dev/null || echo "")"
  [ -n "$prev_version" ] || die "Core changed but $CORE_VERSION_FILE is missing in base ($base). Add it on main first."

  prev_major="$(parse_major "$prev_version" || true)"
  [ -n "$prev_major" ] || die "Invalid semver in base $CORE_VERSION_FILE: $prev_version"

  if [ "$current_major" -le "$prev_major" ]; then
    die "spec/core changed but MAJOR not bumped. base=$prev_version current=$current_version"
  fi

  echo "[VERSION_GATE] OK: core changed, major bumped ($prev_version -> $current_version)"
else
  echo "[VERSION_GATE] OK: no core change detected"
fi
