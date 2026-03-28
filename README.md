# rpx

Unified CLI to scaffold, build, test, lint, and document Python and R packages from a single, consistent workflow.

## Why rpx?

Many packages exist in both R and Python — either as ports of each other or as parallel implementations for different audiences. Data science teams often use R for analysis and Python for production, while community projects like ggplot2/plotnine, tidyverse/pyjanitor, and bioconductor/scanpy show how common cross-language packaging is.

Maintaining packages in both languages means juggling two build systems, two test frameworks, two sets of linting rules, and two version files. One wrong step and your versions drift, your metadata is inconsistent, or your CI only tests one language.

`rpx` solves this by:

- **Unifying your workflow** — one CLI for build, test, lint, docs, and versioning across both languages
- **Preventing version drift** — bump the version once and it propagates to `pyproject.toml` and `DESCRIPTION` automatically
- **Scaffolding quickly** — generate a ready-to-run package skeleton for either language in seconds
- **Checking your environment** — `rpx doctor` tells you exactly what tools you're missing before you start

If you maintain a package in both Python and R, or you're porting one to the other, `rpx` keeps everything in sync from a single `pkg.yaml` manifest.

## Install

```bash
# Run without installing (recommended)
uvx rpx

# Install into current environment
uv pip install rpx

# Install as a standalone CLI tool
uv tool install rpx

# Developer install from source
git clone https://github.com/<owner>/rpx.git
cd rpx
uv pip install -e .
```

## Quick start

```bash
# Scaffold a new Python package
rpx new python my-package

# Scaffold a new R package
rpx new r my-r-package

# Initialize pkg.yaml in an existing directory
rpx init --name my-package --languages python,r
```

## Commands

| Command | Description |
|---------|-------------|
| `rpx new <lang> <name>` | Scaffold a new package from templates |
| `rpx init` | Create a `pkg.yaml` manifest in the current directory |
| `rpx build` | Build artifacts for the package(s) |
| `rpx test` | Run tests for the package(s) |
| `rpx lint` | Run linters for the package(s) |
| `rpx docs` | Build documentation for the package(s) |
| `rpx version` | Bump or set the version and propagate to ecosystem files |
| `rpx doctor` | Diagnose local environment for Python and R tooling |

Most commands accept a `--lang` flag to restrict operations to a single language.

## Usage

### Scaffold a new package

```bash
rpx new python my-lib                      # creates my-lib/ with pyproject.toml, src/, tests/, docs/
rpx new r my-r-lib                         # creates my-r-lib/ with DESCRIPTION, R/, tests/, NAMESPACE
rpx new python my-lib --template minimal   # specify a template (default: minimal)
```

### Initialize an existing project

```bash
rpx init --name my-project --version 1.0.0 --license MIT --languages python,r
```

This creates a `pkg.yaml` manifest that tracks metadata shared across languages.

### Build, test, lint, docs

```bash
rpx build                # python: python -m build; R: R CMD build .
rpx test                 # python: pytest; R: testthat::test_local()
rpx lint                 # python: ruff + black; R: lintr::lint_package()
rpx docs                 # python: mkdocs; R: pkgdown::build_site()

# Restrict to one language in a multi-language project
rpx build --lang python
rpx test --lang r
```

### Version management

```bash
rpx version patch                     # 0.1.0 -> 0.1.1
rpx version minor                     # 0.1.1 -> 0.2.0
rpx version major                     # 0.2.0 -> 1.0.0
rpx version --set 2.0.0               # set exact version
rpx version patch --dry-run           # show what would change without writing
rpx version patch --no-propagate      # update pkg.yaml only, skip ecosystem files
rpx version patch --lang python       # propagate only to Python ecosystem files
```

Version changes are propagated to language-specific files automatically:
- **Python**: updates `version` in `pyproject.toml`
- **R**: updates `Version` in `DESCRIPTION`

### Diagnose environment

```bash
rpx doctor
```

Checks for required tooling (Python, pip, pytest, ruff, black, mkdocs, R, Rscript, testthat, lintr, pkgdown, pandoc) and reports what is missing.

## The manifest (`pkg.yaml`)

`rpx` uses a `pkg.yaml` file as the single source of truth for package metadata. Example:

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

Per-language tooling (pytest, ruff, R, etc.) must be installed separately. Run `rpx doctor` to check what you need.
