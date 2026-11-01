#!/usr/bin/env python3
"""2.0.0-x13.0: exact four-field editor status order; no surrounding source modifications."""
from pathlib import Path
import hashlib, ast, json
ROOT=Path(__file__).resolve().parents[1]
APP=ROOT/'app.py'
src=APP.read_text(encoding='utf-8')
new_order='self.app_status_bar.addWidget(self.operation_mode_label); self.app_status_bar.addWidget(self.counter_label); self.app_status_bar.addWidget(self.zoom_label); self.app_status_bar.addWidget(self.status_message_label,1)'
old_order='self.app_status_bar.addWidget(self.operation_mode_label); self.app_status_bar.addWidget(self.zoom_label); self.app_status_bar.addWidget(self.counter_label); self.app_status_bar.addWidget(self.status_message_label,1)'
assert src.count(new_order)==1, 'approved status field ordering absent or duplicated'
assert old_order not in src, 'old status field order retained'
restored=src.replace(new_order,old_order).replace('2.0.0-x13.0','2.0.0-x12.5')
assert hashlib.sha256(restored.encode()).hexdigest()=='e87387e609d81f2325214c39e6af73fd595290318037922db68177697b20ef7e', 'other changes to editor production code'
assert 'self.counter_label.setText(f"Chars {characters:,}")' in src, 'numeric grouping altered'
assert 'self.status_message_label.setToolTip(text)' in src, 'independent messages altered'
assert 'self.status_message_label.setMinimumWidth(0)' in src, 'message field sizing altered'
assert src.count('self.app_status_bar.addWidget(self.status_message_label')==1, 'message ownership changed'
assert src.index(new_order) < src.index('def update_status_counts('), 'unexpected status method relocation'
print('PASS: 2.0.0-x13.0 editor order, preserved formatting, message behavior and original editor source')
