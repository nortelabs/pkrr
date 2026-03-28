from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field
import yaml
import os


class Author(BaseModel):
    name: str
    email: Optional[str] = None


class Manifest(BaseModel):
    name: str
    version: str
    license: str
    description: Optional[str] = None
    authors: List[Author] = Field(default_factory=list)
    homepage: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    languages: List[str]
    python: dict = Field(default_factory=dict)
    r: dict = Field(default_factory=dict)
    docs: dict = Field(default_factory=dict)
    ci: dict = Field(default_factory=dict)

    def model_dump_yaml(self) -> str:
        return yaml.safe_dump(self.model_dump(), sort_keys=False)


def create_default_manifest(
    name: str,
    version: str = "0.1.0",
    license: str = "MIT",
    languages: List[str] | None = None,
) -> Manifest:
    languages = languages or ["python"]
    m = Manifest(
        name=name,
        version=version,
        license=license,
        languages=languages,
        python={"build_backend": "hatchling", "requires": []},
        r={"depends": []},
        docs={"python": "mkdocs", "r": "pkgdown"},
        ci={"provider": "none", "release_on_tag": False},
    )
    return m


def load_manifest(path: str) -> Manifest:
    fp = os.path.join(path, "pkg.yaml")
    if not os.path.exists(fp):
        raise FileNotFoundError(
            "pkg.yaml not found; run 'pkrr init' first or use 'pkrr new'"
        )
    with open(fp, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return Manifest.model_validate(data)


def save_manifest(m: Manifest, path: str) -> None:
    fp = os.path.join(path, "pkg.yaml")
    with open(fp, "w", encoding="utf-8") as f:
        f.write(m.model_dump_yaml())
