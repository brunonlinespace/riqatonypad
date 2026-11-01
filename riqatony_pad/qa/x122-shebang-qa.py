#!/usr/bin/env python3
"""x12.2 bounded Python source-header convergence: no code, layout, mode changes."""
from pathlib import Path
from shortcut_legacy import legacy_read_bytes
import hashlib, ast, stat
ROOT = Path(__file__).resolve().parents[1]
OUTER = ROOT.parent
HEAD = b"#!/usr/bin/env python3\n"
VERSION = '2.0.0-x13.0'
PRIOR = '2.0.0-x12.1'
EXPECTED = {'widgets/rwpyn/editor_widgets.py': '4950f1371e7917dde27caafa40d25942773518eb1f08c719e3415638c7276d18', 'rtf_new_document.py': '539058c822ebb5e5360b6b03f610b3ef9fc8d8196a662e402815622a05f32a41', 'widgets/shortcut_search.py': 'c9ea5e80ffca4f5523873c5b9035e17cf802f83f0b78fa611ff0ca66d1b63310'}
assert len(EXPECTED) == 3
for name, digest in EXPECTED.items():
    path=ROOT/('widgets/keyboard_shortcuts.py' if name=='widgets/shortcut_search.py' else name)
    content=legacy_read_bytes(ROOT,name)
    assert content.startswith(HEAD), f"missing canonical shebang: {name}"
    assert hashlib.sha256(content[len(HEAD):]).hexdigest()==digest, f"non-shebang change: {name}"
    assert not (path.stat().st_mode & stat.S_IXUSR), f"import-only file became executable: {name}"
for path in [OUTER/"main.py", *ROOT.rglob("*.py")]:
    content=path.read_bytes()
    assert content.startswith(b"#!/usr/bin/env python3"), f"Python shebang missing: {path}"
    compile(content, str(path), "exec")
assert (OUTER/"main.py").stat().st_mode & stat.S_IXUSR, "root launcher lost executable permission"
assert hashlib.sha256((OUTER/"README.md").read_bytes().replace(VERSION.encode(), PRIOR.encode())).hexdigest() == '5690081f4216206dc72b57a162ebc591c95ec6fa9349f3959e49f9739796ccc5', "public README changed beyond version"
assert hashlib.sha256((ROOT/"README.md").read_bytes().replace(VERSION.encode(), PRIOR.encode())).hexdigest() == 'a0081f3d39f2db4f8cb304b958cd64e7d2c33af96c8c372acaf599a050b6dd80', "internal README changed beyond version"
assert (ROOT/"app.py").is_file(), "app.py not retained"
assert (ROOT/"widgets"/"__init__.py").is_file() and (ROOT/"widgets"/"rwpyn"/"__init__.py").is_file(), "x12.3 widget package missing"
print("PASS: x12.2 Python shebangs, content preservation, permissions, and README protection")
