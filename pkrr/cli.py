from __future__ import annotations

import os
import sys
from typing import Optional

import typer

from pkrr.core.manifest import (
    Manifest,
    create_default_manifest,
    load_manifest,
    save_manifest,
)
from pkrr.core.templates import render_template_dir
from pkrr.core.versioning import bump_version
from pkrr.plugins import get as get_plugin, available as available_langs
import shutil
import platform
import subprocess

app = typer.Typer(
    add_completion=False, help="pkrr – unified packaging for Python and R"
)


@app.callback(invoke_without_command=True)
def callback(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


@app.command()
def init(
    name: Optional[str] = typer.Option(None, "--name", help="Package name"),
    version: Optional[str] = typer.Option(None, "--version", help="Initial version"),
    license: Optional[str] = typer.Option(
        None, "--license", help="SPDX license identifier or text"
    ),
    languages: Optional[str] = typer.Option(
        None, "--languages", help="Comma-separated languages: python,r"
    ),
):
    if name is None:
        name = typer.prompt("Package name")
    name = name.strip()
    version = version or "0.1.0"
    license = license or "MIT"
    languages = languages or "python"
    """Create a pkg.yaml manifest in the current directory."""
    langs = [l.strip() for l in languages.split(",") if l.strip()]
    m = create_default_manifest(
        name=name, version=version, license=license, languages=langs
    )
    if os.path.exists("pkg.yaml"):
        typer.secho("pkg.yaml already exists; aborting", err=True, fg=typer.colors.RED)
        raise typer.Exit(code=2)
    save_manifest(m, path=".")
    typer.secho("Created pkg.yaml", fg=typer.colors.GREEN)

    for lang in langs:
        provider = get_plugin(lang)
        provider.scaffold(os.getcwd(), m.model_dump())
        typer.secho(f"Scaffolded {lang} package", fg=typer.colors.GREEN)


@app.command()
def new(
    lang: str = typer.Argument(..., help="Language: python or r"),
    name: str = typer.Argument(..., help="New package name (creates a directory)"),
    template: str = typer.Option("minimal", "--template", help="Template name"),
):
    """Scaffold a new package directory from templates and write pkg.yaml."""
    lang = lang.lower()
    if lang not in available_langs():
        typer.secho(f"Unsupported language: {lang}", err=True, fg=typer.colors.RED)
        raise typer.Exit(code=2)

    dest = os.path.abspath(name)
    if os.path.exists(dest):
        typer.secho(
            f"Destination already exists: {dest}", err=True, fg=typer.colors.RED
        )
        raise typer.Exit(code=2)
    os.makedirs(dest, exist_ok=True)

    # Create manifest
    m = create_default_manifest(name=name, languages=[lang])
    save_manifest(m, path=dest)

    # Delegate scaffold to language provider
    provider = get_plugin(lang)
    provider.scaffold(dest, m.model_dump())
    typer.secho(f"Created {lang} package at {dest}", fg=typer.colors.GREEN)


def _run_for_langs(cmd: str, lang: Optional[str]):
    m = load_manifest(".")
    langs = [lang] if lang else m.languages
    for l in langs:
        provider = get_plugin(l)
        try:
            getattr(provider, cmd)(os.getcwd(), m.model_dump())
        except FileNotFoundError as e:
            typer.secho(str(e), err=True, fg=typer.colors.RED)
            raise typer.Exit(code=10)


@app.command()
def build(
    lang: Optional[str] = typer.Option(None, "--lang", help="Restrict to a language"),
):
    """Build artifacts for the package(s)."""
    _run_for_langs("build", lang)


@app.command()
def test(
    lang: Optional[str] = typer.Option(None, "--lang", help="Restrict to a language"),
):
    """Run tests for the package(s)."""
    _run_for_langs("test", lang)


@app.command()
def lint(
    lang: Optional[str] = typer.Option(None, "--lang", help="Restrict to a language"),
):
    """Run linters for the package(s)."""
    _run_for_langs("lint", lang)


@app.command()
def docs(
    lang: Optional[str] = typer.Option(None, "--lang", help="Restrict to a language"),
):
    """Build documentation for the package(s)."""
    _run_for_langs("docs", lang)


@app.command()
def version(
    bump: Optional[str] = typer.Argument(None, help="Bump kind: patch|minor|major"),
    set_version: Optional[str] = typer.Option(None, "--set", help="Set exact version"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show changes without writing"
    ),
    no_propagate: bool = typer.Option(
        False, "--no-propagate", help="Do not update ecosystem files"
    ),
    lang: Optional[str] = typer.Option(
        None, "--lang", help="Restrict propagation to a language"
    ),
):
    """Bump or set the version in pkg.yaml and propagate to Python/R files."""
    m = load_manifest(".")
    current = m.version
    if set_version and bump:
        typer.secho(
            "Specify either a bump kind or --set, not both",
            err=True,
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=2)
    if set_version:
        new_ver = set_version
    else:
        if bump is None:
            typer.secho(
                "Provide a bump kind (patch|minor|major) or --set X.Y.Z",
                err=True,
                fg=typer.colors.RED,
            )
            raise typer.Exit(code=2)
        bump = bump.lower()
        if bump not in {"patch", "minor", "major"}:
            typer.secho(
                "Bump kind must be patch, minor, or major",
                err=True,
                fg=typer.colors.RED,
            )
            raise typer.Exit(code=2)
        try:
            new_ver = bump_version(current, bump)
        except ValueError as e:
            typer.secho(str(e), err=True, fg=typer.colors.RED)
            raise typer.Exit(code=2)

    if dry_run:
        typer.secho(
            f"Version would change: {current} -> {new_ver}", fg=typer.colors.YELLOW
        )
        return

    # Write manifest
    m.version = new_ver
    save_manifest(m, path=".")
    typer.secho(f"Updated pkg.yaml: {current} -> {new_ver}", fg=typer.colors.GREEN)

    # Propagate to ecosystem files
    if not no_propagate:
        langs = [lang] if lang else m.languages
        for l in langs:
            provider = get_plugin(l)
            try:
                provider.version_apply(os.getcwd(), m.model_dump())
            except Exception as e:
                typer.secho(
                    f"Propagation failed for {l}: {e}", err=True, fg=typer.colors.RED
                )
                raise typer.Exit(code=20)
        typer.secho("Propagation complete", fg=typer.colors.GREEN)


@app.command()
def doctor():
    """Diagnose local environment for Python and R tooling."""
    os_name = platform.system().lower()
    typer.secho(f"Environment: {os_name}", fg=typer.colors.BLUE)

    # Python checks
    typer.secho("Python:", fg=typer.colors.BLUE)
    typer.echo(f"- interpreter: {sys.version.split()[0]}")
    # pip
    try:
        out = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True,
        )
        pip_line = out.stdout.strip() or out.stderr.strip()
        typer.echo(f"- pip: {pip_line or 'unknown'}")
    except Exception:
        typer.echo("- pip: not found")
    # Python modules/tools
    py_tools = ["build", "pytest", "ruff", "black", "mkdocs"]
    missing_py = []
    for mod in py_tools:
        try:
            __import__(mod)
            typer.echo(f"- {mod}: OK")
        except Exception:
            missing_py.append(mod)
            typer.echo(f"- {mod}: missing")

    # R checks
    typer.secho("R:", fg=typer.colors.BLUE)
    r_bin = shutil.which("R")
    rs_bin = shutil.which("Rscript")
    if r_bin:
        try:
            rv = subprocess.run([r_bin, "--version"], capture_output=True, text=True)
            version_line = (
                (rv.stdout or rv.stderr).splitlines()[0]
                if (rv.stdout or rv.stderr)
                else "unknown"
            )
            typer.echo(f"- R: {version_line}")
        except Exception:
            typer.echo("- R: found (version unknown)")
    else:
        typer.echo("- R: missing")
    typer.echo(f"- Rscript: {'OK' if rs_bin else 'missing'}")

    r_packages = ["testthat", "lintr", "pkgdown", "roxygen2"]
    missing_r_pkgs = []
    if rs_bin:
        for pkg in r_packages:
            expr = f"if (!requireNamespace('{pkg}', quietly=TRUE)) quit(status=10)"
            pr = subprocess.run([rs_bin, "-e", expr], capture_output=True)
            if pr.returncode == 0:
                typer.echo(f"- R pkg {pkg}: OK")
            else:
                missing_r_pkgs.append(pkg)
                typer.echo(f"- R pkg {pkg}: missing")
    else:
        typer.echo("- R packages: skipped (Rscript missing)")

    # Pandoc check
    pandoc_bin = shutil.which("pandoc")
    typer.echo(f"- pandoc: {'OK' if pandoc_bin else 'missing'}")

    # Suggestions
    typer.secho("Suggestions:", fg=typer.colors.BLUE)
    if missing_py:
        typer.echo(
            f"- Install Python tools: python -m pip install {' '.join(missing_py)}"
        )
    if not r_bin or not rs_bin:
        typer.echo("- Install R (and ensure Rscript is on PATH)")
    if missing_r_pkgs:
        pkg_list = ", ".join([f"'{p}'" for p in missing_r_pkgs])
        typer.echo(f"- In R: install.packages(c({pkg_list}))")
    if not pandoc_bin:
        if os_name == "darwin":
            typer.echo("- Install pandoc: brew install pandoc")
        elif os_name == "linux":
            typer.echo(
                "- Install pandoc: sudo apt-get install pandoc (or your distro equivalent)"
            )
        else:
            typer.echo("- Install pandoc from https://pandoc.org/install.html")
    typer.echo(
        "- If on macOS with Homebrew Python, prefer pipx/uvx or a virtualenv (PEP 668)"
    )

    # Exit status: success even if some tools are missing (doctor is diagnostic)
    return


def main():
    try:
        app()
    except typer.Exit as e:  # passthrough
        raise
    except Exception as e:  # safeguard
        typer.secho(str(e), err=True, fg=typer.colors.RED)
        raise SystemExit(20)


if __name__ == "__main__":
    main()
