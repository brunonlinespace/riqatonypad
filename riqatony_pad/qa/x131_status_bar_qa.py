#!/usr/bin/env python3
"""Current correction: exactly two status labels, no other editor-source change."""
from pathlib import Path
import hashlib

OLD_BLOCK='        self.operation_mode_label=QLabel("Insert",self.app_status_bar); self.operation_mode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)\n        self.operation_mode_label.setFixedWidth(self.operation_mode_label.fontMetrics().horizontalAdvance("Overwrite")+4)\n        self.counter_label=QLabel("Chars 0",self.app_status_bar)\n        self.counter_label.setFixedWidth(self.counter_label.fontMetrics().horizontalAdvance(f"Chars {MAX_DOCUMENT_CHARACTERS:,}")+4)\n        self.status_message_label=QLabel("",self.app_status_bar); self.status_message_label.setMinimumWidth(0); self.status_message_label.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Preferred); self.status_message_label.setToolTip("")\n        self.zoom_label=QLabel("100%",self.app_status_bar); self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter); self.zoom_label.setFixedWidth(self.zoom_label.fontMetrics().horizontalAdvance("300%")+4)\n        self._status_message_timer=QTimer(self); self._status_message_timer.setSingleShot(True); self._status_message_timer.timeout.connect(self._clear_status_message)\n        self.app_status_bar.addWidget(self.operation_mode_label); self.app_status_bar.addWidget(self.counter_label); self.app_status_bar.addWidget(self.zoom_label); self.app_status_bar.addWidget(self.status_message_label,1)'
NEW_BLOCK='        self.status_message_label=QLabel("",self.app_status_bar); self.status_message_label.setMinimumWidth(0); self.status_message_label.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Preferred); self.status_message_label.setToolTip("")\n        self.status_indicators_label=QLabel("Insert · Chars 0 · 100%",self.app_status_bar)\n        self.status_indicators_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)\n        self.status_indicators_label.setMinimumWidth(0)\n        self._status_message_timer=QTimer(self); self._status_message_timer.setSingleShot(True); self._status_message_timer.timeout.connect(self._clear_status_message)\n        self.app_status_bar.addWidget(self.status_message_label,1); self.app_status_bar.addPermanentWidget(self.status_indicators_label)'
OLD_COUNTS='        self.operation_mode_label.setText("Overwrite" if self.text_area.overwriteMode() else "Insert")\n        characters=max(0,self.text_area.document().characterCount()-1)\n        self.counter_label.setText(f"Chars {characters:,}")\n        self.zoom_label.setText(f"{self.zoom_percent}%")'
NEW_COUNTS='        mode="Overwrite" if self.text_area.overwriteMode() else "Insert"\n        characters=max(0,self.text_area.document().characterCount()-1)\n        self.status_indicators_label.setText(f"{mode} · Chars {characters:,} · {self.zoom_percent}%")'
BASELINE_SHA256='85511ad23a0a735fbbf19b52b1fa0efabf0e942bdda912d02264b3f1939f04de'
OLD_VERSION='2.0.0-x13.0'
NEW_VERSION='2.0.0-x13.1'

def restore_x130_status_source(source):
    assert source.count(NEW_BLOCK)==1 and source.count(NEW_COUNTS)==1, 'approved status code missing'
    restored=source.replace(NEW_BLOCK,OLD_BLOCK).replace(NEW_COUNTS,OLD_COUNTS)
    return restored

def verify_source(source):
    restored=restore_x130_status_source(source).replace(NEW_VERSION,OLD_VERSION)
    assert hashlib.sha256(restored.encode('utf-8')).hexdigest()==BASELINE_SHA256, 'other editor production changes detected'
    assert source.count('addWidget(self.status_message_label')==1, 'left message widget missing'
    assert source.count('addPermanentWidget(self.status_indicators_label)')==1, 'right permanent indicator missing'
    assert source.count('QLabel("Insert · Chars 0 · 100%"')==1, 'not consolidated to one indicator'
    assert 'Chars {characters:,}' in source, 'numerical grouping changed'
    assert '· {self.zoom_percent}%' in source, 'rightmost zoom missing'
    assert 'self.status_message_label.setToolTip(text)' in source, 'message tooltips changed'
    assert 'self._status_message_timer' in source, 'message timer missing'
    assert 'setFixedWidth(' not in source[source.index('self.status_message_label = QLabel(') if 'self.status_message_label = QLabel(' in source else source.index('self.status_message_label=QLabel('):source.index('self._status_message_timer')], 'obsolete fixed widths in status block'
    for obsolete in ('self.operation_mode_label', 'self.counter_label', 'self.zoom_label'):
        assert obsolete not in source, 'old status field survived: '+obsolete

if __name__=='__main__':
    package=Path(__file__).resolve().parents[1]
    editor=package/"app.py"
    verify_source(editor.read_text(encoding='utf-8'))
    print('PASS: 2.0.0-x13.1 two-field editor correction and complete editor preservation')
