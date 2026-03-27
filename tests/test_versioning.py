from __future__ import annotations

import os
from pathlib import Path

import yaml
from typer.testing import CliRunner

from rpx.cli import app


PYPROJECT_MINIMAL = """
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "demo_pkg"
version = "0.1.0"
description = ""
readme = "README.md"
requires-python = ">=3.9"
license = { text = "MIT" }
authors = []
keywords = []
urls = { Homepage = "" }
dependencies = []
"""


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_bump_patch_updates_pkg_and_pyproject(tmp_path: Path, monkeypatch):
    # Arrange
    pkg = {
        "name": "demo_pkg",
        "version": "0.1.0",
        "license": "MIT",
        "languages": ["python"],
        "python": {"build_backend": "hatchling", "requires": []},
        "r": {"depends": []},
        "docs": {"python": "mkdocs", "r": "pkgdown"},
        "ci": {"provider": "none", "release_on_tag": False},
    }
    write_file(tmp_path / "pkg.yaml", yaml.safe_dump(pkg, sort_keys=False))
    write_file(tmp_path / "pyproject.toml", PYPROJECT_MINIMAL)
    write_file(tmp_path / "README.md", "demo")

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    # Act
    result = runner.invoke(app, ["version", "patch"])  # 0.1.0 -> 0.1.1

    # Assert
    assert result.exit_code == 0, result.output
    new_pkg = yaml.safe_load((tmp_path / "pkg.yaml").read_text(encoding="utf-8"))
    assert new_pkg["version"] == "0.1.1"
    pyproj = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    assert 'version = "0.1.1"' in pyproj


def test_set_version_updates_r_description(tmp_path: Path, monkeypatch):
    # Arrange
    pkg = {
        "name": "demoR",
        "version": "0.2.3",
        "license": "MIT",
        "languages": ["r"],
        "python": {"build_backend": "hatchling", "requires": []},
        "r": {"depends": []},
        "docs": {"python": "mkdocs", "r": "pkgdown"},
        "ci": {"provider": "none", "release_on_tag": False},
    }
    write_file(tmp_path / "pkg.yaml", yaml.safe_dump(pkg, sort_keys=False))
    write_file(
        tmp_path / "DESCRIPTION",
        "\n".join(
            [
                "Package: demoR",
                "Title: T",
                "Version: 0.2.3",
                "Description: D",
            ]
        ),
    )
    write_file(tmp_path / "README.md", "demo")

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    # Act
    result = runner.invoke(app, ["version", "--set", "0.3.0"])

    # Assert
    assert result.exit_code == 0, result.output
    new_pkg = yaml.safe_load((tmp_path / "pkg.yaml").read_text(encoding="utf-8"))
    assert new_pkg["version"] == "0.3.0"
    desc = (tmp_path / "DESCRIPTION").read_text(encoding="utf-8")
    assert "Version: 0.3.0" in desc


def test_dry_run_does_not_modify_files(tmp_path: Path, monkeypatch):
    # Arrange
    pkg = {
        "name": "demo_pkg",
        "version": "1.0.0",
        "license": "MIT",
        "languages": ["python", "r"],
        "python": {"build_backend": "hatchling", "requires": []},
        "r": {"depends": []},
        "docs": {"python": "mkdocs", "r": "pkgdown"},
        "ci": {"provider": "none", "release_on_tag": False},
    }
    write_file(tmp_path / "pkg.yaml", yaml.safe_dump(pkg, sort_keys=False))
    write_file(tmp_path / "pyproject.toml", PYPROJECT_MINIMAL.replace("0.1.0", "1.0.0"))
    write_file(
        tmp_path / "DESCRIPTION",
        "\n".join(
            ["Package: demo_pkg", "Title: T", "Version: 1.0.0", "Description: D"]
        ),
    )

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    # Act
    result = runner.invoke(app, ["version", "minor", "--dry-run"])

    # Assert
    assert result.exit_code == 0, result.output
    # Files unchanged
    new_pkg = yaml.safe_load((tmp_path / "pkg.yaml").read_text(encoding="utf-8"))
    assert new_pkg["version"] == "1.0.0"
    pyproj = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    assert 'version = "1.0.0"' in pyproj
    desc = (tmp_path / "DESCRIPTION").read_text(encoding="utf-8")
    assert "Version: 1.0.0" in desc


def test_no_propagate_only_updates_manifest(tmp_path: Path, monkeypatch):
    # Arrange
    pkg = {
        "name": "demo_pkg",
        "version": "0.9.0",
        "license": "MIT",
        "languages": ["python", "r"],
        "python": {"build_backend": "hatchling", "requires": []},
        "r": {"depends": []},
        "docs": {"python": "mkdocs", "r": "pkgdown"},
        "ci": {"provider": "none", "release_on_tag": False},
    }
    write_file(tmp_path / "pkg.yaml", yaml.safe_dump(pkg, sort_keys=False))
    write_file(tmp_path / "pyproject.toml", PYPROJECT_MINIMAL.replace("0.1.0", "0.9.0"))
    write_file(
        tmp_path / "DESCRIPTION",
        "\n".join(
            ["Package: demo_pkg", "Title: T", "Version: 0.9.0", "Description: D"]
        ),
    )

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    # Act
    result = runner.invoke(
        app, ["version", "minor", "--no-propagate"]
    )  # 0.9.0 -> 0.10.0

    # Assert manifest updated
    assert result.exit_code == 0, result.output
    new_pkg = yaml.safe_load((tmp_path / "pkg.yaml").read_text(encoding="utf-8"))
    assert new_pkg["version"] == "0.10.0"
    # Ecosystem files unchanged
    pyproj = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    assert 'version = "0.9.0"' in pyproj
    desc = (tmp_path / "DESCRIPTION").read_text(encoding="utf-8")
    assert "Version: 0.9.0" in desc


def test_lang_filter_only_updates_specific_language(tmp_path: Path, monkeypatch):
    # Arrange
    pkg = {
        "name": "demo_pkg",
        "version": "2.1.0",
        "license": "MIT",
        "languages": ["python", "r"],
        "python": {"build_backend": "hatchling", "requires": []},
        "r": {"depends": []},
        "docs": {"python": "mkdocs", "r": "pkgdown"},
        "ci": {"provider": "none", "release_on_tag": False},
    }
    write_file(tmp_path / "pkg.yaml", yaml.safe_dump(pkg, sort_keys=False))
    write_file(tmp_path / "pyproject.toml", PYPROJECT_MINIMAL.replace("0.1.0", "2.1.0"))
    write_file(
        tmp_path / "DESCRIPTION",
        "\n".join(
            ["Package: demo_pkg", "Title: T", "Version: 2.1.0", "Description: D"]
        ),
    )

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    # Act: bump patch but only propagate to python
    result = runner.invoke(
        app, ["version", "patch", "--lang", "python"]
    )  # 2.1.0 -> 2.1.1

    assert result.exit_code == 0, result.output
    new_pkg = yaml.safe_load((tmp_path / "pkg.yaml").read_text(encoding="utf-8"))
    assert new_pkg["version"] == "2.1.1"
    pyproj = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    assert 'version = "2.1.1"' in pyproj
    desc = (tmp_path / "DESCRIPTION").read_text(encoding="utf-8")
    # R not propagated
    assert "Version: 2.1.0" in desc


def test_conflicting_flags_errors(tmp_path: Path, monkeypatch):
    # Arrange
    pkg = {
        "name": "demo_pkg",
        "version": "3.0.0",
        "license": "MIT",
        "languages": ["python"],
        "python": {"build_backend": "hatchling", "requires": []},
        "r": {"depends": []},
        "docs": {"python": "mkdocs", "r": "pkgdown"},
        "ci": {"provider": "none", "release_on_tag": False},
    }
    write_file(tmp_path / "pkg.yaml", yaml.safe_dump(pkg, sort_keys=False))
    write_file(tmp_path / "pyproject.toml", PYPROJECT_MINIMAL.replace("0.1.0", "3.0.0"))

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    # Act: conflicting flags
    result = runner.invoke(app, ["version", "patch", "--set", "3.1.0"])

    # Assert: error and no changes
    assert result.exit_code != 0
    new_pkg = yaml.safe_load((tmp_path / "pkg.yaml").read_text(encoding="utf-8"))
    assert new_pkg["version"] == "3.0.0"
    pyproj = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    assert 'version = "3.0.0"' in pyproj


def test_invalid_semver_errors_without_changes(tmp_path: Path, monkeypatch):
    # Arrange
    pkg = {
        "name": "demo_pkg",
        "version": "notsemver",
        "license": "MIT",
        "languages": ["python"],
        "python": {"build_backend": "hatchling", "requires": []},
        "r": {"depends": []},
        "docs": {"python": "mkdocs", "r": "pkgdown"},
        "ci": {"provider": "none", "release_on_tag": False},
    }
    write_file(tmp_path / "pkg.yaml", yaml.safe_dump(pkg, sort_keys=False))
    write_file(tmp_path / "pyproject.toml", PYPROJECT_MINIMAL.replace("0.1.0", "0.0.1"))

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    # Act
    result = runner.invoke(app, ["version", "patch"])  # should fail to parse

    # Assert
    assert result.exit_code != 0
    new_pkg = yaml.safe_load((tmp_path / "pkg.yaml").read_text(encoding="utf-8"))
    assert new_pkg["version"] == "notsemver"
    pyproj = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    assert 'version = "0.0.1"' in pyproj
