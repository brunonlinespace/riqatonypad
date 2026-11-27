# RiqatonyPad 2 Windows portable build

This folder contains the PowerShell builder for the self-contained **RiqatonyPad Windows x64 portable package**.

The builder uses the project-root `main.py`, canonical `riqatony_pad/app.py`, current runtime modules, RiqatonyPad assets, bundled RTF documentation, and Windows version metadata from this source tree.

## Requirements

Build on **Windows x64** with:

- Python 3 available from PowerShell;
- internet access when the isolated build environment needs to install Python build dependencies;
- PowerShell permission to run the build script.

The builder does not install RiqatonyPad system-wide.

## Running the builder

### From the repository root

Open PowerShell in the repository root.

If PowerShell blocks local scripts, allow scripts for the **current PowerShell process only**:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
```

Then run:

```powershell
.\riqatony_pad\packaging\windows\build-windows-portable.ps1
```

### From `riqatony_pad\packaging\windows`

If PowerShell is already open in the Windows packaging folder:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\build-windows-portable.ps1
```

If the current PowerShell execution policy already allows the script to run, the `Set-ExecutionPolicy` command is not required.

## What the builder does

The builder:

1. confirms that it is running on Windows;
2. checks the required source modules, icon families, styles, documentation, requirements, and Windows version-information file;
3. verifies that the canonical RiqatonyPad source reports the expected application version;
4. creates a clean isolated Python virtual environment under `riqatony_pad\packaging\windows\build`;
5. updates `pip`, `wheel`, and `setuptools` inside that environment;
6. installs the RiqatonyPad runtime and Windows/PyInstaller build requirements;
7. runs `pip check` and Python syntax validation;
8. runs the Qt-backed RTF save/round-trip QA in the isolated environment;
9. records the complete Python environment with `pip freeze --all`;
10. stages the current modular RiqatonyPad runtime and all four command-icon families, including Halcyon;
11. builds the Windows application with PyInstaller in `--windowed --onedir` mode;
12. assembles the flat portable package with lowercase `riqatonypad.exe`, `_internal\`, and the master `README.md`;
13. keeps the bundled RTF documentation inside the frozen runtime rather than exposing a visible root-level `docs\` folder;
14. runs a deterministic GUI smoke test unless explicitly skipped;
15. creates the portable ZIP, SHA-256 checksum, build-information record, and Python-lock record;
16. removes the temporary `build` workspace only after all build outputs and records have been created successfully.

If the build fails before completion, the temporary build workspace is left in place for diagnosis.

## Build options

### Skip the GUI smoke test

The normal build includes a launch test of the frozen executable. To skip it deliberately:

```powershell
.\riqatony_pad\packaging\windows\build-windows-portable.ps1 -SkipSmokeTest
```

### Use a different Python command

The builder uses `python` by default. To select another Python command:

```powershell
.\riqatony_pad\packaging\windows\build-windows-portable.ps1 -PythonCommand py
```

or, for example:

```powershell
.\riqatony_pad\packaging\windows\build-windows-portable.ps1 -PythonCommand python3
```

The selected command must be able to create the isolated virtual environment.

## Outputs

Successful builds are written under:

```text
riqatony_pad\dist\
```

For RiqatonyPad 2.1.2, the expected outputs are:

```text
RiqatonyPad-2.1.2-Windows-x64-portable\
RiqatonyPad-2.1.2-Windows-x64-portable.zip
RiqatonyPad-2.1.2-Windows-x64-portable.zip.sha256
RiqatonyPad-2.1.2-Windows-x64.build-info.txt
RiqatonyPad-2.1.2-Windows-x64.build-python-lock.txt
```

The visible portable-folder root contains:

```text
RiqatonyPad-2.1.2-Windows-x64-portable\
├── _internal\
├── riqatonypad.exe
└── README.md
```

There is no extra nested RiqatonyPad application folder and no visible root-level `docs\` directory.

## What the builder does not do

The Windows builder does **not**:

- install RiqatonyPad into Windows;
- create file associations;
- create or modify RiqatonyPad registry entries;
- require a system-wide PyInstaller installation;
- reuse the host Python environment for the packaged application.

Build dependencies live only in the isolated build workspace. That workspace is removed after a successful build and retained when a build fails.

## Troubleshooting

### PowerShell says running scripts is disabled

Run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
```

and then run the builder again in the same PowerShell window.

### `python` is not found

Confirm that Python is installed and available from PowerShell:

```powershell
python --version
```

If your Windows Python installation uses another command, pass it with `-PythonCommand`.

### The GUI smoke test fails

Do not treat a failed smoke test as a successful release build. Review the error first. `-SkipSmokeTest` is intended only for deliberate diagnostic or packaging work; the normal release build is expected to pass its smoke test.

## Packaging model

The Windows release is a **portable folder plus ZIP**. Users extract the ZIP and run `riqatonypad.exe` directly.

The portable root deliberately exposes only the executable, PyInstaller's `_internal\` directory, and the master `README.md`; supporting runtime assets and the bundled RTF documentation remain internal.

No installer is produced by this builder.
