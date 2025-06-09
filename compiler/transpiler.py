# transpiler.py
from .ast import AppNode, WidgetNode

def transpile_to_python(ast, indent=0):
    # print(f"[DEBUG_PY] Processing node: {repr(ast)}")
    IND = '    ' * indent
    if isinstance(ast, AppNode):
        out = "import streamlit as st\n"
        # print(f"[DEBUG_PY] AppNode: {str(ast.name)}, Initial out: {repr(out)}")
        for w_idx, w in enumerate(ast.body):
            # print(f"[DEBUG_PY] AppNode child {w_idx}: {repr(w)}")
            child_out = transpile_to_python(w, indent)
            # print(f"[DEBUG_PY] AppNode child {w_idx} output: {repr(child_out)}")
            out += child_out
        # print(f"[DEBUG_PY] AppNode final out: {repr(out)}")
        return out
    if isinstance(ast, WidgetNode):
        name = str(ast.name)
        # print(f"[DEBUG_PY] WidgetNode: {name}, Args: {ast.args}, Children: {len(ast.children)}")
        if name == "Text" and ast.args:
            # Only handle single string argument for now
            res = f"{IND}st.write(\"{ast.args[0]}\")\n"
            # print(f"[DEBUG_PY] Text widget output: {repr(res)}")
            return res
        else:
            # Handle children recursively (no extra indent for generic containers)
            out = ''
            for c_idx, child in enumerate(ast.children):
                # print(f"[DEBUG_PY] WidgetNode {name} child {c_idx}: {repr(child)}")
                child_out = transpile_to_python(child, indent)
                # print(f"[DEBUG_PY] WidgetNode {name} child {c_idx} output: {repr(child_out)}")
                out += child_out
            # print(f"[DEBUG_PY] WidgetNode {name} final out: {repr(out)}")
            return out
    # print(f"[DEBUG_PY] Unknown node type or unhandled case, returning empty string for: {repr(ast)}")
    return ""

def transpile_to_r(ast):
    # print(f"[DEBUG_R] Processing node: {repr(ast)}")
    if isinstance(ast, AppNode):
        out = f"# R code for app {str(ast.name)}\n"
        # print(f"[DEBUG_R] AppNode: {str(ast.name)}, Initial out: {repr(out)}")
        for w_idx, w in enumerate(ast.body):
            # print(f"[DEBUG_R] AppNode child {w_idx}: {repr(w)}")
            child_out = transpile_to_r(w)
            # print(f"[DEBUG_R] AppNode child {w_idx} output: {repr(child_out)}")
            out += child_out
        # print(f"[DEBUG_R] AppNode final out: {repr(out)}")
        return out
    if isinstance(ast, WidgetNode):
        name = str(ast.name)
        # print(f"[DEBUG_R] WidgetNode: {name}, Args: {ast.args}, Children: {len(ast.children)}")
        res = f"# Widget: {name}\n"
        # Handle children recursively for R as well
        for c_idx, child in enumerate(ast.children):
            # print(f"[DEBUG_R] WidgetNode {name} child {c_idx}: {repr(child)}")
            child_out = transpile_to_r(child)
            # print(f"[DEBUG_R] WidgetNode {name} child {c_idx} output: {repr(child_out)}")
            res += child_out # Concatenate child output, maybe with indent later
        # print(f"[DEBUG_R] WidgetNode {name} final out: {repr(res)}")
        return res
    # print(f"[DEBUG_R] Unknown node type or unhandled case, returning empty string for: {repr(ast)}")
    return ""
