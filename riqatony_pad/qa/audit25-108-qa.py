#!/usr/bin/env python3
"""Dependency-free RiqatonyPad 1.0.11 Audit 25 Ribbon group-order gate."""
from pathlib import Path
import ast, hashlib
from source_contract import contract_text
from shortcut_legacy import legacy_read_bytes
ROOT=Path(__file__).resolve().parents[1]; errors=[]
def req(c,m):
    if not c: errors.append(m)
def sha(rel):
    data=legacy_read_bytes(ROOT, rel)
    if rel in ("rtf_new_document.py", "widgets/shortcut_search.py"):
        assert data.startswith(b"#!/usr/bin/env python3\n"), f"x12.2 approved shebang missing: {rel}"
        data=data[len(b"#!/usr/bin/env python3\n"):]
    return hashlib.sha256(data).hexdigest()
source=contract_text(ROOT)
req('APP_VERSION = "2.0.0-x13.0"' in source,'1.0.11 identity missing')
ribbon_source=(ROOT/'widgets/editor_ribbon_retro.py').read_text(encoding='utf-8'); tree=ast.parse(ribbon_source); cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='EditorRibbonRetroMixin'); fn=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='build_ribbon'); ribbon=ast.get_source_segment(ribbon_source,fn) or ''
help_group='group(help_page,"Help")'; github_group='group(help_page,"GitHub")'
req(help_group in ribbon and github_group in ribbon,'Help/GitHub Ribbon groups missing')
if help_group in ribbon and github_group in ribbon: req(ribbon.index(help_group)<ribbon.index(github_group),'Help group must precede GitHub group')
for fragment in ('cab(g,"documentation",0,0)','cab(g,"tutorial",0,1)','cab(g,"shortcuts",1,0)','cab(g,"about",1,1)','cab(g,"github",0,0)','cab(g,"issue",1,0)'): req(fragment in ribbon,f'Ribbon command membership changed: {fragment}')
protected={'rtf_codec.py':'598938f533f0b562c55c901d46daef1c6de8bc788ff96eeed387d428737666b8','rich_text_support.py':'6c6d7152ad306788a72d420401a4563506e72150c389e80a61a5bdbc8d235fdb','rtf_new_document.py':'539058c822ebb5e5360b6b03f610b3ef9fc8d8196a662e402815622a05f32a41','widgets/shortcut_search.py':'c9ea5e80ffca4f5523873c5b9035e17cf802f83f0b78fa611ff0ca66d1b63310'}
for r,h in protected.items(): req(sha(r)==h,f'protected out-of-scope file changed: {r}')
if errors:
    print('RiqatonyPad 1.0.11 Audit 25 check failed:'); [print(f'- {e}') for e in errors]; raise SystemExit(1)
print('PASS: RiqatonyPad 1.0.11 Audit 25 Help-before-GitHub Ribbon contract')
