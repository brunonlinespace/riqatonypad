#!/usr/bin/env python3
"""AST-parity and import-surface gate for x1.0, pinned to RiqatonyPad 1.1.2."""
import ast, hashlib
from pathlib import Path
from source_contract import contract_text
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'widgets/rwpyn/editor_widgets.py').read_text(encoding="utf-8")
original=contract_text(ROOT)
classes={x.name:x for x in ast.parse(source).body if isinstance(x,ast.ClassDef)}
expected={'SafeTextDocument': '96fe6df2d82f637828d0de09e5f3e7281a6220beb0568e5e55b6ad5acf2ca71b', 'RichTextEdit': 'aa662e24d36ba0f47921f4a8f9435fef50eee3824609db2d757ee882b1e680a6'}
for name,digest in expected.items():
    assert name in classes, f"{name} missing"
    actual=hashlib.sha256(ast.dump(classes[name],include_attributes=False).encode()).hexdigest()
    assert actual==digest, f"{name} differs from original RiqatonyPad 1.1.2 AST"
    assert not any(isinstance(n,ast.ClassDef) and n.name==name for n in ast.parse(original).body), f"duplicate {name} left in original host"
assert 'import' in original and 'editor_widgets' in original
assert 'from ' in source and 'sanitise_qt_html' in source
# All pre-existing host classes/functions outside the extracted widgets are untouched.
original_host_fingerprints={'read_bounded_bytes': '3762448e3b9f3b665dc707d6e158be025e5ec8022bf6d58ae75e2b108fb548cf', 'fsync_directory': 'f98dc002cf0a7480b7d1b46253d1e3c714de515c00abe275d7ab74f2cf09d6af', 'count_words': 'ee79820caeeabc599aa106fb6ff66f3e610dab9359ebe0df94227a33e4aaabbc', 'preference_bool': '84e1e50efff0ff186af497ff60bd89850896ded61f697444e5927b5488b615f8', 'preference_text': '8169dd60eb385ace8959ab3cf69099558ef7d79327f617838d6fe857aef83072', 'register_window': '8bc4762b09f36badb58b10ab7ebcaf49ee35f347d989766902dd192a5d64c17d', 'normalise_windows_organisation_directory': 'e8858b37ecbe00fd02303c291414a5a8374fbafb382e5d45e4d9e8b4e3fc5aa6', 'platform_config_locations': '04ca4231732f065251c2e0645aa612431f308c394889304a4dfe6f08042e8ab4', 'configure_platform_identity': 'b488f07a42b5dc3e10bd252dfc0861b5cddbbfa47dec69a3cb8ce30847f77b5f', 'host_process_environment': 'de1668c890fafe3c3afc96892bf67f63e131afde8ef14968135879f813c1d109', 'appimage_theme_resources': '6a065104f6304432c0033fd9258adafd7dc0e37c3c31c41fa31296a843e47c3e', 'resource_path': 'c799e167b08dde40b54a69a6bc3c488adf050cecf0179297cb0febc4e8e4fa60', 'RibbonScrollArea': '1161c15993da3c18965799485c6ba4d01dbebac6e62427dc78d6b69286561d9f', 'main': 'ba001174087a059f14e84f3f37bf621e7b46f820ed10ec626aa4ff7792fd9ae9'}
pref_nodes=ast.parse((ROOT/"widgets/rwpyn/editor_preferences.py").read_text(encoding='utf-8')).body
print_nodes=ast.parse((ROOT/"widgets/rwpyn/editor_printing.py").read_text(encoding="utf-8")).body
insertion_nodes=ast.parse((ROOT/'widgets/rwpyn/editor_insertion.py').read_text(encoding="utf-8")).body
host_nodes=ast.parse(original).body
platform_nodes=ast.parse((ROOT/"editor_platform_startup.py").read_text(encoding="utf-8")).body
ribbon_nodes=ast.parse((ROOT/'widgets/editor_ribbon_retro.py').read_text(encoding='utf-8')).body
# Normalise only the approved resource-path location adjustment back to its
# original single-directory expression before comparing the frozen x1 hash.
# The new path itself is asserted by x12.3's relocation QA.
def original_context(node):
    if isinstance(node, ast.FunctionDef) and node.name=='resource_path':
        import copy
        node=copy.deepcopy(node)
        assignments=[x for x in ast.walk(node) if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='script_dir' for t in x.targets)]
        assert len(assignments)==1
        assignments[0].value=ast.parse('os.path.dirname(os.path.abspath(__file__))',mode='eval').body
    return node
host_fingerprints={n.name: hashlib.sha256(ast.dump(original_context(n), include_attributes=False).encode()).hexdigest() for n in [*host_nodes,*ribbon_nodes,*insertion_nodes,*print_nodes,*pref_nodes,*platform_nodes] if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name not in ('RiqatonyPad','EditorInsertionMixin','EditorPrintingMixin','EditorPreferencesMixin','EditorRibbonRetroMixin')}
assert host_fingerprints==original_host_fingerprints, "host class/function AST changed outside x1.0 scope"
print('PASS: x1.0 widgets/host AST match unmodified baseline, imports preserved')
