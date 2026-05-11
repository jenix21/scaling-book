#!/usr/bin/env python3
"""Report Korean translations whose English source has changed since translation.

For each ko/*.md file, reads `source_file` and `source_commit` from the YAML
frontmatter, then asks git for the most recent commit touching the matching
English file. If they differ, the translation is stale.

Exit 0 when everything is current, 1 when at least one translation is stale.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
KO_DIR = REPO_ROOT / "ko"
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
SKIP_FILES = {"TRANSLATION_STATUS.md", "README.md", "dropdown.md"}


def parse_frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER_RE.search(text)
    if not match:
        return {}
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line or line.lstrip().startswith("-"):
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip().strip('"\'')
    return fields


def latest_commit(path: Path) -> str | None:
    rel = path.relative_to(REPO_ROOT).as_posix()
    try:
        out = subprocess.check_output(
            ["git", "log", "-1", "--format=%h", "--", rel],
            cwd=REPO_ROOT,
            text=True,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return out or None


def main() -> int:
    if not KO_DIR.is_dir():
        print(f"No {KO_DIR.relative_to(REPO_ROOT)} directory — nothing to check.")
        return 0

    stale: list[tuple[str, str, str]] = []
    missing_meta: list[str] = []
    ok = 0

    for ko_file in sorted(KO_DIR.glob("*.md")):
        if ko_file.name in SKIP_FILES:
            continue
        fm = parse_frontmatter(ko_file.read_text(encoding="utf-8"))
        source_file = fm.get("source_file")
        recorded = fm.get("source_commit")
        if not source_file or not recorded:
            missing_meta.append(ko_file.name)
            continue

        source_path = REPO_ROOT / source_file
        if not source_path.exists():
            print(f"  WARN {ko_file.name}: source file {source_file} not found")
            continue

        current = latest_commit(source_path)
        if current is None:
            print(f"  WARN {ko_file.name}: could not read git log for {source_file}")
            continue

        if current.startswith(recorded) or recorded.startswith(current):
            ok += 1
        else:
            stale.append((ko_file.name, recorded, current))

    print(f"{ok} translation(s) up to date.")
    if missing_meta:
        print(f"{len(missing_meta)} translation(s) missing source_file/source_commit:")
        for name in missing_meta:
            print(f"  - {name}")
    if stale:
        print(f"{len(stale)} translation(s) stale:")
        for name, recorded, current in stale:
            print(f"  - {name}: recorded {recorded}, latest {current}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
