#!/usr/bin/env bash
set -Eeuo pipefail
umask 022

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT="$(cd -- "${SCRIPT_DIR}/../.." && pwd -P)"
VERSION="2.0.0"
APP_NAME="RiqatonyPad"
HOST_ARCH_RAW="$(uname -m)"
case "$HOST_ARCH_RAW" in
  x86_64) HOST_ARCH="x86_64" ;;
  aarch64|arm64) HOST_ARCH="aarch64" ;;
  *) printf 'Unsupported architecture: %s\n' "$HOST_ARCH_RAW" >&2; exit 2 ;;
esac
ARCH="${ARCH:-$HOST_ARCH}"
APPIMAGE="${1:-${ROOT}/dist/RiqatonyPad-${VERSION}-${ARCH}.AppImage}"
SHA_FILE="${APPIMAGE}.sha256"

[[ -x "$APPIMAGE" ]] || { echo "Missing executable AppImage: $APPIMAGE" >&2; exit 1; }
[[ -f "$SHA_FILE" ]] && (cd "$(dirname "$APPIMAGE")" && sha256sum -c "$(basename "$SHA_FILE")")

WORK_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/riqatonypad-postbuild.XXXXXX")"
SMOKE_HOME="${WORK_ROOT}/smoke-home"
EXTRACT_ROOT="${WORK_ROOT}/extract"
EXTRACTED_APPDIR="${EXTRACT_ROOT}/squashfs-root"
trap 'rm -rf "$WORK_ROOT"' EXIT

extract_final_appimage() {
  local log_file status
  mkdir -p "$EXTRACT_ROOT"
  log_file="${WORK_ROOT}/extract.log"
  set +e
  (
    cd "$EXTRACT_ROOT"
    "$APPIMAGE" --appimage-extract >"$log_file" 2>&1
  )
  status=$?
  set -e
  if [[ "$status" -ne 0 ]]; then
    cat "$log_file" >&2
    printf 'Completed AppImage extraction failed with exit code %s\n' "$status" >&2
    exit 1
  fi
  [[ -x "$EXTRACTED_APPDIR/AppRun" ]] || {
    printf 'Completed AppImage did not extract an executable squashfs-root/AppRun.\n' >&2
    exit 1
  }
  [[ -x "$EXTRACTED_APPDIR/usr/bin/riqatonypad" ]] || {
    printf 'Completed AppImage did not contain the RiqatonyPad launcher.\n' >&2
    exit 1
  }
}

run_gui_smoke() {
  local label="$1"
  local theme="$2"
  local iconset="$3"
  local log_file status
  rm -rf "$SMOKE_HOME"
  mkdir -p "$SMOKE_HOME/.config" "$SMOKE_HOME/.cache" "$SMOKE_HOME/.local/share" "$SMOKE_HOME/Documents"
  log_file="${WORK_ROOT}/gui-${theme}-${iconset}.log"
  set +e
  timeout 30s env "RIQATONYPAD_APPIMAGE_THEME=${theme}" "RIQATONYPAD_APPIMAGE_ICONSET=${iconset}" \
    HOME="$SMOKE_HOME" \
    XDG_CONFIG_HOME="$SMOKE_HOME/.config" \
    XDG_CACHE_HOME="$SMOKE_HOME/.cache" \
    XDG_DATA_HOME="$SMOKE_HOME/.local/share" \
    QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software \
    "$EXTRACTED_APPDIR/AppRun" --riqatonypad-smoke-test >"$log_file" 2>&1
  status=$?
  set -e
  if [[ "$status" -ne 0 ]] || ! grep -Fq 'GUI smoke test passed.' "$log_file"; then
    cat "$log_file" >&2
    printf '%s GUI smoke test failed with exit code %s\n' "$label" "$status" >&2
    exit 1
  fi
}

run_version_smoke() {
  local label="$1"
  local theme="$2"
  local log_file status expected
  expected="${APP_NAME} ${VERSION}"
  log_file="${WORK_ROOT}/version-${theme}.log"
  set +e
  timeout 30s env "RIQATONYPAD_APPIMAGE_THEME=${theme}" QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software \
    "$EXTRACTED_APPDIR/AppRun" --version >"$log_file" 2>&1
  status=$?
  set -e
  if [[ "$status" -ne 0 ]] || ! grep -Fxq "$expected" "$log_file"; then
    cat "$log_file" >&2
    printf '%s version smoke test failed with exit code %s\n' "$label" "$status" >&2
    exit 1
  fi
}

extract_final_appimage
for theme in system dark light; do
  for iconset in new classic original aero; do
    run_gui_smoke "${theme}-theme ${iconset}-icons" "$theme" "$iconset"
  done
  run_version_smoke "${theme}-theme" "$theme"
done

printf 'RiqatonyPad %s AppImage post-build tests passed (artifact extraction + system/dark/light x four-family icon GUI matrix).\n' "$VERSION"
