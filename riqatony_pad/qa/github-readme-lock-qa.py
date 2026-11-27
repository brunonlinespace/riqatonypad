#!/usr/bin/env python3
"""Protected GitHub README gate for the user-approved RiqatonyPad 2.1.2 README."""
from pathlib import Path
import hashlib
root=Path(__file__).resolve().parents[2]
reference=Path(__file__).with_name("github-readme-authority.txt").read_bytes()
assert hashlib.sha256(reference).hexdigest()=="3a76e148f6f9f0c76aa6d82131ba776e58f1821522a4091cc8d8d6a1cd16b05d", "Protected README authority was changed"
actual=(root/"README.md").read_bytes()
assert actual==reference, "GitHub README differs from the approved 2.1.2 authority"
print("PASS protected GitHub README 2.1.2 authority")
