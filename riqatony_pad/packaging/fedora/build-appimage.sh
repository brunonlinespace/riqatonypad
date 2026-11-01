#!/usr/bin/env bash
set -Eeuo pipefail
umask 022

# RiqatonyPad AppImage builder aligned with the current Suite Pythoine packaging
# hardening. Deliberately non-privileged: no sudo, su, pkexec, dnf or other
# system-package installation is performed. Python build dependencies live
# only in the isolated build virtualenv; missing host tools are reported and
# the build stops.

APP_NAME="RiqatonyPad"
APP_ID="riqatonypad"
APP_VERSION="2.0.0"
DESKTOP_ID="io.github.brunonlinespace.riqatonypad"

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
PROGRAM_ROOT="$(cd -- "${SCRIPT_DIR}/../.." && pwd -P)"
PROJECT_ROOT="$(cd -- "${PROGRAM_ROOT}/.." && pwd -P)"
SOURCE_ENTRY="${PROJECT_ROOT}/main.py"
COMPONENT_MANIFEST="${PROJECT_ROOT}/suite-pythoine-component.json"
SOURCE_FILE="${PROGRAM_ROOT}/app.py"
EDITOR_WIDGETS="${PROGRAM_ROOT}/widgets/rwpyn/editor_widgets.py"
EDITOR_FORMATTING="${PROGRAM_ROOT}/widgets/rwpyn/editor_formatting.py"
EDITOR_INSERTION="${PROGRAM_ROOT}/widgets/rwpyn/editor_insertion.py"
EDITOR_SEARCH_VIEW="${PROGRAM_ROOT}/widgets/rwpyn/editor_search_view.py"
EDITOR_PRINTING="${PROGRAM_ROOT}/widgets/rwpyn/editor_printing.py"
EDITOR_PREFERENCES="${PROGRAM_ROOT}/widgets/rwpyn/editor_preferences.py"
EDITOR_RIBBON_RETRO="${PROGRAM_ROOT}/widgets/editor_ribbon_retro.py"
EDITOR_COMMANDS_APPEARANCE="${PROGRAM_ROOT}/widgets/editor_commands_appearance.py"
EDITOR_PLATFORM_STARTUP="${PROGRAM_ROOT}/editor_platform_startup.py"
EDITOR_LIFECYCLE="${PROGRAM_ROOT}/widgets/rwpyn/editor_lifecycle.py"
RTF_CODEC="${PROGRAM_ROOT}/rtf_codec.py"
RICH_TEXT_SUPPORT="${PROGRAM_ROOT}/rich_text_support.py"
RTF_NEW_DOCUMENT="${PROGRAM_ROOT}/rtf_new_document.py"
SHORTCUT_SEARCH="${PROGRAM_ROOT}/widgets/keyboard_shortcuts.py"
ABOUT_DIALOG="${PROGRAM_ROOT}/widgets/about_dialog.py"
CHARACTER_COUNT="${PROGRAM_ROOT}/widgets/rwpyn/character_count.py"
MESSAGE_CONVENTIONS="${PROGRAM_ROOT}/widgets/message_conventions.py"
QUICK_TOUR="${PROGRAM_ROOT}/widgets/quick_tour.py"
SOURCE_MANIFEST="${PROGRAM_ROOT}/SOURCE_MANIFEST.sha256"
RUNTIME_REQUIREMENTS="${PROGRAM_ROOT}/requirements.txt"
BUILD_REQUIREMENTS="${PROGRAM_ROOT}/packaging/pyinstaller/build-requirements.txt"
STATIC_QA="${PROGRAM_ROOT}/qa/static-qa.sh"
QT_RTF_QA="${PROGRAM_ROOT}/qa/qt-rtf-qa.py"
QT_HIGHLIGHT_QA="${PROGRAM_ROOT}/qa/highlight-runtime-qa.py"
QT_FIND_TOGGLE_QA="${PROGRAM_ROOT}/qa/find-toggle-qt-qa.py"
ASSET_DIR="${PROGRAM_ROOT}/assets/icons"
HICOLOR_DIR="${PROGRAM_ROOT}/assets/hicolor"
RIBBON_ICON_DIR="${PROGRAM_ROOT}/assets/ribbon-icons"
CLASSIC_RIBBON_ICON_DIR="${PROGRAM_ROOT}/assets/ribbon-icons-classic"
LEGACY_RIBBON_ICON_DIR="${PROGRAM_ROOT}/assets/ribbon-icons-original"
AERO_RIBBON_ICON_DIR="${PROGRAM_ROOT}/assets/ribbon-icons-aero"
STYLE_DIR="${PROGRAM_ROOT}/assets/styles"
TEMPLATE_DIR="${PROGRAM_ROOT}/assets/templates"
APPIMAGE_PAYLOAD="${PROGRAM_ROOT}/packaging/appimage"
DOCS_DIR="${PROGRAM_ROOT}/docs"

HOST_ARCH_RAW="$(uname -m)"
case "$HOST_ARCH_RAW" in
    x86_64) HOST_ARCH="x86_64" ;;
    aarch64|arm64) HOST_ARCH="aarch64" ;;
    *) printf 'Error: unsupported build architecture: %s\n' "$HOST_ARCH_RAW" >&2; exit 2 ;;
esac
ARCH="${ARCH:-$HOST_ARCH}"

FEDORA_RELEASE="unknown"
HOST_NAME="unknown Linux"
OS_ID="unknown"
if [[ -r /etc/os-release ]]; then
    mapfile -d '' -t OS_RELEASE_VALUES < <(
        set +u
        # shellcheck disable=SC1091
        source /etc/os-release
        printf '%s\0%s\0%s\0' "${ID:-unknown}" "${VERSION_ID:-unknown}" "${PRETTY_NAME:-unknown Linux}"
    )
    OS_ID="${OS_RELEASE_VALUES[0]:-unknown}"
    FEDORA_RELEASE="${OS_RELEASE_VALUES[1]:-unknown}"
    HOST_NAME="${OS_RELEASE_VALUES[2]:-unknown Linux}"
fi

BUILD_ROOT="${BUILD_ROOT:-${PROGRAM_ROOT}/build/appimage-fedora${FEDORA_RELEASE}-${ARCH}}"
VENV="${BUILD_ROOT}/venv"
PYI_WORK="${BUILD_ROOT}/pyinstaller-work"
PYI_DIST="${BUILD_ROOT}/pyinstaller-dist"
FINAL_APPDIR="${BUILD_ROOT}/RiqatonyPad.AppDir"
SOURCE_STAGE="${BUILD_ROOT}/source-stage"
SMOKE_HOME="${BUILD_ROOT}/smoke-home"
FINAL_EXTRACT_ROOT="${BUILD_ROOT}/final-appimage-extract"
FINAL_EXTRACT_APPDIR="${FINAL_EXTRACT_ROOT}/squashfs-root"
DIST_DIR="${OUTPUT_DIR:-${PROGRAM_ROOT}/dist}"
CACHE_DIR="${XDG_CACHE_HOME:-${HOME}/.cache}/riqatonypad-appimage-tools"

APPIMAGE="${DIST_DIR}/${APP_NAME}-${APP_VERSION}-${ARCH}.AppImage"
SHA_FILE="${APPIMAGE}.sha256"
BUILD_INFO="${DIST_DIR}/${APP_NAME}-${APP_VERSION}-${ARCH}.build-info.txt"
PYTHON_LOCK="${DIST_DIR}/${APP_NAME}-${APP_VERSION}-${ARCH}.build-python-lock.txt"
APPIMAGETOOL_RESOLVED=""
MAX_TOOL_BYTES=$((200 * 1024 * 1024))

export PYTHONDONTWRITEBYTECODE=1

log() { printf '\n==> %s\n' "$*"; }
die() { printf 'Error: %s\n' "$*" >&2; exit 1; }
require_file() { [[ -f "$1" ]] || die "Missing file: $1"; }

validate_build_root() {
    local allowed_root resolved_root
    allowed_root="$(readlink -m -- "${PROGRAM_ROOT}/build")"
    resolved_root="$(readlink -m -- "$BUILD_ROOT")"
    [[ "$resolved_root" != "$allowed_root" ]] \
        || die "BUILD_ROOT must be a child directory beneath ${allowed_root}; refusing to remove the build root itself."
    case "$resolved_root" in
        "$allowed_root"/*) ;;
        *) die "Unsafe BUILD_ROOT outside ${allowed_root}: ${resolved_root}" ;;
    esac
}

clean_source_python_caches() {
    while IFS= read -r -d '' cache_dir; do
        rm -rf -- "$cache_dir"
    done < <(
        find "$PROJECT_ROOT" \
            \( -path "$PROJECT_ROOT/.git" \
               -o -path "$PROJECT_ROOT/.venv" \
               -o -path "$PROJECT_ROOT/venv" \
               -o -path "$PROGRAM_ROOT/build" \
               -o -path "$PROGRAM_ROOT/dist" \) -prune \
            -o -type d -name '__pycache__' -print0
    )
    while IFS= read -r -d '' bytecode_file; do
        rm -f -- "$bytecode_file"
    done < <(
        find "$PROJECT_ROOT" \
            \( -path "$PROJECT_ROOT/.git" \
               -o -path "$PROJECT_ROOT/.venv" \
               -o -path "$PROJECT_ROOT/venv" \
               -o -path "$PROGRAM_ROOT/build" \
               -o -path "$PROGRAM_ROOT/dist" \) -prune \
            -o -type f \( -name '*.pyc' -o -name '*.pyo' \) -print0
    )
}

cleanup() {
    rm -rf "$SMOKE_HOME" "$SOURCE_STAGE" "$FINAL_EXTRACT_ROOT"
    clean_source_python_caches
}
trap cleanup EXIT

check_non_privileged_policy() {
    if grep -Eq '^[[:space:]]*(sudo|dnf|pkexec|su)([[:space:]]|$)' "$0"; then
        die "Privilege-elevation or host-package-install command detected in builder."
    fi
}

check_host_prerequisites() {
    log "Checking non-privileged host prerequisites"
    local missing=() command_name
    for command_name in python3 bash timeout sha256sum od stat find grep cp ln chmod install mktemp dirname tail cat \
        rm mkdir mv tr awk cut date uname readlink sort env wc; do
        command -v "$command_name" >/dev/null 2>&1 || missing+=("$command_name")
    done
    if ! command -v curl >/dev/null 2>&1 && ! command -v wget >/dev/null 2>&1; then
        missing+=("curl-or-wget")
    fi
    if ((${#missing[@]})); then
        die "Missing required host command(s): ${missing[*]}. The builder will not install system packages; provide them and rerun."
    fi
    python3 - <<'PYVENV' >/dev/null 2>&1 || \
        die "This Python cannot create virtual environments. Provide Python with venv/ensurepip support and rerun."
import ensurepip, venv
PYVENV
}

check_inputs() {
    validate_build_root
    if (( EUID == 0 )) && [[ "${RIQATONYPAD_ALLOW_ROOT_BUILD:-0}" != "1" ]]; then
        die "Do not run the RiqatonyPad AppImage builder with sudo/root."
    fi
    case "$ARCH" in x86_64|aarch64) ;; *) die "Unsupported AppImage architecture: ${ARCH}" ;; esac
    [[ "$ARCH" == "$HOST_ARCH" ]] || die "Requested ${ARCH}, but host is ${HOST_ARCH_RAW}; cross-building is unsupported."
    if [[ "$OS_ID" != "fedora" || ! "$FEDORA_RELEASE" =~ ^(43|44)$ ]]; then
        if [[ "${RIQATONYPAD_ALLOW_UNSUPPORTED_HOST:-0}" != "1" ]]; then
            die "Validated for Fedora 43/44. Detected ${HOST_NAME}. Set RIQATONYPAD_ALLOW_UNSUPPORTED_HOST=1 only for intentional testing."
        fi
        printf 'Warning: continuing on unsupported host: %s\n' "$HOST_NAME" >&2
    fi

    for path in \
        "$SOURCE_ENTRY" "$COMPONENT_MANIFEST" "$SOURCE_FILE" "$EDITOR_WIDGETS" "$EDITOR_FORMATTING" "$EDITOR_INSERTION" "$EDITOR_SEARCH_VIEW" "$EDITOR_PRINTING" "$EDITOR_PREFERENCES" "$EDITOR_RIBBON_RETRO" "$EDITOR_COMMANDS_APPEARANCE" "$EDITOR_PLATFORM_STARTUP" "$EDITOR_LIFECYCLE" "$CHARACTER_COUNT" "$MESSAGE_CONVENTIONS" "$RTF_CODEC" "$RICH_TEXT_SUPPORT" "$RTF_NEW_DOCUMENT" "$SOURCE_MANIFEST" \
        "$RUNTIME_REQUIREMENTS" "$BUILD_REQUIREMENTS" "$STATIC_QA" "$QT_RTF_QA" \
        "${ASSET_DIR}/riqatonypad.png" "${ASSET_DIR}/riqatonypad-about.png" \
        "${RIBBON_ICON_DIR}/light/superscript.png" "${RIBBON_ICON_DIR}/dark/superscript.png" \
        "${RIBBON_ICON_DIR}/light/subscript.png" "${RIBBON_ICON_DIR}/dark/subscript.png" \
        "${CLASSIC_RIBBON_ICON_DIR}/light/superscript.png" "${CLASSIC_RIBBON_ICON_DIR}/dark/superscript.png" \
        "${CLASSIC_RIBBON_ICON_DIR}/light/subscript.png" "${CLASSIC_RIBBON_ICON_DIR}/dark/subscript.png" \
        "${LEGACY_RIBBON_ICON_DIR}/light/subscript.png" "${LEGACY_RIBBON_ICON_DIR}/dark/subscript.png" \
        "${AERO_RIBBON_ICON_DIR}/light/subscript.png" "${AERO_RIBBON_ICON_DIR}/dark/subscript.png" \
        "${APPIMAGE_PAYLOAD}/AppRun" "${APPIMAGE_PAYLOAD}/riqatonypad.desktop" \
        "${APPIMAGE_PAYLOAD}/riqatonypad.png" \
        "${APPIMAGE_PAYLOAD}/io.github.brunonlinespace.riqatonypad.metainfo.xml" \
        "${APPIMAGE_PAYLOAD}/styles/breeze-dark.qss" "${APPIMAGE_PAYLOAD}/styles/breeze-light.qss" \
        "${PROGRAM_ROOT}/LICENSE" "${TEMPLATE_DIR}/default-document.rtf" \
        "${DOCS_DIR}/RiqatonyPad-Documentation.rtf" "${DOCS_DIR}/README.md" "${DOCS_DIR}/QA_TEST_PLAN.md" \
        "${DOCS_DIR}/RELEASE_NOTES.md"; do
        require_file "$path"
    done
    for size in 16 22 24 32 48 64 128 256 512; do
        require_file "${HICOLOR_DIR}/${size}x${size}/apps/riqatonypad.png"
    done

    python3 - "$COMPONENT_MANIFEST" "$APP_ID" "$APP_NAME" "$APP_VERSION" "$DESKTOP_ID" <<'PYMANIFEST'
import json
from pathlib import Path
import sys
path = Path(sys.argv[1])
expected_id, expected_name, expected_version, expected_desktop = sys.argv[2:]
try:
    data = json.loads(path.read_text(encoding="utf-8"))
except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
    raise SystemExit(f"Invalid Suite Pythoine component manifest: {exc}")
expected = {
    "id": expected_id,
    "name": expected_name,
    "version": expected_version,
    "component_kind": "editor",
    "desktop_id": "riqatonypad",
    "publisher_id": "brunonlinespace",
}
for key, value in expected.items():
    if data.get(key) != value:
        raise SystemExit(f"Suite component manifest mismatch for {key}: {data.get(key)!r} != {value!r}")
if data.get("portable_command") != ["main.py"]:
    raise SystemExit('Suite component manifest must declare portable_command ["main.py"]')
if data.get("extensions") != [".rtf"]:
    raise SystemExit("Suite component manifest must declare only the .rtf extension")
if data.get("tagline") != "Friendly. Fast. Focused.":
    raise SystemExit("Suite component manifest must preserve RiqatonyPad's current slogan")
capabilities = data.get("capabilities")
if capabilities != {"routing": True, "open": True, "create": True}:
    raise SystemExit("Suite component manifest has unexpected capabilities")
PYMANIFEST

    grep -Fq "APP_NAME = \"${APP_NAME}\"" "$EDITOR_PRINTING" || die "Canonical source name mismatch."
    grep -Fq "APP_VERSION = \"${APP_VERSION}\"" "$SOURCE_FILE" || die "Canonical source version mismatch."
    # The extracted widgets tree is authoritative; no frozen top-level module count.
    # The staging contract below and its executable QA check enforce import closure.

    # RiqatonyPad does not declare QtPdf/QtPdfWidgets as application requirements.
    # Do not make the build depend on whether PyInstaller/Fedora happens to
    # collect their shared libraries transitively; the explicit PyInstaller
    # exclusions below are payload minimisation only, not a fatal bundle gate.
}

run_release_qa() {
    log "Running RiqatonyPad release/static/security QA"
    # Invoke nested QA through Bash so ZIP/file-manager extraction does not
    # need to preserve the helper's executable bit.
    bash "$STATIC_QA"
}

validate_desktop_entry_basic() {
    local desktop="$1"
    python3 - "$desktop" <<'PYDESKTOP'
from pathlib import Path
import sys
path = Path(sys.argv[1])
values = {}
for raw in path.read_text(encoding='utf-8').splitlines():
    line = raw.strip()
    if not line or line.startswith('#') or '=' not in line:
        continue
    key, value = line.split('=', 1)
    values[key] = value
assert '[Desktop Entry]' in path.read_text(encoding='utf-8').splitlines(), 'missing [Desktop Entry]'
assert values.get('Type') == 'Application'
assert values.get('Name') == 'RiqatonyPad'
assert values.get('Exec', '').split()[0] == 'riqatonypad'
assert values.get('Icon') == 'riqatonypad'
expected = {'text/rtf', 'application/rtf'}
actual = {item for item in values.get('MimeType', '').split(';') if item}
assert actual == expected, (actual, expected)
PYDESKTOP
}

validate_appstream_basic() {
    local metainfo="$1"
    python3 - "$metainfo" "$APP_VERSION" <<'PYXML'
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
path = Path(sys.argv[1]); version = sys.argv[2]
root = ET.parse(path).getroot()
def txt(tag):
    node = root.find(tag)
    return (node.text or '').strip() if node is not None else ''
assert txt('id') == 'io.github.brunonlinespace.riqatonypad'
assert txt('project_license') == 'GPL-3.0-or-later'
assert txt('name') == 'RiqatonyPad'
assert txt("launchable[@type='desktop-id']") == 'riqatonypad.desktop'
assert txt("url[@type='homepage']") == 'https://github.com/brunonlinespace/riqatonypad'
assert txt("url[@type='bugtracker']") == 'https://github.com/brunonlinespace/riqatonypad/issues'
dev = root.find("developer[@id='io.github.brunonlinespace']")
assert dev is not None and (dev.findtext('name') or '').strip() == 'Bruno Machado'
assert root.find("content_rating[@type='oars-1.1']") is not None
expected = {'text/rtf', 'application/rtf'}
actual = {(node.text or '').strip() for node in root.findall('./provides/mediatype')}
assert actual == expected, (actual, expected)
releases = root.findall('./releases/release')
assert len(releases) == 1 and releases[0].attrib.get('version') == version
assert releases[0].attrib.get('date'), 'current AppStream release requires date'
PYXML
}

prepare_environment() {
    log "Preparing isolated build environment"
    rm -rf "$BUILD_ROOT"
    clean_source_python_caches
    mkdir -p "$BUILD_ROOT" "$DIST_DIR" "$CACHE_DIR"
    chmod 0700 "$CACHE_DIR"
    python3 -m venv "$VENV"
    "$VENV/bin/python" -m pip install --upgrade pip wheel setuptools
    "$VENV/bin/python" -m pip install -r "$RUNTIME_REQUIREMENTS" -r "$BUILD_REQUIREMENTS"
    # Compile the *current* production module tree and QA.  The historical
    # tools/ directory does not exist in RiqatonyPad and must not be required.
    PYTHONPYCACHEPREFIX="${BUILD_ROOT}/pycache" \
        "$VENV/bin/python" -m compileall -q \
        "$SOURCE_ENTRY" "$PROGRAM_ROOT/widgets" "$PROGRAM_ROOT/qa" \
        "$SOURCE_FILE" "$EDITOR_PLATFORM_STARTUP" "$RTF_CODEC" \
        "$RICH_TEXT_SUPPORT" "$RTF_NEW_DOCUMENT"
    "$VENV/bin/python" -m pip check
    log "Running Qt-backed RTF save/round-trip QA"
    QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software \
        "$VENV/bin/python" "$QT_RTF_QA"
    log "Running Qt-backed highlight/clear regression QA"
    QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software \
        "$VENV/bin/python" "$QT_HIGHLIGHT_QA"
    log "Running Qt-backed Ribbon/Retro Find/Replace toggle regression QA"
    QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software \
        "$VENV/bin/python" "$QT_FIND_TOGGLE_QA"
    "$VENV/bin/python" -m pip freeze --all > "$PYTHON_LOCK"
}

stage_source() {
    # Stage all actual runtime .py modules; no brittle extracted-widget inventory.
    # Do not stage the qa/ tree or build artifacts into the frozen application.
    local module relative
    mkdir -p "${SOURCE_STAGE}/widgets" "${SOURCE_STAGE}/icons" \
        "${SOURCE_STAGE}/ribbon-icons" "${SOURCE_STAGE}/ribbon-icons-classic" \
        "${SOURCE_STAGE}/ribbon-icons-original" "${SOURCE_STAGE}/ribbon-icons-aero" \
        "${SOURCE_STAGE}/styles" "${SOURCE_STAGE}/templates" "${SOURCE_STAGE}/docs" \
        "${SOURCE_STAGE}/riqatony_pad/widgets"
    for module in "${PROGRAM_ROOT}"/*.py; do
        [[ -f "$module" ]] || continue
        cp -f "$module" "${SOURCE_STAGE}/"
    done
    while IFS= read -r -d '' module; do
        relative="${module#"${PROGRAM_ROOT}/"}"
        mkdir -p "${SOURCE_STAGE}/$(dirname -- "$relative")"
        cp -f "$module" "${SOURCE_STAGE}/${relative}"
    done < <(find "${PROGRAM_ROOT}/widgets" -type f -name '*.py' -print0)
    # The status-message helper is imported by its existing absolute package name.
    # Make that name available to PyInstaller without modifying application code.
    : > "${SOURCE_STAGE}/riqatony_pad/__init__.py"
    : > "${SOURCE_STAGE}/riqatony_pad/widgets/__init__.py"
    cp -f "$MESSAGE_CONVENTIONS" \
        "${SOURCE_STAGE}/riqatony_pad/widgets/message_conventions.py"
    cp -a "${ASSET_DIR}/." "${SOURCE_STAGE}/icons/"
    cp -a "${RIBBON_ICON_DIR}/light" "${SOURCE_STAGE}/ribbon-icons/light"
    cp -a "${RIBBON_ICON_DIR}/dark" "${SOURCE_STAGE}/ribbon-icons/dark"
    cp -a "${CLASSIC_RIBBON_ICON_DIR}/light" "${SOURCE_STAGE}/ribbon-icons-classic/light"
    cp -a "${CLASSIC_RIBBON_ICON_DIR}/dark" "${SOURCE_STAGE}/ribbon-icons-classic/dark"
    cp -a "${LEGACY_RIBBON_ICON_DIR}/light" "${SOURCE_STAGE}/ribbon-icons-original/light"
    cp -a "${LEGACY_RIBBON_ICON_DIR}/dark" "${SOURCE_STAGE}/ribbon-icons-original/dark"
    cp -a "${AERO_RIBBON_ICON_DIR}/light" "${SOURCE_STAGE}/ribbon-icons-aero/light"
    cp -a "${AERO_RIBBON_ICON_DIR}/dark" "${SOURCE_STAGE}/ribbon-icons-aero/dark"
    cp -a "${STYLE_DIR}/." "${SOURCE_STAGE}/styles/"
    cp -a "${TEMPLATE_DIR}/." "${SOURCE_STAGE}/templates/"
    cp -f "${DOCS_DIR}/RiqatonyPad-Documentation.rtf" \
        "${SOURCE_STAGE}/docs/RiqatonyPad-Documentation.rtf"
}

freeze_application() {
    log "Freezing RiqatonyPad with PyInstaller"
    stage_source
    "$VENV/bin/pyinstaller" \
        --noconfirm --clean --onedir --optimize 1 \
        --name "$APP_ID" --paths "$SOURCE_STAGE" \
        --hidden-import riqatony_pad.widgets.message_conventions \
        --distpath "$PYI_DIST" --workpath "$PYI_WORK" --specpath "$BUILD_ROOT" \
        --add-data "${SOURCE_STAGE}/icons:icons" \
        --add-data "${SOURCE_STAGE}/ribbon-icons:ribbon-icons" \
        --add-data "${SOURCE_STAGE}/ribbon-icons-classic:ribbon-icons-classic" \
        --add-data "${SOURCE_STAGE}/ribbon-icons-original:ribbon-icons-original" \
        --add-data "${SOURCE_STAGE}/ribbon-icons-aero:ribbon-icons-aero" \
        --add-data "${SOURCE_STAGE}/styles:styles" \
        --add-data "${SOURCE_STAGE}/templates:templates" \
        --add-data "${SOURCE_STAGE}/docs:docs" \
        --exclude-module PyQt6.QtPdf \
        --exclude-module PyQt6.QtPdfWidgets \
        --exclude-module PyQt6.QtWebEngineCore \
        --exclude-module PyQt6.QtWebEngineWidgets \
        "${SOURCE_STAGE}/app.py"
    [[ -x "${PYI_DIST}/${APP_ID}/${APP_ID}" ]] || die "PyInstaller executable was not created."
}

assemble_appdir() {
    log "Dynamically assembling AppDir"
    rm -rf "$FINAL_APPDIR"
    mkdir -p \
        "$FINAL_APPDIR/usr/lib/riqatonypad" \
        "$FINAL_APPDIR/usr/bin" \
        "$FINAL_APPDIR/usr/share/applications" \
        "$FINAL_APPDIR/usr/share/icons/hicolor" \
        "$FINAL_APPDIR/usr/share/metainfo" \
        "$FINAL_APPDIR/usr/share/riqatonypad/styles" \
        "$FINAL_APPDIR/usr/share/doc/riqatonypad"

    cp -a "${PYI_DIST}/${APP_ID}/." "$FINAL_APPDIR/usr/lib/riqatonypad/"
    ln -s ../lib/riqatonypad/riqatonypad "$FINAL_APPDIR/usr/bin/riqatonypad"
    install -m 0755 "${APPIMAGE_PAYLOAD}/AppRun" "$FINAL_APPDIR/AppRun"
    install -m 0644 "${APPIMAGE_PAYLOAD}/riqatonypad.desktop" "$FINAL_APPDIR/riqatonypad.desktop"
    install -m 0644 "${APPIMAGE_PAYLOAD}/riqatonypad.desktop" "$FINAL_APPDIR/usr/share/applications/riqatonypad.desktop"
    install -m 0644 "${APPIMAGE_PAYLOAD}/riqatonypad.png" "$FINAL_APPDIR/riqatonypad.png"
    ln -s riqatonypad.png "$FINAL_APPDIR/.DirIcon"
    cp -a "${HICOLOR_DIR}/." "$FINAL_APPDIR/usr/share/icons/hicolor/"
    install -m 0644 "${APPIMAGE_PAYLOAD}/io.github.brunonlinespace.riqatonypad.metainfo.xml" \
        "$FINAL_APPDIR/usr/share/metainfo/io.github.brunonlinespace.riqatonypad.metainfo.xml"
    install -m 0644 "${APPIMAGE_PAYLOAD}/styles/breeze-dark.qss" "$FINAL_APPDIR/usr/share/riqatonypad/styles/breeze-dark.qss"
    install -m 0644 "${APPIMAGE_PAYLOAD}/styles/breeze-light.qss" "$FINAL_APPDIR/usr/share/riqatonypad/styles/breeze-light.qss"

    for doc in RiqatonyPad-Documentation.rtf README.md CHANGELOG.md RELEASE_NOTES.md ARCHITECTURE.md \
        FORMAT_SUPPORT.md KNOWN_LIMITATIONS.md QA_TEST_PLAN.md \
        LICENSING_AND_PROVENANCE.md PORT_AUDIT.md SECURITY_REVIEW.md; do
        [[ -f "${DOCS_DIR}/${doc}" ]] && install -m 0644 "${DOCS_DIR}/${doc}" "$FINAL_APPDIR/usr/share/doc/riqatonypad/${doc}"
    done
    install -m 0644 "${PROGRAM_ROOT}/LICENSE" "$FINAL_APPDIR/usr/share/doc/riqatonypad/LICENSE"
    chmod 0755 "$FINAL_APPDIR/usr/lib/riqatonypad/riqatonypad"

    validate_desktop_entry_basic "$FINAL_APPDIR/riqatonypad.desktop"
    validate_desktop_entry_basic "$FINAL_APPDIR/usr/share/applications/riqatonypad.desktop"
    validate_appstream_basic "$FINAL_APPDIR/usr/share/metainfo/io.github.brunonlinespace.riqatonypad.metainfo.xml"
    if command -v desktop-file-validate >/dev/null 2>&1; then
        desktop-file-validate "$FINAL_APPDIR/riqatonypad.desktop"
        desktop-file-validate "$FINAL_APPDIR/usr/share/applications/riqatonypad.desktop"
    else
        printf 'Info: desktop-file-validate unavailable; built-in checks passed.\n' >&2
    fi
    if command -v appstreamcli >/dev/null 2>&1; then
        appstreamcli validate --no-net "$FINAL_APPDIR/usr/share/metainfo/io.github.brunonlinespace.riqatonypad.metainfo.xml"
    else
        printf 'Info: appstreamcli unavailable; built-in AppStream checks passed.\n' >&2
    fi
}


FORMAT_PARITY_BASELINE=""

run_format_parity_probe() {
    local label="$1"
    local theme="$2"
    shift 2
    local probe_log status actual
    rm -rf "$SMOKE_HOME"
    mkdir -p "$SMOKE_HOME/.config" "$SMOKE_HOME/.cache" "$SMOKE_HOME/.local/share" "$SMOKE_HOME/Documents"
    probe_log="$(mktemp "${TMPDIR:-/tmp}/riqatonypad-format-parity.XXXXXX.log")"
    set +e
    timeout 30s env "RIQATONYPAD_APPIMAGE_THEME=${theme}" HOME="$SMOKE_HOME" XDG_CONFIG_HOME="$SMOKE_HOME/.config" XDG_CACHE_HOME="$SMOKE_HOME/.cache" XDG_DATA_HOME="$SMOKE_HOME/.local/share" QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software "$@" --riqatonypad-format-parity-probe >"$probe_log" 2>&1
    status=$?
    set -e
    actual="$(grep '^FORMAT_PARITY ' "$probe_log" | tail -n 1 || true)"
    if [[ "$status" -ne 0 || -z "$actual" ]]; then
        cat "$probe_log" >&2
        rm -f "$probe_log"
        die "${label} formatting-parity probe failed with exit code ${status}."
    fi
    if [[ -z "$FORMAT_PARITY_BASELINE" ]]; then
        FORMAT_PARITY_BASELINE="$actual"
        log "Formatting-parity baseline: ${FORMAT_PARITY_BASELINE}"
    elif [[ "$actual" != "$FORMAT_PARITY_BASELINE" ]]; then
        printf 'Portable/source baseline: %s\n%s result: %s\n' "$FORMAT_PARITY_BASELINE" "$label" "$actual" >&2
        rm -f "$probe_log"
        die "Portable/AppImage live document formatting parity failed."
    fi
    rm -f "$probe_log"
}

run_smoke_test() {
    local label="$1"
    local theme="$2"
    local iconset="$3"
    shift 3
    local smoke_log status
    rm -rf "$SMOKE_HOME"
    mkdir -p "$SMOKE_HOME/.config" "$SMOKE_HOME/.cache" "$SMOKE_HOME/.local/share" "$SMOKE_HOME/Documents"
    smoke_log="$(mktemp "${TMPDIR:-/tmp}/riqatonypad-smoke.XXXXXX.log")"
    log "Running ${label} off-screen GUI smoke test"
    set +e
    timeout 30s env \
        "RIQATONYPAD_APPIMAGE_THEME=${theme}" \
        "RIQATONYPAD_APPIMAGE_ICONSET=${iconset}" \
        HOME="$SMOKE_HOME" \
        XDG_CONFIG_HOME="$SMOKE_HOME/.config" \
        XDG_CACHE_HOME="$SMOKE_HOME/.cache" \
        XDG_DATA_HOME="$SMOKE_HOME/.local/share" \
        QT_QPA_PLATFORM=offscreen \
        QT_QUICK_BACKEND=software \
        "$@" --riqatonypad-smoke-test >"$smoke_log" 2>&1
    status=$?
    set -e
    if [[ "$status" -ne 0 ]] || ! grep -Fq 'GUI smoke test passed.' "$smoke_log"; then
        cat "$smoke_log" >&2
        rm -f "$smoke_log"
        die "${label} GUI smoke test failed with exit code ${status}."
    fi
    rm -f "$smoke_log"
}

run_version_smoke_test() {
    local label="$1"
    local theme="$2"
    shift 2
    local smoke_log expected status
    expected="${APP_NAME} ${APP_VERSION}"
    smoke_log="$(mktemp "${TMPDIR:-/tmp}/riqatonypad-version.XXXXXX.log")"
    log "Running ${label} version smoke test"
    set +e
    timeout 30s env "RIQATONYPAD_APPIMAGE_THEME=${theme}" QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software \
        "$@" --version >"$smoke_log" 2>&1
    status=$?
    set -e
    if [[ "$status" -ne 0 ]] || ! grep -Fxq "$expected" "$smoke_log"; then
        cat "$smoke_log" >&2
        rm -f "$smoke_log"
        die "${label} version smoke test failed with exit code ${status}."
    fi
    rm -f "$smoke_log"
}

run_theme_smoke_matrix() {
    local label="$1"; shift
    local theme iconset
    for theme in system dark light; do
        for iconset in new classic original aero; do
            run_smoke_test "${label} ${theme}-theme ${iconset}-icons" "$theme" "$iconset" "$@"
        done
    done
}

run_version_smoke_matrix() {
    local label="$1"; shift
    local theme
    for theme in system dark light; do
        run_version_smoke_test "${label} ${theme}-theme" "$theme" "$@"
    done
}

extract_final_appimage() {
    local extract_log status
    rm -rf "$FINAL_EXTRACT_ROOT"
    mkdir -p "$FINAL_EXTRACT_ROOT"
    extract_log="$(mktemp "${TMPDIR:-/tmp}/riqatonypad-appimage-extract.XXXXXX.log")"
    log "Extracting completed AppImage for final-artifact QA"
    set +e
    (
        cd "$FINAL_EXTRACT_ROOT"
        "$APPIMAGE" --appimage-extract >"$extract_log" 2>&1
    )
    status=$?
    set -e
    if [[ "$status" -ne 0 ]]; then
        cat "$extract_log" >&2
        rm -f "$extract_log"
        die "Completed AppImage extraction failed with exit code ${status}."
    fi
    rm -f "$extract_log"
    [[ -x "$FINAL_EXTRACT_APPDIR/AppRun" ]] \
        || die "Completed AppImage did not extract an executable squashfs-root/AppRun."
    [[ -x "$FINAL_EXTRACT_APPDIR/usr/bin/riqatonypad" ]] \
        || die "Completed AppImage did not contain the RiqatonyPad launcher."
}

validate_bundle() {
    log "Validating Qt bundle"
    find "$FINAL_APPDIR/usr/lib/riqatonypad" -name 'libqxcb.so' -print -quit | grep -q . \
        || die "Qt XCB platform plugin was not bundled."
    find "$FINAL_APPDIR/usr/lib/riqatonypad" \
        \( -name 'libqwayland*.so' -o -name '*wayland*.so' \) -print -quit | grep -q . \
        || printf 'Warning: Qt Wayland plugin was not detected; test XWayland carefully.\n' >&2
    find "$FINAL_APPDIR/usr/lib/riqatonypad" \
        \( -name '*Qt6PrintSupport*' -o -name '*QtPrintSupport*' \) -print -quit | grep -q . \
        || die "Qt Print Support was not bundled."
    # Do not fail on QtPdf/QtPdfWidgets payload files. PyInstaller can collect
    # Qt libraries transitively on Fedora even when the Python modules are
    # excluded and RiqatonyPad never imports them. Their presence or absence is not
    # a RiqatonyPad build requirement.
    if find "$FINAL_APPDIR/usr/lib/riqatonypad" -iname '*WebEngine*' -print -quit | grep -q .; then
        die "Qt WebEngine was bundled unexpectedly; RiqatonyPad does not require it."
    fi
    rm -rf "$SMOKE_HOME"
    mkdir -p "$SMOKE_HOME/.config" "$SMOKE_HOME/.cache" "$SMOKE_HOME/.local/share" "$SMOKE_HOME/Documents"
    FORMAT_PARITY_BASELINE=""
    for parity_theme in system dark light; do
        run_format_parity_probe "portable/source ${parity_theme}-theme" "$parity_theme" "$VENV/bin/python" "$SOURCE_STAGE/app.py"
    done
    run_theme_smoke_matrix "AppDir" "$FINAL_APPDIR/AppRun"
    for parity_theme in system dark light; do
        run_format_parity_probe "AppDir ${parity_theme}-theme" "$parity_theme" "$FINAL_APPDIR/AppRun"
    done
    run_version_smoke_matrix "AppDir" "$FINAL_APPDIR/AppRun"
}

elf_sanity_check() {
    local tool="$1" magic size
    require_file "$tool"
    size="$(stat -c %s "$tool")"
    [[ "$size" -gt 0 && "$size" -le "$MAX_TOOL_BYTES" ]] \
        || die "appimagetool invalid size: ${size} bytes."
    magic="$(od -An -tx1 -N4 "$tool" | tr -d ' \n')"
    [[ "$magic" == "7f454c46" ]] || die "appimagetool is not an ELF executable: $tool"
}

download_tool() {
    local url="$1"
    local destination="$2"
    local part="${destination}.part"
    [[ "$url" == https://* ]] || die "appimagetool URL must use HTTPS."
    rm -f "$part"
    if command -v curl >/dev/null 2>&1; then
        curl --proto '=https' --tlsv1.2 --fail --location --retry 3 --retry-all-errors \
            --connect-timeout 30 --max-time 300 --max-filesize "$MAX_TOOL_BYTES" \
            --output "$part" "$url"
    else
        wget --https-only --tries=3 --timeout=30 --output-document="$part" "$url"
    fi
    [[ -f "$part" ]] || die "appimagetool download produced no file."
    elf_sanity_check "$part"
    chmod 0755 "$part"
    mv -f "$part" "$destination"
}

prepare_appimagetool() {
    local tool url
    mkdir -p "$CACHE_DIR"
    chmod 0700 "$CACHE_DIR"
    if [[ -n "${APPIMAGETOOL_PATH:-}" ]]; then
        tool="$(readlink -f -- "$APPIMAGETOOL_PATH")"
        [[ -x "$tool" ]] || die "APPIMAGETOOL_PATH is not executable: $tool"
        log "Using appimagetool supplied through APPIMAGETOOL_PATH"
    else
        tool="${CACHE_DIR}/appimagetool-${ARCH}.AppImage"
        url="${APPIMAGETOOL_URL:-https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-${ARCH}.AppImage}"
        if [[ ! -x "$tool" ]]; then
            log "Downloading official appimagetool"
            download_tool "$url" "$tool"
        else
            log "Using cached appimagetool"
        fi
    fi
    elf_sanity_check "$tool"
    if [[ -n "${APPIMAGETOOL_SHA256:-}" ]]; then
        [[ "$APPIMAGETOOL_SHA256" =~ ^[[:xdigit:]]{64}$ ]] \
            || die "APPIMAGETOOL_SHA256 must be 64 hexadecimal characters."
        printf '%s  %s\n' "$APPIMAGETOOL_SHA256" "$tool" | sha256sum --check --status \
            || die "appimagetool SHA-256 verification failed."
    elif [[ "${RIQATONYPAD_RELEASE_BUILD:-0}" == "1" ]]; then
        die "RIQATONYPAD_RELEASE_BUILD=1 requires APPIMAGETOOL_SHA256."
    else
        printf 'Warning: APPIMAGETOOL_SHA256 not supplied; resolved hash will be recorded.\n' >&2
    fi
    APPIMAGETOOL_RESOLVED="$tool"
}

build_appimage() {
    prepare_appimagetool
    log "Creating ${APPIMAGE##*/}"
    rm -f "$APPIMAGE" "$SHA_FILE"
    ARCH="$ARCH" VERSION="$APP_VERSION" \
        "$APPIMAGETOOL_RESOLVED" --appimage-extract-and-run "$FINAL_APPDIR" "$APPIMAGE"
    [[ -s "$APPIMAGE" ]] || die "appimagetool did not create expected output."
    chmod 0755 "$APPIMAGE"
    # Validate the actual completed artifact without routing RiqatonyPad arguments
    # through the AppImage runtime. Extraction is FUSE-independent and proves
    # that the finished AppImage/runtime can expose its embedded payload; the
    # extracted AppRun is then tested under the same theme matrix as AppDir.
    extract_final_appimage
    run_theme_smoke_matrix "final AppImage extracted payload" "$FINAL_EXTRACT_APPDIR/AppRun"
    # Formatting-parity checks are run below using the same portable/source baseline.
    for parity_theme in system dark light; do
        run_format_parity_probe "final AppImage extracted ${parity_theme}-theme" "$parity_theme" "$FINAL_EXTRACT_APPDIR/AppRun"
    done
    run_version_smoke_matrix "final AppImage extracted payload" "$FINAL_EXTRACT_APPDIR/AppRun"
    (cd "$DIST_DIR" && sha256sum "${APPIMAGE##*/}" > "${SHA_FILE##*/}")
}

write_build_info() {
    {
        echo "RiqatonyPad AppImage build"
        echo "Version: ${APP_VERSION}"
        echo "Architecture: ${ARCH}"
        echo "Release mode: ${RIQATONYPAD_RELEASE_BUILD:-0}"
        echo "Built: $(date --iso-8601=seconds)"
        echo "Host: ${HOST_NAME}"
        echo "Fedora release: ${FEDORA_RELEASE}"
        echo "Privilege policy: non-privileged; no sudo/dnf/su/pkexec"
        echo "System Python: $(python3 --version 2>&1)"
        echo "Build Python: $("$VENV/bin/python" --version 2>&1)"
        echo "PyInstaller: $("$VENV/bin/pyinstaller" --version)"
        "$VENV/bin/python" - <<'PYVERS'
from PyQt6.QtCore import PYQT_VERSION_STR, QT_VERSION_STR
print(f"PyQt6: {PYQT_VERSION_STR}")
print(f"Qt: {QT_VERSION_STR}")
PYVERS
        echo "main.py SHA-256: $(sha256sum "$SOURCE_ENTRY" | awk '{print $1}')"
        echo "Suite component manifest SHA-256: $(sha256sum "$COMPONENT_MANIFEST" | awk '{print $1}')"
        echo "RiqatonyPad source SHA-256: $(sha256sum "$SOURCE_FILE" | awk '{print $1}')"
        echo "RTF codec SHA-256: $(sha256sum "$RTF_CODEC" | awk '{print $1}')"
        echo "Rich-text support SHA-256: $(sha256sum "$RICH_TEXT_SUPPORT" | awk '{print $1}')"
        echo "SOURCE_MANIFEST.sha256 SHA-256: $(sha256sum "$SOURCE_MANIFEST" | awk '{print $1}')"
        echo "Runtime requirements SHA-256: $(sha256sum "$RUNTIME_REQUIREMENTS" | awk '{print $1}')"
        echo "Build requirements SHA-256: $(sha256sum "$BUILD_REQUIREMENTS" | awk '{print $1}')"
        echo "Builder SHA-256: $(sha256sum "$0" | awk '{print $1}')"
        echo "appimagetool: ${APPIMAGETOOL_RESOLVED}"
        echo "appimagetool SHA-256: $(sha256sum "$APPIMAGETOOL_RESOLVED" | awk '{print $1}')"
        echo "Output: ${APPIMAGE##*/}"
        echo "Output SHA-256: $(sha256sum "$APPIMAGE" | awk '{print $1}')"
        echo "QtPdf/QtPdfWidgets: not application requirements; transitive payload presence is tolerated"
        echo "RTF fidelity: Qt-backed save/round-trip QA PASS"
        echo "Smoke tests: portable/source format parity PASS (system/dark/light); AppDir GUI+version+format parity PASS (system/dark/light x Harmony/Humility/Heritage/Halcyon icons); completed AppImage extraction PASS; final extracted payload GUI+version+format parity PASS"
        echo "Source cleanliness: __pycache__/pyc/pyo removed before QA/build and at exit"
    } > "$BUILD_INFO"
}

main() {
    check_non_privileged_policy
    check_host_prerequisites
    check_inputs
    clean_source_python_caches
    run_release_qa
    clean_source_python_caches
    prepare_environment
    freeze_application
    assemble_appdir
    validate_bundle
    build_appimage
    write_build_info
    clean_source_python_caches
    log "Build complete"
    printf 'AppImage: %s\nChecksum: %s\nBuild information: %s\nPython lock: %s\n' \
        "$APPIMAGE" "$SHA_FILE" "$BUILD_INFO" "$PYTHON_LOCK"
}

main "$@"
