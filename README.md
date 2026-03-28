# pkrr

[![Python Versions](https://img.shields.io/pypi/pyversions/pkrr.svg)](https://pypi.python.org/pypi/pkrr/)
[![PyPI](https://img.shields.io/pypi/v/pkrr)](https://pypi.org/project/pkrr/#history)
[![Repo Status](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)
Unified CLI to scaffold, build, test, lint, and document Python and R packages from a single, consistent workflow.

## Why pkrr?

Many packages exist in both R and Python — either as ports of each other or as parallel implementations for different audiences. Data science teams often use R for analysis and Python for production, while community projects like ggplot2/plotnine, tidyverse/pyjanitor, and bioconductor/scanpy show how common cross-language packaging is.

Maintaining packages in both languages means juggling two build systems, two test frameworks, two sets of linting rules, and two version files. One wrong step and your versions drift, your metadata is inconsistent, or your CI only tests one language.

`pkrr` solves this by:

- **Unifying your workflow** — one CLI for build, test, lint, docs, and versioning across both languages
- **Preventing version drift** — bump the version once and it propagates to `pyproject.toml` and `DESCRIPTION` automatically
- **Scaffolding quickly** — generate a ready-to-run package skeleton for either language in seconds
- **Checking your environment** — `pkrr doctor` tells you exactly what tools you're missing before you start

If you maintain a package in both Python and R, or you're porting one to the other, `pkrr` keeps everything in sync from a single `pkg.yaml` manifest.

## Install

```bash
# Run without installing (recommended)
uvx pkrr

# Install into current environment
uv pip install pkrr

# Install as a standalone CLI tool
uv tool install pkrr

# Developer install from source
git clone https://github.com/<owner>/pkrr.git
cd pkrr
uv pip install -e .
```

## Quick start

```bash
# Scaffold a new Python package
pkrr new python my-package

# Scaffold a new R package
pkrr new r my-r-package

# Initialize pkg.yaml in an existing directory
pkrr init --name my-package --languages python,r
```

## Commands

| Command | Description |
|---------|-------------|
| `pkrr new <lang> <name>` | Scaffold a new package from templates |
| `pkrr init` | Create a `pkg.yaml` manifest in the current directory |
| `pkrr build` | Build artifacts for the package(s) |
| `pkrr test` | Run tests for the package(s) |
| `pkrr lint` | Run linters for the package(s) |
| `pkrr docs` | Build documentation for the package(s) |
| `pkrr version` | Bump or set the version and propagate to ecosystem files |
| `pkrr doctor` | Diagnose local environment for Python and R tooling |

Most commands accept a `--lang` flag to restrict operations to a single language.

## Usage

### Scaffold a new package

```bash
pkrr new python my-lib                      # creates my-lib/ with pyproject.toml, src/, tests/, docs/
pkrr new r my-r-lib                         # creates my-r-lib/ with DESCRIPTION, R/, tests/, NAMESPACE
pkrr new python my-lib --template minimal   # specify a template (default: minimal)
```

### Initialize an existing project

```bash
pkrr init --name my-project --version 1.0.0 --license MIT --languages python,r
```

This creates a `pkg.yaml` manifest that tracks metadata shared across languages.

### Build, test, lint, docs

```bash
pkrr build                # python: python -m build; R: R CMD build .
pkrr test                 # python: pytest; R: testthat::test_local()
pkrr lint                 # python: ruff + black; R: lintr::lint_package()
pkrr docs                 # python: mkdocs; R: pkgdown::build_site()

# Restrict to one language in a multi-language project
pkrr build --lang python
pkrr test --lang r
```

### Version management

```bash
pkrr version patch                     # 0.1.0 -> 0.1.1
pkrr version minor                     # 0.1.1 -> 0.2.0
pkrr version major                     # 0.2.0 -> 1.0.0
pkrr version --set 2.0.0               # set exact version
pkrr version patch --dry-run           # show what would change without writing
pkrr version patch --no-propagate      # update pkg.yaml only, skip ecosystem files
pkrr version patch --lang python       # propagate only to Python ecosystem files
```

Version changes are propagated to language-specific files automatically:
- **Python**: updates `version` in `pyproject.toml`
- **R**: updates `Version` in `DESCRIPTION`

### Diagnose environment

```bash
pkrr doctor
```

Checks for required tooling (Python, pip, pytest, ruff, black, mkdocs, R, Rscript, testthat, lintr, pkgdown, pandoc) and reports what is missing.

## The manifest (`pkg.yaml`)

`pkrr` uses a `pkg.yaml` file as the single source of truth for package metadata. Example:

```yaml
name: my-package
version: 0.1.0
license: MIT
description: My awesome package
languages:
  - python
  - r
authors:
  - name: Jane Doe
    email: jane@example.com
keywords:
  - data
python:
  build_backend: hatchling
  requires: []
r:
  depends: []
docs:
  python: mkdocs
  r: pkgdown
ci:
  provider: none
  release_on_tag: false
```

## Supported languages

| Language | Build | Test | Lint | Docs | Version propagation |
|----------|-------|------|------|------|---------------------|
| Python | `python -m build` | `pytest` | `ruff`, `black` | `mkdocs` | `pyproject.toml` |
| R | `R CMD build` | `testthat` | `lintr` | `pkgdown` | `DESCRIPTION` |

## Dependencies

- Python >= 3.9
- typer, pydantic, PyYAML, Jinja2 (installed automatically)

Per-language tooling (pytest, ruff, R, etc.) must be installed separately. Run `pkrr doctor` to check what you need.
