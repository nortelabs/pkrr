from __future__ import annotations

import os
import shutil
import subprocess
from typing import Mapping

from pkrr.core.templates import render_template_dir
import re


class RProvider:
    lang = "r"

    def scaffold(self, dest: str, manifest: Mapping) -> None:
        template_root = os.path.join(
            os.path.dirname(__file__), "..", "templates", "r", "minimal"
        )
        template_root = os.path.abspath(template_root)
        # Sanitize R package name: start with a letter, letters/digits/.
        raw = manifest["name"]
        safe = re.sub(r"[^A-Za-z0-9.]", "", raw)
        if not safe or not safe[0].isalpha():
            safe = f"pkg{safe}"
        ctx = dict(manifest)
        ctx["name"] = safe
        render_template_dir(template_root, dest, ctx)

    def _run_R(self, expr: str, cwd: str) -> None:
        if shutil.which("Rscript") is None:
            raise FileNotFoundError("Missing required tool: Rscript")
        proc = subprocess.run(["Rscript", "-e", expr], cwd=cwd)
        if proc.returncode != 0:
            raise RuntimeError(f"R command failed: {expr}")

    def build(self, cwd: str, manifest: Mapping) -> None:
        # R CMD build .
        if shutil.which("R") is None:
            raise FileNotFoundError("Missing required tool: R")
        proc = subprocess.run(["R", "CMD", "build", "."], cwd=cwd)
        if proc.returncode != 0:
            raise RuntimeError("R CMD build failed")

    def test(self, cwd: str, manifest: Mapping) -> None:
        self._run_R(
            "if (!requireNamespace('testthat', quietly=TRUE)) quit(status=10); testthat::test_local()",
            cwd,
        )

    def lint(self, cwd: str, manifest: Mapping) -> None:
        self._run_R(
            "if (!requireNamespace('lintr', quietly=TRUE)) quit(status=10); lintr::lint_package();",
            cwd,
        )

    def docs(self, cwd: str, manifest: Mapping) -> None:
        try:
            self._run_R(
                "if (!requireNamespace('pkgdown', quietly=TRUE)) quit(status=10); pkgdown::build_site()",
                cwd,
            )
            return
        except (FileNotFoundError, RuntimeError):
            # docs-light fallback: create docs/index.md from README.md (Pandoc/pkgdown unavailable)
            pass
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
            desc = manifest.get("description") or "Package documentation"
            with open(index, "w", encoding="utf-8") as wf:
                wf.write(f"# {name}\n\n{desc}\n")
        print("pkgdown/pandoc unavailable; generated docs-light at ./docs/index.md")

    def version_apply(self, cwd: str, manifest: Mapping) -> None:
        """Update Version in DESCRIPTION if present."""
        desc = os.path.join(cwd, "DESCRIPTION")
        if not os.path.exists(desc):
            return
        new_ver = manifest.get("version")
        out_lines = []
        with open(desc, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("Version:"):
                    out_lines.append(f"Version: {new_ver}\n")
                else:
                    out_lines.append(line)
        with open(desc, "w", encoding="utf-8") as f:
            f.writelines(out_lines)
