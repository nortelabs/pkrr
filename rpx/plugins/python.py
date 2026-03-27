from __future__ import annotations

import os
import shutil
import subprocess
from typing import Mapping

from rpx.core.templates import render_template_dir


class PythonProvider:
    lang = "python"

    def scaffold(self, dest: str, manifest: Mapping) -> None:
        template_root = os.path.join(
            os.path.dirname(__file__), "..", "templates", "python", "minimal"
        )
        template_root = os.path.abspath(template_root)
        ctx = manifest | {"name": manifest["name"].replace("-", "_")}
        render_template_dir(template_root, dest, ctx)

    def _run(self, args: list[str], cwd: str) -> None:
        if shutil.which(args[0]) is None:
            raise FileNotFoundError(f"Missing required tool: {args[0]}")
        proc = subprocess.run(args, cwd=cwd)
        if proc.returncode != 0:
            raise RuntimeError(f"Command failed: {' '.join(args)}")

    def build(self, cwd: str, manifest: Mapping) -> None:
        # Prefer python -m build
        if shutil.which("python") is None:
            raise FileNotFoundError("Missing required tool: python")
        self._run(["python", "-m", "build"], cwd)

    def test(self, cwd: str, manifest: Mapping) -> None:
        self._run(["pytest", "-q"], cwd)

    def lint(self, cwd: str, manifest: Mapping) -> None:
        # Run ruff then black --check if available
        if shutil.which("ruff") is not None:
            self._run(["ruff", "check", "src", "tests"], cwd)
        if shutil.which("black") is not None:
            self._run(["black", "--check", "."], cwd)

    def docs(self, cwd: str, manifest: Mapping) -> None:
        docs_cfg = (manifest.get("docs") or {}).get("python", "mkdocs")
        if docs_cfg == "mkdocs":
            try:
                self._run(["mkdocs", "build", "-q"], cwd)
                return
            except (FileNotFoundError, RuntimeError):
                # Fall back to lightweight docs if mkdocs unavailable or build fails
                pass
        # docs-light fallback: create docs/index.md from README.md
        docs_dir = os.path.join(cwd, "docs")
        os.makedirs(docs_dir, exist_ok=True)
        readme = os.path.join(cwd, "README.md")
        index = os.path.join(docs_dir, "index.md")
        if os.path.exists(readme):
            with (
                open(readme, "r", encoding="utf-8") as rf,
                open(index, "w", encoding="utf-8") as wf,
            ):
                wf.write(rf.read())
        else:
            name = manifest.get("name", "package")
            desc = manifest.get("description") or "Project documentation"
            with open(index, "w", encoding="utf-8") as wf:
                wf.write(f"# {name}\n\n{desc}\n")
        print("mkdocs unavailable; generated docs-light at ./docs/index.md")

    def version_apply(self, cwd: str, manifest: Mapping) -> None:
        """Update version in pyproject.toml if present."""
        pyproj = os.path.join(cwd, "pyproject.toml")
        if not os.path.exists(pyproj):
            return
        with open(pyproj, "r", encoding="utf-8") as f:
            lines = f.readlines()
        out = []
        in_project = False
        new_ver = manifest.get("version")
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("[project]"):
                in_project = True
                out.append(line)
                continue
            if (
                in_project
                and stripped.startswith("[")
                and not stripped.startswith("[project]")
            ):
                in_project = False
            if in_project and stripped.startswith("version"):
                out.append(f'version = "{new_ver}"\n')
            else:
                out.append(line)
        with open(pyproj, "w", encoding="utf-8") as f:
            f.writelines(out)
