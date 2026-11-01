param(
    [switch]$SkipSmokeTest,
    [string]$PythonCommand = "python"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$AppName = "RiqatonyPad"
$Version = "2.0.0"
$Architecture = "x64"

if ([System.Environment]::OSVersion.Platform -ne [System.PlatformID]::Win32NT) {
    throw "This build script must be run on Windows."
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = (Resolve-Path (Join-Path $ScriptDir "..\..")).Path
$SourceFile = Join-Path $Root "app.py"
$EditorWidgets = Join-Path $Root "widgets/rwpyn/editor_widgets.py"
$EditorFormatting = Join-Path $Root "widgets/rwpyn/editor_formatting.py"
$EditorInsertion = Join-Path $Root "widgets/rwpyn/editor_insertion.py"
$EditorSearchView = Join-Path $Root "widgets/rwpyn/editor_search_view.py"
$EditorPrinting = Join-Path $Root "widgets/rwpyn/editor_printing.py"
$EditorPreferences = Join-Path $Root "widgets/rwpyn/editor_preferences.py"
$EditorRibbonRetro = Join-Path $Root "widgets/editor_ribbon_retro.py"
$EditorCommandsAppearance = Join-Path $Root "widgets/editor_commands_appearance.py"
$EditorPlatformStartup = Join-Path $Root "editor_platform_startup.py"
$EditorLifecycle = Join-Path $Root "widgets/rwpyn/editor_lifecycle.py"
$RtfCodec = Join-Path $Root "rtf_codec.py"
$RichTextSupport = Join-Path $Root "rich_text_support.py"
$RtfNewDocument = Join-Path $Root "rtf_new_document.py"
$ShortcutSearch = Join-Path $Root "widgets/keyboard_shortcuts.py"
$AboutDialog = Join-Path $Root "widgets/about_dialog.py"
$QuickTour = Join-Path $Root "widgets/quick_tour.py"
$IconDir = Join-Path $Root "assets\icons"
$RibbonIconDir = Join-Path $Root "assets\ribbon-icons"
$ClassicRibbonIconDir = Join-Path $Root "assets\ribbon-icons-classic"
$LegacyRibbonIconDir = Join-Path $Root "assets\ribbon-icons-original"
$StyleDir = Join-Path $Root "assets\styles"
$TemplateDir = Join-Path $Root "assets\templates"
$DocsDir = Join-Path $Root "docs"
$IconFile = Join-Path $IconDir "riqatonypad.ico"
$AboutImage = Join-Path $IconDir "riqatonypad-about.png"
$Requirements = Join-Path $ScriptDir "build-requirements.txt"
$VersionInfo = Join-Path $ScriptDir "windows-version-info.txt"
$QtRtfQa = Join-Path $Root "qa\qt-rtf-qa.py"

$BuildRoot = Join-Path $ScriptDir "build"
$Venv = Join-Path $BuildRoot "venv"
$VenvPython = Join-Path $Venv "Scripts\python.exe"
$PyInstaller = Join-Path $Venv "Scripts\pyinstaller.exe"
$Stage = Join-Path $BuildRoot "source-stage"
$PyInstallerDist = Join-Path $BuildRoot "pyinstaller-dist"
$PyInstallerWork = Join-Path $BuildRoot "pyinstaller-work"
$Dist = Join-Path $Root "dist"
$PackageName = "$AppName-$Version-Windows-$Architecture-portable"
$PackageDir = Join-Path $Dist $PackageName
$ZipFile = Join-Path $Dist "$PackageName.zip"
$ChecksumFile = "$ZipFile.sha256"
$BuildInfo = Join-Path $Dist "$AppName-$Version-Windows-$Architecture.build-info.txt"
$PythonLock = Join-Path $Dist "$AppName-$Version-Windows-$Architecture.build-python-lock.txt"

function Write-Step([string]$Message) {
    Write-Host ""
    Write-Host "==> $Message"
}

function Assert-File([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Missing required file: $Path"
    }
}

Assert-File $SourceFile
Assert-File $EditorWidgets
Assert-File $RtfCodec
Assert-File $RichTextSupport
Assert-File $RtfNewDocument
Assert-File $ShortcutSearch
Assert-File $IconFile
Assert-File $AboutImage
Assert-File (Join-Path $RibbonIconDir "light\superscript.png")
Assert-File (Join-Path $RibbonIconDir "dark\superscript.png")
Assert-File (Join-Path $RibbonIconDir "light\subscript.png")
Assert-File (Join-Path $RibbonIconDir "dark\subscript.png")
Assert-File (Join-Path $ClassicRibbonIconDir "light\subscript.png")
Assert-File (Join-Path $LegacyRibbonIconDir "light\subscript.png")
Assert-File $Requirements
Assert-File $VersionInfo
Assert-File (Join-Path $StyleDir "breeze-dark.qss")
Assert-File (Join-Path $StyleDir "breeze-light.qss")
Assert-File (Join-Path $TemplateDir "default-document.rtf")
Assert-File (Join-Path $DocsDir "RiqatonyPad-Documentation.rtf")
Assert-File $QtRtfQa

$SourceText = Get-Content -LiteralPath $SourceFile -Raw
$ExpectedVersionPattern = (
    'APP_VERSION\s*=\s*"' +
    [regex]::Escape($Version) +
    '"'
)
if ($SourceText -notmatch $ExpectedVersionPattern) {
    $DetectedVersionLine = (
        $SourceText -split "\r?\n" |
        Where-Object { $_ -match '^\s*APP_VERSION\s*=' } |
        Select-Object -First 1
    )
    throw (
        "Canonical source version mismatch. " +
        "Expected $Version. Found: $DetectedVersionLine"
    )
}

$ApplicationPythonFiles = @(
    Get-ChildItem -LiteralPath $Root -File -Filter *.py
)
if ($ApplicationPythonFiles.Count -ne 7) {
    throw "Expected the seven RiqatonyPad runtime Python modules in the RiqatonyPad program directory."
}

Write-Step "Preparing isolated Python environment"
if (Test-Path -LiteralPath $BuildRoot) {
    Remove-Item -LiteralPath $BuildRoot -Recurse -Force
}
New-Item -ItemType Directory -Path $BuildRoot, $Stage, $Dist -Force | Out-Null

& $PythonCommand -m venv $Venv
if ($LASTEXITCODE -ne 0) {
    throw "Could not create the Python virtual environment."
}

& $VenvPython -m pip install --upgrade pip wheel setuptools
if ($LASTEXITCODE -ne 0) {
    throw "Could not update the Python build tools."
}

& $VenvPython -m pip install -r $Requirements
if ($LASTEXITCODE -ne 0) {
    throw "Could not install the Windows build requirements."
}

& $VenvPython -m py_compile $SourceFile $EditorWidgets $EditorFormatting $EditorInsertion $EditorSearchView $RtfCodec $RichTextSupport $RtfNewDocument $ShortcutSearch $EditorPlatformStartup
if ($LASTEXITCODE -ne 0) {
    throw "The canonical source failed Python syntax validation."
}

& $VenvPython -m pip check
if ($LASTEXITCODE -ne 0) {
    throw "The isolated Windows build environment has dependency conflicts."
}

Write-Step "Running Qt-backed RTF save/round-trip QA"
$env:QT_QPA_PLATFORM = "offscreen"
& $VenvPython $QtRtfQa
if ($LASTEXITCODE -ne 0) {
    throw "The Qt-backed RTF save/round-trip QA failed."
}
Remove-Item Env:QT_QPA_PLATFORM -ErrorAction SilentlyContinue

& $VenvPython -m pip freeze --all |
    Set-Content -LiteralPath $PythonLock -Encoding UTF8

Write-Step "Staging the canonical source and shared assets"
New-Item -ItemType Directory -Path (Join-Path $Stage "widgets\rwpyn") -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $Root "widgets\__init__.py") -Destination (Join-Path $Stage "widgets\__init__.py")
Copy-Item -LiteralPath (Join-Path $Root "widgets\rwpyn\__init__.py") -Destination (Join-Path $Stage "widgets\rwpyn\__init__.py")
Copy-Item -LiteralPath $SourceFile -Destination (Join-Path $Stage "app.py")
Copy-Item -LiteralPath $EditorWidgets -Destination (Join-Path $Stage "widgets/rwpyn/editor_widgets.py")
Copy-Item -LiteralPath $EditorFormatting -Destination (Join-Path $Stage "widgets/rwpyn/editor_formatting.py")
Copy-Item -LiteralPath $EditorInsertion -Destination (Join-Path $Stage "widgets/rwpyn/editor_insertion.py")
Copy-Item -LiteralPath $EditorSearchView -Destination (Join-Path $Stage "widgets/rwpyn/editor_search_view.py")
Copy-Item -LiteralPath $EditorPrinting -Destination (Join-Path $Stage "widgets/rwpyn/editor_printing.py")
Copy-Item -LiteralPath $EditorPreferences -Destination (Join-Path $Stage "widgets/rwpyn/editor_preferences.py")
Copy-Item -LiteralPath $EditorRibbonRetro -Destination (Join-Path $Stage "widgets/editor_ribbon_retro.py")
Copy-Item -LiteralPath $EditorCommandsAppearance -Destination (Join-Path $Stage "widgets/editor_commands_appearance.py")
Copy-Item -LiteralPath $EditorPlatformStartup -Destination (Join-Path $Stage "editor_platform_startup.py")
Copy-Item -LiteralPath $EditorLifecycle -Destination (Join-Path $Stage "widgets/rwpyn/editor_lifecycle.py")
Copy-Item -LiteralPath $RtfCodec -Destination (Join-Path $Stage "rtf_codec.py")
Copy-Item -LiteralPath $RichTextSupport -Destination (Join-Path $Stage "rich_text_support.py")
Copy-Item -LiteralPath $RtfNewDocument -Destination (Join-Path $Stage "rtf_new_document.py")
Copy-Item -LiteralPath $ShortcutSearch -Destination (Join-Path $Stage "widgets/keyboard_shortcuts.py")
Copy-Item -LiteralPath $AboutDialog -Destination (Join-Path $Stage "widgets/about_dialog.py")
Copy-Item -LiteralPath $QuickTour -Destination (Join-Path $Stage "widgets/quick_tour.py")
Copy-Item -LiteralPath $IconDir -Destination (Join-Path $Stage "icons") -Recurse
Copy-Item -LiteralPath $RibbonIconDir -Destination (Join-Path $Stage "ribbon-icons") -Recurse
Copy-Item -LiteralPath $ClassicRibbonIconDir -Destination (Join-Path $Stage "ribbon-icons-classic") -Recurse
Copy-Item -LiteralPath $LegacyRibbonIconDir -Destination (Join-Path $Stage "ribbon-icons-original") -Recurse
Copy-Item -LiteralPath $StyleDir -Destination (Join-Path $Stage "styles") -Recurse
Copy-Item -LiteralPath $TemplateDir -Destination (Join-Path $Stage "templates") -Recurse
New-Item -ItemType Directory -Force -Path (Join-Path $Stage "docs") | Out-Null
Copy-Item -LiteralPath (Join-Path $DocsDir "RiqatonyPad-Documentation.rtf") -Destination (Join-Path $Stage "docs\RiqatonyPad-Documentation.rtf")

Write-Step "Building the Windows portable application"
$PyInstallerArguments = @(
    "--noconfirm",
    "--clean",
    "--windowed",
    "--onedir",
    "--optimize", "1",
    "--name", $AppName,
    "--icon", $IconFile,
    "--version-file", $VersionInfo,
    "--distpath", $PyInstallerDist,
    "--workpath", $PyInstallerWork,
    "--specpath", $BuildRoot,
    "--add-data", "$Stage\icons;icons",
    "--add-data", "$Stage\ribbon-icons;ribbon-icons",
    "--add-data", "$Stage\ribbon-icons-classic;ribbon-icons-classic",
    "--add-data", "$Stage\ribbon-icons-original;ribbon-icons-original",
    "--add-data", "$Stage\styles;styles",
    "--add-data", "$Stage\templates;templates",
    "--add-data", "$Stage\docs;docs",
    "--exclude-module", "PyQt6.QtPdf",
    "--exclude-module", "PyQt6.QtPdfWidgets",
    "--exclude-module", "PyQt6.QtWebEngineCore",
    "--exclude-module", "PyQt6.QtWebEngineWidgets",
    (Join-Path $Stage "app.py")
)
& $PyInstaller @PyInstallerArguments
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed."
}

Write-Step "Assembling the portable Windows package"
if (Test-Path -LiteralPath $PackageDir) {
    Remove-Item -LiteralPath $PackageDir -Recurse -Force
}
New-Item -ItemType Directory -Path $PackageDir | Out-Null
Copy-Item -Path (Join-Path $PyInstallerDist "$AppName\*") `
    -Destination $PackageDir -Recurse -Force

$PackageDocs = Join-Path $PackageDir "docs"
New-Item -ItemType Directory -Path $PackageDocs -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $Root "LICENSE") `
    -Destination (Join-Path $PackageDocs "LICENSE")
$DocumentationFiles = @(
    "RiqatonyPad-Documentation.rtf",
    "README.md",
    "ARCHITECTURE.md",
    "FEATURE_MATRIX.md",
    "FORMAT_SUPPORT.md",
    "KNOWN_LIMITATIONS.md",
    "QA_TEST_PLAN.md",
    "LICENSING_AND_PROVENANCE.md",
    "PORT_AUDIT.md",
    "CHANGELOG.md",
    "RELEASE_NOTES.md",
    "SECURITY_REVIEW.md"
)
foreach ($DocumentationFile in $DocumentationFiles) {
    Copy-Item -LiteralPath (Join-Path $Root "docs\$DocumentationFile") `
        -Destination (Join-Path $PackageDocs $DocumentationFile)
}

if (-not $SkipSmokeTest) {
    Write-Step "Running deterministic Windows smoke test"
    $Executable = Join-Path $PackageDir "$AppName.exe"
    $SmokeRoot = Join-Path $BuildRoot "smoke-profile"
    if (Test-Path -LiteralPath $SmokeRoot) {
        Remove-Item -LiteralPath $SmokeRoot -Recurse -Force
    }
    New-Item -ItemType Directory -Path $SmokeRoot -Force | Out-Null

    $OldAppData = $env:APPDATA
    $OldLocalAppData = $env:LOCALAPPDATA
    $OldQtPlatform = $env:QT_QPA_PLATFORM
    try {
        $env:APPDATA = Join-Path $SmokeRoot "Roaming"
        $env:LOCALAPPDATA = Join-Path $SmokeRoot "Local"
        $env:QT_QPA_PLATFORM = "offscreen"
        New-Item -ItemType Directory -Path $env:APPDATA, $env:LOCALAPPDATA -Force | Out-Null
        $Process = Start-Process -FilePath $Executable `
            -ArgumentList "--riqatonypad-smoke-test" -PassThru -Wait
        if ($Process.ExitCode -ne 0) {
            throw "$AppName smoke test failed with code $($Process.ExitCode)."
        }
    }
    finally {
        $env:APPDATA = $OldAppData
        $env:LOCALAPPDATA = $OldLocalAppData
        $env:QT_QPA_PLATFORM = $OldQtPlatform
        Remove-Item -LiteralPath $SmokeRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Step "Creating the portable ZIP and build records"
if (Test-Path -LiteralPath $ZipFile) {
    Remove-Item -LiteralPath $ZipFile -Force
}
Compress-Archive -LiteralPath $PackageDir -DestinationPath $ZipFile `
    -CompressionLevel Optimal

$Hash = (Get-FileHash -LiteralPath $ZipFile -Algorithm SHA256).Hash.ToLowerInvariant()
"$Hash  $(Split-Path -Leaf $ZipFile)" |
    Set-Content -LiteralPath $ChecksumFile -Encoding ASCII

$PythonVersion = (& $VenvPython --version 2>&1 | Out-String).Trim()
if ($LASTEXITCODE -ne 0) {
    throw "Could not read the build Python version."
}

$PyInstallerVersion = (& $PyInstaller --version 2>&1 | Out-String).Trim()
if ($LASTEXITCODE -ne 0) {
    throw "Could not read the PyInstaller version."
}

$QtVersions = (& $VenvPython -c `
    "from PyQt6.QtCore import PYQT_VERSION_STR, QT_VERSION_STR; print('PyQt6:', PYQT_VERSION_STR); print('Qt:', QT_VERSION_STR)" `
    2>&1 | Out-String).Trim()
if ($LASTEXITCODE -ne 0) {
    throw "Could not read the PyQt6 and Qt versions."
}

$SourceHash = (Get-FileHash -LiteralPath $SourceFile -Algorithm SHA256).Hash.ToLowerInvariant()
$CodecHash = (Get-FileHash -LiteralPath $RtfCodec -Algorithm SHA256).Hash.ToLowerInvariant()
$RichSupportHash = (Get-FileHash -LiteralPath $RichTextSupport -Algorithm SHA256).Hash.ToLowerInvariant()
$SourceEditorHash = (Get-FileHash -LiteralPath $SourceEditor -Algorithm SHA256).Hash.ToLowerInvariant()

@"
RiqatonyPad Windows build
Version: $Version
Architecture: $Architecture
Built: $(Get-Date -Format o)
Host: $([System.Environment]::OSVersion.VersionString)
Python: $PythonVersion
PyInstaller: $PyInstallerVersion
$QtVersions
RiqatonyPad source SHA-256: $SourceHash
RTF codec SHA-256: $CodecHash
Rich-text support SHA-256: $RichSupportHash
Source editor SHA-256: $SourceEditorHash
Output: $(Split-Path -Leaf $ZipFile)
Output SHA-256: $Hash
"@ | Set-Content -LiteralPath $BuildInfo -Encoding UTF8

Write-Step "Build complete"
Write-Host $PackageDir
Write-Host $ZipFile
Write-Host $ChecksumFile
Write-Host $BuildInfo
Write-Host $PythonLock
