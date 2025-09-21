# transpiler.py
import os
from .ast import (
    PackageNode, FunctionDefinitionNode, ParameterNode, TypeNode,
    ReturnStatementNode, LiteralNode, VariableAccessNode, BinaryOpNode,
    ArrayLiteralNode, ArrayAccessNode, ArrayMethodCallNode, FunctionCallNode,
    VariableDeclarationNode, AssignmentNode, IfStatementNode, ForStatementNode,
    ExpressionStatementNode, StructDefinitionNode, StructFieldNode,
    ImportNode, PackageMetadataNode, StructAccessNode, StructInstantiationNode,
    ArraySliceNode, StringMethodCallNode, LambdaNode, WhileStatementNode,
    BreakStatementNode, ContinueStatementNode, TryStatementNode, CatchClauseNode,
    ThrowStatementNode, SwitchStatementNode, CaseNode,
    ExpressionNode, StatementNode
)

# Type mapping from RPX to target languages
RPX_TO_PYTHON_TYPES = {
    "Integer": "int",
    "Number": "float",
    "String": "str",
    "Boolean": "bool",
    "Array": "list"
}

RPX_TO_R_TYPES = {
    "Integer": "integer",
    "Number": "numeric",
    "String": "character",
    "Boolean": "logical",
    "Array": "vector"
}

def get_python_type_hint(type_node: TypeNode) -> str:
    """Convert RPX TypeNode to Python type hint string."""
    if type_node.name == "Array" and type_node.element_type:
        element_type = get_python_type_hint(type_node.element_type)
        return f"list[{element_type}]"
    elif type_node.name == "Optional" and type_node.element_type:
        element_type = get_python_type_hint(type_node.element_type)
        return f"Optional[{element_type}]"
    elif type_node.is_optional:
        base_type = RPX_TO_PYTHON_TYPES.get(type_node.name, type_node.name)
        return f"Optional[{base_type}]"
    elif type_node.name == "Union" and type_node.union_types:
        union_types = [get_python_type_hint(t) for t in type_node.union_types]
        return f"Union[{', '.join(union_types)}]"
    elif type_node.name in RPX_TO_PYTHON_TYPES:
        return RPX_TO_PYTHON_TYPES[type_node.name]
    else:
        # Assume it's a custom struct/class
        return type_node.name

def transpile_expression_to_python(expr: ExpressionNode) -> str:
    """Convert an RPX expression to Python code."""
    if isinstance(expr, LiteralNode):
        if expr.type_node.name == "String":
            return f'"{expr.value}"'
        elif expr.type_node.name == "Boolean":
            return str(expr.value)
        else:
            return str(expr.value)
    elif isinstance(expr, VariableAccessNode):
        return expr.name
    elif isinstance(expr, BinaryOpNode):
        left = transpile_expression_to_python(expr.left)
        right = transpile_expression_to_python(expr.right)
        # Convert logical operators to Python equivalents
        operator = expr.operator
        if operator == "&&":
            operator = "and"
        elif operator == "||":
            operator = "or"
        return f"({left} {operator} {right})"
    elif isinstance(expr, ArrayLiteralNode):
        elements = [transpile_expression_to_python(elem) for elem in expr.elements]
        return f"[{', '.join(elements)}]"
    elif isinstance(expr, ArrayAccessNode):
        array_code = transpile_expression_to_python(expr.array)
        index_code = transpile_expression_to_python(expr.index)
        return f"{array_code}[{index_code}]"
    elif isinstance(expr, ArrayMethodCallNode):
        array_code = transpile_expression_to_python(expr.array)
        if expr.method == "length":
            return f"len({array_code})"
        elif expr.method == "append":
            if expr.args:
                arg_code = transpile_expression_to_python(expr.args[0])
                return f"{array_code}.append({arg_code})"
        return f"{array_code}.{expr.method}()"
    elif isinstance(expr, FunctionCallNode):
        args_code = [transpile_expression_to_python(arg) for arg in expr.args]
        if expr.function_name == "range":
            # Handle range function specially
            if len(args_code) == 1:
                return f"range({args_code[0]})"
            elif len(args_code) == 2:
                return f"range({args_code[0]}, {args_code[1]})"
            elif len(args_code) == 3:
                return f"range({args_code[0]}, {args_code[1]}, {args_code[2]})"
        return f"{expr.function_name}({', '.join(args_code)})"
    elif isinstance(expr, StructAccessNode):
        struct_code = transpile_expression_to_python(expr.struct)
        return f"{struct_code}.{expr.field}"
    elif isinstance(expr, StructInstantiationNode):
        field_assignments = []
        for field, value in expr.field_values.items():
            value_code = transpile_expression_to_python(value)
            field_assignments.append(f"{field}={value_code}")
        return f"{expr.struct_name}({', '.join(field_assignments)})"
    elif isinstance(expr, ArraySliceNode):
        array_code = transpile_expression_to_python(expr.array)
        start_code = transpile_expression_to_python(expr.start) if expr.start else ""
        end_code = transpile_expression_to_python(expr.end) if expr.end else ""
        return f"{array_code}[{start_code}:{end_code}]"
    elif isinstance(expr, StringMethodCallNode):
        string_code = transpile_expression_to_python(expr.string)
        args_code = [transpile_expression_to_python(arg) for arg in expr.args]

        # Map RPX string methods to Python equivalents
        method_map = {
            "length": "len",
            "substring": "__getitem__",
            "replace": "replace",
            "split": "split",
            "upper": "upper",
            "lower": "lower",
            "trim": "strip"
        }

        python_method = method_map.get(expr.method, expr.method)
        if python_method == "len":
            return f"len({string_code})"
        elif python_method == "__getitem__" and len(args_code) == 2:
            return f"{string_code}[{args_code[0]}:{args_code[1]}]"
        else:
            return f"{string_code}.{python_method}({', '.join(args_code)})"
    elif isinstance(expr, LambdaNode):
        param_names = [param.name for param in expr.params]
        body_code = transpile_expression_to_python(expr.body)
        return f"lambda {', '.join(param_names)}: {body_code}"
    else:
        raise ValueError(f"Unknown expression type: {type(expr)}")

def transpile_expression_to_r(expr: ExpressionNode) -> str:
    """Convert an RPX expression to R code."""
    if isinstance(expr, LiteralNode):
        if expr.type_node.name == "String":
            return f'"{expr.value}"'
        elif expr.type_node.name == "Boolean":
            return "TRUE" if expr.value else "FALSE"
        else:
            return str(expr.value)
    elif isinstance(expr, VariableAccessNode):
        return expr.name
    elif isinstance(expr, BinaryOpNode):
        left = transpile_expression_to_r(expr.left)
        right = transpile_expression_to_r(expr.right)
        # Convert logical operators to R equivalents
        operator = expr.operator
        if operator == "&&":
            operator = "&"
        elif operator == "||":
            operator = "|"
        return f"({left} {operator} {right})"
    elif isinstance(expr, ArrayLiteralNode):
        elements = [transpile_expression_to_r(elem) for elem in expr.elements]
        return f"c({', '.join(elements)})"
    elif isinstance(expr, ArrayAccessNode):
        array_code = transpile_expression_to_r(expr.array)
        index_code = transpile_expression_to_r(expr.index)
        return f"{array_code}[{index_code}]"
    elif isinstance(expr, ArrayMethodCallNode):
        array_code = transpile_expression_to_r(expr.array)
        if expr.method == "length":
            return f"length({array_code})"
        elif expr.method == "append":
            if expr.args:
                arg_code = transpile_expression_to_r(expr.args[0])
                return f"c({array_code}, {arg_code})"
        return f"{array_code}${expr.method}()"
    elif isinstance(expr, FunctionCallNode):
        args_code = [transpile_expression_to_r(arg) for arg in expr.args]
        if expr.function_name == "range":
            # Handle range function for R (use seq)
            if len(args_code) == 1:
                return f"1:{args_code[0]}"
            elif len(args_code) == 2:
                return f"{args_code[0]}:{args_code[1]}"
            elif len(args_code) == 3:
                return f"seq({args_code[0]}, {args_code[1]}, by={args_code[2]})"
        return f"{expr.function_name}({', '.join(args_code)})"
    elif isinstance(expr, StructAccessNode):
        struct_code = transpile_expression_to_r(expr.struct)
        return f"{struct_code}${expr.field}"
    elif isinstance(expr, StructInstantiationNode):
        field_assignments = []
        for field, value in expr.field_values.items():
            value_code = transpile_expression_to_r(value)
            field_assignments.append(f"{field} = {value_code}")
        return f"list({', '.join(field_assignments)})"
    elif isinstance(expr, ArraySliceNode):
        array_code = transpile_expression_to_r(expr.array)
        start_code = transpile_expression_to_r(expr.start) if expr.start else "1"
        end_code = transpile_expression_to_r(expr.end) if expr.end else "length({array_code})"
        return f"{array_code}[{start_code}:{end_code}]"
    elif isinstance(expr, StringMethodCallNode):
        string_code = transpile_expression_to_r(expr.string)
        args_code = [transpile_expression_to_r(arg) for arg in expr.args]

        # Map RPX string methods to R equivalents
        method_map = {
            "length": "nchar",
            "substring": "substr",
            "replace": "gsub",
            "split": "strsplit",
            "upper": "toupper",
            "lower": "tolower",
            "trim": "trimws"
        }

        r_method = method_map.get(expr.method, expr.method)
        if r_method == "nchar":
            return f"nchar({string_code})"
        elif r_method == "substr" and len(args_code) == 2:
            return f"substr({string_code}, {args_code[0]}, {args_code[1]})"
        elif r_method == "gsub" and len(args_code) == 2:
            return f"gsub({args_code[0]}, {args_code[1]}, {string_code})"
        else:
            return f"{r_method}({string_code}, {', '.join(args_code)})"
    elif isinstance(expr, LambdaNode):
        param_names = [param.name for param in expr.params]
        body_code = transpile_expression_to_r(expr.body)
        return f"function({', '.join(param_names)}) {body_code}"
    else:
        raise ValueError(f"Unknown expression type: {type(expr)}")

def transpile_statement_to_python(stmt: StatementNode, indent: int = 1) -> str:
    """Convert an RPX statement to Python code."""
    ind = "    " * indent

    if isinstance(stmt, ReturnStatementNode):
        expr_code = transpile_expression_to_python(stmt.expression)
        return f"{ind}return {expr_code}\n"
    elif isinstance(stmt, VariableDeclarationNode):
        type_hint = get_python_type_hint(stmt.type_node)
        if stmt.initial_value:
            init_code = transpile_expression_to_python(stmt.initial_value)
            return f"{ind}{stmt.name}: {type_hint} = {init_code}\n"
        else:
            return f"{ind}{stmt.name}: {type_hint}\n"
    elif isinstance(stmt, AssignmentNode):
        value_code = transpile_expression_to_python(stmt.value)
        return f"{ind}{stmt.target} = {value_code}\n"
    elif isinstance(stmt, IfStatementNode):
        condition_code = transpile_expression_to_python(stmt.condition)
        result = f"{ind}if {condition_code}:\n"
        for then_stmt in stmt.then_body:
            result += transpile_statement_to_python(then_stmt, indent + 1)
        if stmt.else_body:
            result += f"{ind}else:\n"
            for else_stmt in stmt.else_body:
                result += transpile_statement_to_python(else_stmt, indent + 1)
        return result
    elif isinstance(stmt, ForStatementNode):
        iterable_code = transpile_expression_to_python(stmt.iterable)
        result = f"{ind}for {stmt.variable} in {iterable_code}:\n"
        for body_stmt in stmt.body:
            result += transpile_statement_to_python(body_stmt, indent + 1)
        return result
    elif isinstance(stmt, ExpressionStatementNode):
        expr_code = transpile_expression_to_python(stmt.expression)
        return f"{ind}{expr_code}\n"
    elif isinstance(stmt, WhileStatementNode):
        condition_code = transpile_expression_to_python(stmt.condition)
        result = f"{ind}while {condition_code}:\n"
        for body_stmt in stmt.body:
            result += transpile_statement_to_python(body_stmt, indent + 1)
        return result
    elif isinstance(stmt, BreakStatementNode):
        return f"{ind}break\n"
    elif isinstance(stmt, ContinueStatementNode):
        return f"{ind}continue\n"
    elif isinstance(stmt, TryStatementNode):
        result = f"{ind}try:\n"
        for body_stmt in stmt.body:
            result += transpile_statement_to_python(body_stmt, indent + 1)
        for catch_clause in stmt.catch_clauses:
            result += f"{ind}except {catch_clause.exception_type} as {catch_clause.variable}:\n"
            for catch_stmt in catch_clause.body:
                result += transpile_statement_to_python(catch_stmt, indent + 1)
        if stmt.finally_body:
            result += f"{ind}finally:\n"
            for finally_stmt in stmt.finally_body:
                result += transpile_statement_to_python(finally_stmt, indent + 1)
        return result
    elif isinstance(stmt, ThrowStatementNode):
        expr_code = transpile_expression_to_python(stmt.expression)
        return f"{ind}raise {expr_code}\n"
    elif isinstance(stmt, SwitchStatementNode):
        # Python doesn't have switch, so use if/elif chain
        expr_code = transpile_expression_to_python(stmt.expression)
        result = f"{ind}_switch_var = {expr_code}\n"

        for i, case in enumerate(stmt.cases):
            case_value = transpile_expression_to_python(case.value)
            if i == 0:
                result += f"{ind}if _switch_var == {case_value}:\n"
            else:
                result += f"{ind}elif _switch_var == {case_value}:\n"
            for case_stmt in case.body:
                result += transpile_statement_to_python(case_stmt, indent + 1)

        if stmt.default_case:
            result += f"{ind}else:\n"
            for default_stmt in stmt.default_case:
                result += transpile_statement_to_python(default_stmt, indent + 1)
        return result
    else:
        raise ValueError(f"Unknown statement type: {type(stmt)}")

def transpile_statement_to_r(stmt: StatementNode, indent: int = 1) -> str:
    """Convert an RPX statement to R code."""
    ind = "  " * indent

    if isinstance(stmt, ReturnStatementNode):
        expr_code = transpile_expression_to_r(stmt.expression)
        return f"{ind}return({expr_code})\n"
    elif isinstance(stmt, VariableDeclarationNode):
        if stmt.initial_value:
            init_code = transpile_expression_to_r(stmt.initial_value)
            return f"{ind}{stmt.name} <- {init_code}\n"
        else:
            return f"{ind}{stmt.name} <- NULL\n"
    elif isinstance(stmt, AssignmentNode):
        value_code = transpile_expression_to_r(stmt.value)
        return f"{ind}{stmt.target} <- {value_code}\n"
    elif isinstance(stmt, IfStatementNode):
        condition_code = transpile_expression_to_r(stmt.condition)
        result = f"{ind}if ({condition_code}) {{\n"
        for then_stmt in stmt.then_body:
            result += transpile_statement_to_r(then_stmt, indent + 1)
        if stmt.else_body:
            result += f"{ind}}} else {{\n"
            for else_stmt in stmt.else_body:
                result += transpile_statement_to_r(else_stmt, indent + 1)
        result += f"{ind}}}\n"
        return result
    elif isinstance(stmt, ForStatementNode):
        iterable_code = transpile_expression_to_r(stmt.iterable)
        result = f"{ind}for ({stmt.variable} in {iterable_code}) {{\n"
        for body_stmt in stmt.body:
            result += transpile_statement_to_r(body_stmt, indent + 1)
        result += f"{ind}}}\n"
        return result
    elif isinstance(stmt, ExpressionStatementNode):
        expr_code = transpile_expression_to_r(stmt.expression)
        return f"{ind}{expr_code}\n"
    elif isinstance(stmt, WhileStatementNode):
        condition_code = transpile_expression_to_r(stmt.condition)
        result = f"{ind}while ({condition_code}) {{\n"
        for body_stmt in stmt.body:
            result += transpile_statement_to_r(body_stmt, indent + 1)
        result += f"{ind}}}\n"
        return result
    elif isinstance(stmt, BreakStatementNode):
        return f"{ind}break\n"
    elif isinstance(stmt, ContinueStatementNode):
        return f"{ind}next\n"
    elif isinstance(stmt, TryStatementNode):
        # R uses tryCatch
        result = f"{ind}tryCatch({{\n"
        for body_stmt in stmt.body:
            result += transpile_statement_to_r(body_stmt, indent + 1)
        result += f"{ind}}}"

        if stmt.catch_clauses:
            result += ", error = function(e) {\n"
            for catch_clause in stmt.catch_clauses:
                for catch_stmt in catch_clause.body:
                    result += transpile_statement_to_r(catch_stmt, indent + 1)
            result += f"{ind}}}"
        result += ")\n"
        return result
    elif isinstance(stmt, ThrowStatementNode):
        expr_code = transpile_expression_to_r(stmt.expression)
        return f"{ind}stop({expr_code})\n"
    elif isinstance(stmt, SwitchStatementNode):
        expr_code = transpile_expression_to_r(stmt.expression)
        result = f"{ind}switch({expr_code},\n"

        for case in stmt.cases:
            case_value = transpile_expression_to_r(case.value)
            result += f"{ind}  {case_value} = {{\n"
            for case_stmt in case.body:
                result += transpile_statement_to_r(case_stmt, indent + 2)
            result += f"{ind}  }},\n"

        if stmt.default_case:
            result += f"{ind}  {{\n"
            for default_stmt in stmt.default_case:
                result += transpile_statement_to_r(default_stmt, indent + 2)
            result += f"{ind}  }}\n"

        result += f"{ind})\n"
        return result
    else:
        raise ValueError(f"Unknown statement type: {type(stmt)}")

def transpile_function_to_python(func: FunctionDefinitionNode) -> str:
    """Convert an RPX function to Python code."""
    # Build parameter list with type hints and default values
    params = []
    for param in func.params:
        py_type = get_python_type_hint(param.type_node)
        if param.default_value:
            default_code = transpile_expression_to_python(param.default_value)
            params.append(f"{param.name}: {py_type} = {default_code}")
        else:
            params.append(f"{param.name}: {py_type}")

    param_str = ", ".join(params)
    return_type = get_python_type_hint(func.return_type)

    # Generate function body
    body_str = ""
    for stmt in func.body:
        body_str += transpile_statement_to_python(stmt)

    return f"""def {func.name}({param_str}) -> {return_type}:
{body_str}"""

def transpile_function_to_r(func: FunctionDefinitionNode) -> str:
    """Convert an RPX function to R code with documentation."""
    # Build parameter list with default values
    params = []
    for param in func.params:
        if param.default_value:
            default_code = transpile_expression_to_r(param.default_value)
            params.append(f"{param.name} = {default_code}")
        else:
            params.append(param.name)
    param_str = ", ".join(params)

    # Generate function body
    body_str = ""
    for stmt in func.body:
        body_str += transpile_statement_to_r(stmt)

    # Generate roxygen documentation
    param_docs = "\n".join([f"#' @param {param.name} {RPX_TO_R_TYPES.get(param.type_node.name, 'any')} value" for param in func.params])
    return_doc = f"#' @return {RPX_TO_R_TYPES.get(func.return_type.name, 'any')} value"

    return f'''#' {func.name.replace('_', ' ').title()}
#'
#' Function generated from RPX source code.
#'
{param_docs}
{return_doc}
#' @export
{func.name} <- function({param_str}) {{
{body_str}}}
'''

def transpile_struct_to_python(struct: StructDefinitionNode) -> str:
    """Convert an RPX struct to Python dataclass."""
    fields = []
    for field in struct.fields:
        py_type = get_python_type_hint(field.type_node)
        fields.append(f"    {field.name}: {py_type}")

    fields_str = "\n".join(fields)

    return f"""@dataclass
class {struct.name}:
{fields_str}
"""

def transpile_struct_to_r(struct: StructDefinitionNode) -> str:
    """Convert an RPX struct to R list constructor function."""
    field_names = [field.name for field in struct.fields]
    field_params = ", ".join(field_names)
    field_assignments = []

    for field in struct.fields:
        field_assignments.append(f"  {field.name} = {field.name}")

    assignments_str = ",\n".join(field_assignments)

    return f"""#' Create {struct.name} object
#'
#' Constructor function for {struct.name} data structure.
#' @export
{struct.name} <- function({field_params}) {{
  structure(list(
{assignments_str}
  ), class = "{struct.name}")
}}
"""

# Standard library functions that RPX should provide
STANDARD_LIBRARY_PYTHON = '''
# RPX Standard Library - Python Implementation
import math
import random
import datetime
from typing import List, Optional, Union, Any

def rpx_math_abs(x: Union[int, float]) -> Union[int, float]:
    """Absolute value function."""
    return abs(x)

def rpx_math_sqrt(x: Union[int, float]) -> float:
    """Square root function."""
    return math.sqrt(x)

def rpx_math_pow(base: Union[int, float], exp: Union[int, float]) -> Union[int, float]:
    """Power function."""
    return pow(base, exp)

def rpx_math_sin(x: Union[int, float]) -> float:
    """Sine function."""
    return math.sin(x)

def rpx_math_cos(x: Union[int, float]) -> float:
    """Cosine function."""
    return math.cos(x)

def rpx_math_random() -> float:
    """Random number between 0 and 1."""
    return random.random()

def rpx_string_join(strings: List[str], separator: str = "") -> str:
    """Join strings with separator."""
    return separator.join(strings)

def rpx_array_map(func, array: List[Any]) -> List[Any]:
    """Map function over array."""
    return [func(item) for item in array]

def rpx_array_filter(func, array: List[Any]) -> List[Any]:
    """Filter array by predicate function."""
    return [item for item in array if func(item)]

def rpx_array_reduce(func, array: List[Any], initial: Any = None) -> Any:
    """Reduce array to single value."""
    if initial is not None:
        result = initial
        for item in array:
            result = func(result, item)
        return result
    else:
        result = array[0]
        for item in array[1:]:
            result = func(result, item)
        return result
'''

STANDARD_LIBRARY_R = '''
# RPX Standard Library - R Implementation

#' Absolute value
#' @param x numeric value
#' @return absolute value
#' @export
rpx_math_abs <- function(x) {
  abs(x)
}

#' Square root
#' @param x numeric value
#' @return square root
#' @export
rpx_math_sqrt <- function(x) {
  sqrt(x)
}

#' Power function
#' @param base numeric base
#' @param exp numeric exponent
#' @return base raised to exp
#' @export
rpx_math_pow <- function(base, exp) {
  base^exp
}

#' Sine function
#' @param x numeric value
#' @return sine of x
#' @export
rpx_math_sin <- function(x) {
  sin(x)
}

#' Cosine function
#' @param x numeric value
#' @return cosine of x
#' @export
rpx_math_cos <- function(x) {
  cos(x)
}

#' Random number generator
#' @return random number between 0 and 1
#' @export
rpx_math_random <- function() {
  runif(1)
}

#' Join strings
#' @param strings character vector
#' @param separator character separator
#' @return joined string
#' @export
rpx_string_join <- function(strings, separator = "") {
  paste(strings, collapse = separator)
}

#' Map function over array
#' @param func function to apply
#' @param array vector to map over
#' @return mapped vector
#' @export
rpx_array_map <- function(func, array) {
  sapply(array, func)
}

#' Filter array by predicate
#' @param func predicate function
#' @param array vector to filter
#' @return filtered vector
#' @export
rpx_array_filter <- function(func, array) {
  array[sapply(array, func)]
}

#' Reduce array to single value
#' @param func reduction function
#' @param array vector to reduce
#' @param initial initial value
#' @return reduced value
#' @export
rpx_array_reduce <- function(func, array, initial = NULL) {
  if (!is.null(initial)) {
    Reduce(func, array, init = initial)
  } else {
    Reduce(func, array)
  }
}
'''

def generate_python_package(ast: PackageNode, output_dir: str = "output"):
    """Generate a complete Python package from RPX AST."""
    package_name = ast.name
    package_dir = os.path.join(output_dir, package_name)

    # Create package directory structure
    os.makedirs(package_dir, exist_ok=True)

    # Generate setup.py
    setup_content = f'''from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="{package_name}",
    version="0.1.0",
    author="RPX Generated",
    author_email="your.email@example.com",
    description="Package generated from RPX",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/{package_name}",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Add any dependencies here
    ],
)
'''

    with open(os.path.join(output_dir, "setup.py"), "w") as f:
        f.write(setup_content)

    # Generate __init__.py with function exports
    init_content = f'''"""
{package_name} - Generated from RPX
"""

'''

    # Add function and struct imports
    for func in ast.functions:
        init_content += f"from .core import {func.name}\n"
    for struct in ast.structs:
        init_content += f"from .core import {struct.name}\n"

    # Add __all__ list
    func_names = [func.name for func in ast.functions]
    struct_names = [struct.name for struct in ast.structs]
    all_names = func_names + struct_names
    init_content += f"\n__all__ = {all_names}\n"

    with open(os.path.join(package_dir, "__init__.py"), "w") as f:
        f.write(init_content)

    # Generate core.py with all functions and structs
    core_content = f'"""{package_name} core functions"""\n'
    core_content += "from dataclasses import dataclass\n"
    core_content += "from typing import List, Optional, Union, Any\n\n"

    # Add standard library
    core_content += STANDARD_LIBRARY_PYTHON + "\n\n"

    # Add struct definitions
    for struct in ast.structs:
        core_content += transpile_struct_to_python(struct) + "\n"

    # Add function definitions
    for func in ast.functions:
        core_content += transpile_function_to_python(func) + "\n"

    with open(os.path.join(package_dir, "core.py"), "w") as f:
        f.write(core_content)

    # Generate README.md for the package
    readme_content = f'''# {package_name}

Package generated from RPX source code.

## Installation

```bash
pip install {package_name}
```

## Usage

```python
from {package_name} import {", ".join([func.name for func in ast.functions])}

# Example usage:
{f"result = {ast.functions[0].name}(...)" if ast.functions else "# No functions available"}
```

## Functions

{chr(10).join([f"- `{func.name}({', '.join([f'{p.name}: {RPX_TO_PYTHON_TYPES[p.type_node.name]}' for p in func.params])}) -> {RPX_TO_PYTHON_TYPES[func.return_type.name]}`" for func in ast.functions])}

Generated by [RPX](https://github.com/yourusername/rpx) - R and Python Package Compiler.
'''

    with open(os.path.join(output_dir, "README.md"), "w") as f:
        f.write(readme_content)

    # Generate MANIFEST.in
    manifest_content = '''include README.md
include LICENSE
recursive-exclude * __pycache__
recursive-exclude * *.py[co]
'''

    with open(os.path.join(output_dir, "MANIFEST.in"), "w") as f:
        f.write(manifest_content)

    # Generate pyproject.toml for modern Python packaging
    pyproject_content = f'''[build-system]
requires = ["setuptools>=64", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{package_name}"
version = "0.1.0"
description = "Package generated from RPX source code"
authors = [
    {{name = "Your Name", email = "your.email@example.com"}},
]
license = {{text = "MIT"}}
readme = "README.md"
requires-python = ">=3.8"
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

[project.urls]
Homepage = "https://github.com/yourusername/{package_name}"
Repository = "https://github.com/yourusername/{package_name}"
"Bug Tracker" = "https://github.com/yourusername/{package_name}/issues"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

[tool.black]
line-length = 88
target-version = ['py38']

[tool.isort]
profile = "black"
line_length = 88
'''

    with open(os.path.join(output_dir, "pyproject.toml"), "w") as f:
        f.write(pyproject_content)

    # Generate GitHub Actions workflow for CI/CD
    github_dir = os.path.join(output_dir, ".github", "workflows")
    os.makedirs(github_dir, exist_ok=True)

    ci_workflow = f'''name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.8", "3.9", "3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{{{ matrix.python-version }}}}
      uses: actions/setup-python@v4
      with:
        python-version: ${{{{ matrix.python-version }}}}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pytest black isort mypy
        pip install -e .

    - name: Lint with black
      run: black --check .

    - name: Sort imports with isort
      run: isort --check-only .

    - name: Type check with mypy
      run: mypy {package_name}/

    - name: Test with pytest
      run: pytest tests/

  publish:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"

    - name: Install build tools
      run: |
        python -m pip install --upgrade pip
        pip install build twine

    - name: Build package
      run: python -m build

    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{{{ secrets.PYPI_API_TOKEN }}}}
      run: twine upload dist/*
'''

    with open(os.path.join(github_dir, "ci.yml"), "w") as f:
        f.write(ci_workflow)

    # Generate Makefile for development convenience
    makefile_content = f'''# Makefile for {package_name}
.PHONY: help install dev test lint format clean build upload

help:
	@echo "Available commands:"
	@echo "  install    Install package in development mode"
	@echo "  dev        Install development dependencies"
	@echo "  test       Run tests"
	@echo "  lint       Run linting checks"
	@echo "  format     Format code with black and isort"
	@echo "  clean      Clean build artifacts"
	@echo "  build      Build distribution packages"
	@echo "  upload     Upload to PyPI"

install:
	pip install -e .

dev:
	pip install -e ".[dev]"
	pip install pytest black isort mypy

test:
	pytest tests/

lint:
	black --check .
	isort --check-only .
	mypy {package_name}/

format:
	black .
	isort .

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {{}} +
	find . -name "*.pyc" -delete

build: clean
	python -m build

upload: build
	twine upload dist/*
'''

    with open(os.path.join(output_dir, "Makefile"), "w") as f:
        f.write(makefile_content)

    # Generate basic test structure
    tests_dir = os.path.join(output_dir, "tests")
    os.makedirs(tests_dir, exist_ok=True)

    test_init = '''"""Test package for {package_name}."""
'''
    with open(os.path.join(tests_dir, "__init__.py"), "w") as f:
        f.write(test_init)

    # Generate basic test file
    test_content = f'''"""Tests for {package_name} functions."""
import pytest
from {package_name} import *


def test_package_import():
    """Test that package imports successfully."""
    # Basic import test
    assert True


{chr(10).join([f'''def test_{func.name}():
    """Test {func.name} function."""
    # TODO: Add meaningful tests for {func.name}
    # Example test structure:
    # result = {func.name}({", ".join([f"test_{p.name}" for p in func.params])})
    # assert result == expected_value
    pass''' for func in ast.functions[:3]])}  # Only generate tests for first 3 functions

# Add more comprehensive tests as needed
'''

    with open(os.path.join(tests_dir, f"test_{package_name}.py"), "w") as f:
        f.write(test_content)

    return package_dir

def generate_r_package(ast: PackageNode, output_dir: str = "output"):
    """Generate a complete R package from RPX AST."""
    package_name = ast.name
    package_dir = os.path.join(output_dir, package_name)

    # Create R package directory structure
    os.makedirs(package_dir, exist_ok=True)
    os.makedirs(os.path.join(package_dir, "R"), exist_ok=True)
    os.makedirs(os.path.join(package_dir, "man"), exist_ok=True)

    # Generate DESCRIPTION file
    description_content = f'''Package: {package_name}
Type: Package
Title: Package Generated from RPX
Version: 0.1.0
Date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}
Author: Your Name <your.email@example.com>
Maintainer: Your Name <your.email@example.com>
Description: R package generated from RPX source code. This package provides
    mathematical utility functions that were cross-compiled from RPX language.
License: MIT + file LICENSE
URL: https://github.com/yourusername/{package_name}
BugReports: https://github.com/yourusername/{package_name}/issues
Encoding: UTF-8
RoxygenNote: 7.0.0
'''

    with open(os.path.join(package_dir, "DESCRIPTION"), "w") as f:
        f.write(description_content)

    # Generate NAMESPACE file
    namespace_content = "# Generated by RPX\n\n"
    for func in ast.functions:
        namespace_content += f"export({func.name})\n"
    for struct in ast.structs:
        namespace_content += f"export({struct.name})\n"

    with open(os.path.join(package_dir, "NAMESPACE"), "w") as f:
        f.write(namespace_content)

    # Generate R functions file
    r_content = f"# {package_name} - Generated from RPX\n\n"

    # Add standard library
    r_content += STANDARD_LIBRARY_R + "\n\n"

    # Add struct constructors
    for struct in ast.structs:
        r_content += transpile_struct_to_r(struct) + "\n"

    for func in ast.functions:
        r_content += transpile_function_to_r(func) + "\n"

    with open(os.path.join(package_dir, "R", f"{package_name}.R"), "w") as f:
        f.write(r_content)

    return package_dir

def transpile_to_python(ast: PackageNode, output_dir: str = "output"):
    """Generate Python package and return the package directory path."""
    return generate_python_package(ast, output_dir)

def transpile_to_r(ast: PackageNode, output_dir: str = "output"):
    """Generate R package and return the package directory path."""
    return generate_r_package(ast, output_dir)
