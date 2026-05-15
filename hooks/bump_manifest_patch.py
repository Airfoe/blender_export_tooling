#!/usr/bin/env python3
from pathlib import Path
import re
import sys

SCRIPT_ROOT = Path(__file__).resolve().parent
MANIFEST_FILE = SCRIPT_ROOT.parent / "blender_manifest.toml"

if not MANIFEST_FILE.exists():
    print(f"Error: {MANIFEST_FILE} does not exist.")
    sys.exit(1)

content = MANIFEST_FILE.read_text(encoding="utf-8")
pattern = re.compile(r'^(version\s*=\s*)"(\d+)\.(\d+)\.(\d+)"(.*)$', re.MULTILINE)
match = pattern.search(content)

if not match:
    print("Error: could not find a valid version line in blender_manifest.toml.")
    sys.exit(1)

major = int(match.group(2))
minor = int(match.group(3))
patch = int(match.group(4))
new_patch = patch + 1
new_version = f'{major}.{minor}.{new_patch}'
new_line = f'{match.group(1)}"{new_version}"{match.group(5)}'
new_content = content[: match.start()] + new_line + content[match.end() :]

if new_content == content:
    print("No version change needed.")
    sys.exit(0)

MANIFEST_FILE.write_text(new_content, encoding="utf-8")
print(f"Updated blender_manifest.toml version: {major}.{minor}.{patch} -> {new_version}")
print("Please stage the updated manifest and re-run the commit.")
sys.exit(1)
