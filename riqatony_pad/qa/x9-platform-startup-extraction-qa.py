#!/usr/bin/env python3
"""x9.0: unchanged platform/startup function bodies and all x8 editor methods."""
import ast,hashlib,json
from pathlib import Path
from source_contract import contract_text
ROOT=Path(__file__).resolve().parents[1]
info=json.loads((ROOT/'qa/x9-platform-startup-fingerprints.json').read_text(encoding='utf-8'))
assert info['baseline']=='2.0.0-x8.0'
parse=lambda name:ast.parse(contract_text(ROOT) if name=='app.py' else (ROOT/name).read_text(encoding='utf-8'))
sha=lambda node:hashlib.sha256(ast.dump(node,include_attributes=False).encode()).hexdigest()
platform=parse('editor_platform_startup.py')
actual={n.name:sha(n) for n in platform.body if isinstance(n,ast.FunctionDef)}
assert actual==info['functions'], 'one or more relocated startup/helper definitions drifted from x8'
host=parse('app.py')
cls=next(n for n in host.body if isinstance(n,ast.ClassDef) and n.name=='RiqatonyPad')
methods={n.name:sha(n) for n in cls.body if isinstance(n,ast.FunctionDef)}
lifecycle=parse('widgets/rwpyn/editor_lifecycle.py')
lifecycle_cls=next(n for n in lifecycle.body if isinstance(n,ast.ClassDef) and n.name=='EditorFileLifecycleMixin')
assert not set(methods)&{n.name for n in lifecycle_cls.body if isinstance(n,ast.FunctionDef)}
methods.update({n.name:sha(n) for n in lifecycle_cls.body if isinstance(n,ast.FunctionDef)})
assert methods==info['host_methods'], 'one or more remaining editor methods changed'
assert set(info['moved'])==set(actual)
assert not set(info['moved'][:-1]) & {n.name for n in host.body if isinstance(n,ast.FunctionDef)}
assert any(n.name=='main' for n in host.body if isinstance(n,ast.FunctionDef))
text=contract_text(ROOT)
for literal in ('_editor_platform_startup.RiqatonyPad = RiqatonyPad',
                '_editor_platform_startup.APP_VERSION = APP_VERSION',
                '_editor_platform_startup.SMOKE_TEST_MODE = SMOKE_TEST_MODE',
                '_editor_platform_startup.FORMAT_PARITY_PROBE_MODE = FORMAT_PARITY_PROBE_MODE',
                '_editor_platform_startup.configure_platform_identity = configure_platform_identity',
                '_editor_platform_startup.resource_path = resource_path',
                'return _editor_platform_startup.main()'):
    assert literal in text, literal
assert 'from editor_platform_startup import (' in text
assert 'from editor_platform_startup import (' in text
assert 'OPEN_WINDOWS, register_window' in text
print('PASS: RiqatonyPad 2.0.0-x9.0 platform/startup functions and remaining editor AST are unchanged')
