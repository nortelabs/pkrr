from __future__ import annotations

import re
from typing import Tuple

SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:[-+].*)?$")


def parse_semver(version: str) -> Tuple[int, int, int]:
    m = SEMVER_RE.match(version)
    if not m:
        raise ValueError(f"Invalid semantic version: {version}")
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def bump_version(version: str, kind: str) -> str:
    major, minor, patch = parse_semver(version)
    if kind == "patch":
        patch += 1
    elif kind == "minor":
        minor += 1
        patch = 0
    elif kind == "major":
        major += 1
        minor = 0
        patch = 0
    else:
        raise ValueError("Bump kind must be 'patch', 'minor', or 'major'")
    return f"{major}.{minor}.{patch}"
