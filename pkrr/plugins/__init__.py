from __future__ import annotations

from typing import Dict

from .python import PythonProvider
from .r import RProvider

_REGISTRY: Dict[str, object] = {
    "python": PythonProvider(),
    "r": RProvider(),
}


def get(lang: str):
    lang = lang.lower()
    if lang not in _REGISTRY:
        raise KeyError(f"No provider for language: {lang}")
    return _REGISTRY[lang]


def available() -> list[str]:
    return list(_REGISTRY.keys())
