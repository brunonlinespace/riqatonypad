#!/usr/bin/env python3
"""x13.5 release gate: grapheme semantics, cache, PNG integrity and narrow scope."""
from __future__ import annotations
import ast, hashlib, importlib.util, json, sys, types
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PREV=Path(__file__).resolve().parent/'x135-predecessor.json'
record=json.loads(PREV.read_text(encoding='utf-8'))
assert record['predecessor']=='2.0.0-x13.4'
assert record['release']=='2.0.0-x13.5'

# Production code and all binary assets not explicitly authorized to change
# remain byte-for-byte identical to the x13.4 snapshot.
for relative,digest in record['untouched_files'].items():
    path=ROOT/relative
    assert path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==digest,relative

assert not list(ROOT.rglob('*.svg')), 'SVG files remain in the source'
assert not any((ROOT/'tools'/name).exists() for name in ('generate-classic-ribbon-icons.py','generate-ribbon-icons.py'))
assert len(list(ROOT.rglob('*.png')))==record['png_count']==658
for relative,digest in record['png_files'].items():
    assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==digest,relative
assert len(record['png_files'])==658

source=(ROOT/'app.py').read_text(encoding='utf-8')
assert 'APP_VERSION = "2.0.0-x13.5"' in source
assert 'characters=count_visible_characters(self.text_area.document())' in source
assert 'characterCount()-1' not in ast.get_source_segment(source,next(
    fn for cls in ast.parse(source).body if isinstance(cls,ast.ClassDef) and cls.name=='RiqatonyPad'
    for fn in cls.body if isinstance(fn,ast.FunctionDef) and fn.name=='update_status_counts'))
assert '"{mode} · Chars {characters:,} · {self.zoom_percent}%"' in source
assert 'self._critical_editor_message_kind = warning_kind if critical else None' in source
for path,expected in record['unchanged_ast_methods'].items():
    filename,class_method=path.split('::',1)
    cls_name,method_name=class_method.split('.',1)
    tree=ast.parse((ROOT/filename).read_text(encoding='utf-8'))
    cls=next(c for c in tree.body if isinstance(c,ast.ClassDef) and c.name==cls_name)
    fn=next(f for f in cls.body if isinstance(f,ast.FunctionDef) and f.name==method_name)
    actual=hashlib.sha256(ast.dump(fn,include_attributes=False).encode('utf-8')).hexdigest()
    assert actual==expected,path

# Runtime exercise with faithful Qt protocol doubles. The double's segmenter
# uses the Unicode grapheme regex when available; this is NOT an actual Qt GUI
# test. On systems with PyQt6, live Qt integration remains a separate gate.
try:
    import regex
except ImportError:
    regex=None

class FakeBoundaryFinder:
    class BoundaryType:
        Grapheme=object()
    calls=[]
    def __init__(self,kind,text):
        assert kind is self.BoundaryType.Grapheme
        self.calls.append(text)
        if regex is None:
            raise RuntimeError('unicode-regex QA extension unavailable')
        self.boundaries=[m.end() for m in regex.finditer(r'\X',text)]
        self.index=0
    def toNextBoundary(self):
        if self.index>=len(self.boundaries):return -1
        boundary=self.boundaries[self.index];self.index+=1;return boundary
class FakeTextBlockUserData: pass
core=types.ModuleType('PyQt6.QtCore');core.QTextBoundaryFinder=FakeBoundaryFinder
gui=types.ModuleType('PyQt6.QtGui');gui.QTextBlockUserData=FakeTextBlockUserData
old={key:sys.modules.get(key) for key in ('PyQt6','PyQt6.QtCore','PyQt6.QtGui')}
sys.modules['PyQt6']=types.ModuleType('PyQt6');sys.modules['PyQt6.QtCore']=core;sys.modules['PyQt6.QtGui']=gui
try:
    module_path=ROOT/'widgets/rwpyn/character_count.py'
    spec=importlib.util.spec_from_file_location('riqatonypad_grapheme_qa',module_path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
finally:
    for key,value in old.items():
        if value is None:sys.modules.pop(key,None)
        else:sys.modules[key]=value

class Block:
    def __init__(self,doc,index):self.doc=doc;self.index=index
    def isValid(self):return 0<=self.index<len(self.doc.items)
    def revision(self):return self.doc.items[self.index][1]
    def userData(self):return self.doc.items[self.index][2]
    def setUserData(self,value):self.doc.items[self.index][2]=value
    def text(self):return self.doc.items[self.index][0]
    def next(self):return Block(self.doc,self.index+1)
class Document:
    def __init__(self,parts):self.items=[[text,1,None] for text in parts]
    def begin(self):return Block(self,0)
    def edit(self,index,text):
        self.items[index][0]=text
        self.items[index][1]+=1

if regex:
    examples=[('',0),('ABC',3),('😀',1),('e\u0301',1),('👩‍👩‍👧‍👦',1),('🇵🇹',1),('👍🏽',1),('क्\u200dष',1),('a b!',4),('\ufffc',1)]
    for text,count in examples:
        document=Document([text]);assert module.count_visible_characters(document)==count,(text,count)
    doc=Document(['Hello','👩‍👩‍👧‍👦',''])
    assert module.count_visible_characters(doc)==8  # 5 + break + 1 + break
    first=len(FakeBoundaryFinder.calls)
    for _ in range(10):assert module.count_visible_characters(doc)==8
    assert len(FakeBoundaryFinder.calls)==first,'cursor/status-only update re-segmented unchanged blocks'
    doc.edit(1,'😀😀')
    assert module.count_visible_characters(doc)==9
    assert FakeBoundaryFinder.calls[-1]=='😀😀'
    print('PASS: grapheme Unicode examples and QTextBlock revision caching (Qt protocol double)')
else:
    print('SKIP: regex extension absent for grapheme protocol-double examples; actual Qt UI testing required')
print('PASS: x13.5 scope, predecessor PNG hashes, SVG elimination, unchanged methods and warning preservation')
