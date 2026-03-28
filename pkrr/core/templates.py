from __future__ import annotations

import os
from typing import Mapping

from jinja2 import Environment, FileSystemLoader


def _env(template_root: str) -> Environment:
    return Environment(loader=FileSystemLoader(template_root), autoescape=False)


def render_template_dir(template_root: str, dest: str, context: Mapping) -> None:
    env = _env(template_root)
    # Walk template files and render both path names and file contents.
    for root, _dirs, files in os.walk(template_root):
        rel_root = os.path.relpath(root, template_root)
        for fn in files:
            src_rel_path = os.path.join(rel_root, fn) if rel_root != "." else fn
            # Allow templated directories/filenames
            rendered_rel_path = env.from_string(src_rel_path).render(**context)
            if rendered_rel_path.endswith(".j2"):
                rendered_rel_path = rendered_rel_path[:-3]
            out_path = os.path.join(dest, rendered_rel_path)
            os.makedirs(os.path.dirname(out_path), exist_ok=True)

            src_path = os.path.join(root, fn)
            if fn.endswith(".j2"):
                tmpl = env.get_template(src_rel_path)
                rendered = tmpl.render(**context)
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(rendered)
            else:
                with open(src_path, "rb") as sf, open(out_path, "wb") as df:
                    df.write(sf.read())
