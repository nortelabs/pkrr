# ast.py
# AST node definitions for rpx language

class Node:
    """Base class for all AST nodes."""
    def __repr__(self):
        attrs = {k: v for k, v in self.__dict__.items() if not k.startswith('_') and v is not None}
        return f"{self.__class__.__name__}({', '.join(f'{k}={repr(v)}' for k, v in attrs.items())})"

# Type System Nodes
class TypeNode(Node):
    def __init__(self, name: str, element_type: 'TypeNode' = None, union_types: list['TypeNode'] = None, is_optional: bool = False):
        self.name = name # e.g., "Integer", "Number", "String", "Boolean", "Array"
        self.element_type = element_type # For Array<T>, this is T
        self.union_types = union_types or [] # For Union<A, B>
        self.is_optional = is_optional # For Optional<T> or T?

# Expression Nodes
class ExpressionNode(Node):
    """Base class for all expression nodes."""
    pass

class LiteralNode(ExpressionNode):
    def __init__(self, value, type_node: TypeNode):
        self.value = value # The actual value (e.g., 10, 3.14, "hello", True)
        self.type_node = type_node # TypeNode indicating the literal's type

class VariableAccessNode(ExpressionNode):
    def __init__(self, name: str):
        self.name = name # Name of the variable/parameter being accessed

class BinaryOpNode(ExpressionNode):
    def __init__(self, left: ExpressionNode, operator: str, right: ExpressionNode):
        self.left = left
        self.operator = operator # e.g., "+", "-", "*", "/", ">", "<", "==", "+"
        self.right = right

class ArrayLiteralNode(ExpressionNode):
    def __init__(self, elements: list[ExpressionNode], element_type: TypeNode):
        self.elements = elements
        self.element_type = element_type

class ArrayAccessNode(ExpressionNode):
    def __init__(self, array: ExpressionNode, index: ExpressionNode):
        self.array = array
        self.index = index

class ArrayMethodCallNode(ExpressionNode):
    def __init__(self, array: ExpressionNode, method: str, args: list[ExpressionNode] = None):
        self.array = array
        self.method = method # e.g., "length", "append", "get"
        self.args = args or []

class FunctionCallNode(ExpressionNode):
    def __init__(self, function_name: str, args: list[ExpressionNode] = None):
        self.function_name = function_name
        self.args = args or []

class StructAccessNode(ExpressionNode):
    def __init__(self, struct: ExpressionNode, field: str):
        self.struct = struct
        self.field = field

class StructInstantiationNode(ExpressionNode):
    def __init__(self, struct_name: str, field_values: dict[str, ExpressionNode] = None):
        self.struct_name = struct_name
        self.field_values = field_values or {}

class ArraySliceNode(ExpressionNode):
    def __init__(self, array: ExpressionNode, start: ExpressionNode = None, end: ExpressionNode = None):
        self.array = array
        self.start = start
        self.end = end

class StringMethodCallNode(ExpressionNode):
    def __init__(self, string: ExpressionNode, method: str, args: list[ExpressionNode] = None):
        self.string = string
        self.method = method # e.g., "length", "substring", "replace"
        self.args = args or []

class LambdaNode(ExpressionNode):
    def __init__(self, params: list[ParameterNode], body: ExpressionNode):
        self.params = params
        self.body = body

# Statement Nodes
class StatementNode(Node):
    """Base class for all statement nodes."""
    pass

class ReturnStatementNode(StatementNode):
    def __init__(self, expression: ExpressionNode):
        self.expression = expression

class VariableDeclarationNode(StatementNode):
    def __init__(self, name: str, type_node: TypeNode, initial_value: ExpressionNode = None):
        self.name = name
        self.type_node = type_node
        self.initial_value = initial_value

class AssignmentNode(StatementNode):
    def __init__(self, target: str, value: ExpressionNode):
        self.target = target
        self.value = value

class IfStatementNode(StatementNode):
    def __init__(self, condition: ExpressionNode, then_body: list[StatementNode], else_body: list[StatementNode] = None):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body or []

class ForStatementNode(StatementNode):
    def __init__(self, variable: str, iterable: ExpressionNode, body: list[StatementNode]):
        self.variable = variable
        self.iterable = iterable
        self.body = body

class ExpressionStatementNode(StatementNode):
    def __init__(self, expression: ExpressionNode):
        self.expression = expression

class WhileStatementNode(StatementNode):
    def __init__(self, condition: ExpressionNode, body: list[StatementNode]):
        self.condition = condition
        self.body = body

class BreakStatementNode(StatementNode):
    def __init__(self):
        pass

class ContinueStatementNode(StatementNode):
    def __init__(self):
        pass

class TryStatementNode(StatementNode):
    def __init__(self, body: list[StatementNode], catch_clauses: list['CatchClauseNode'], finally_body: list[StatementNode] = None):
        self.body = body
        self.catch_clauses = catch_clauses
        self.finally_body = finally_body or []

class CatchClauseNode(StatementNode):
    def __init__(self, exception_type: str, variable: str, body: list[StatementNode]):
        self.exception_type = exception_type
        self.variable = variable
        self.body = body

class ThrowStatementNode(StatementNode):
    def __init__(self, expression: ExpressionNode):
        self.expression = expression

class SwitchStatementNode(StatementNode):
    def __init__(self, expression: ExpressionNode, cases: list['CaseNode'], default_case: list[StatementNode] = None):
        self.expression = expression
        self.cases = cases
        self.default_case = default_case or []

class CaseNode(Node):
    def __init__(self, value: ExpressionNode, body: list[StatementNode]):
        self.value = value
        self.body = body

# Definition Nodes
class ParameterNode(Node):
    def __init__(self, name: str, type_node: TypeNode, default_value: ExpressionNode = None):
        self.name = name
        self.type_node = type_node
        self.default_value = default_value

class FunctionDefinitionNode(Node):
    def __init__(self, name: str, params: list[ParameterNode], return_type: TypeNode, body: list[StatementNode], doc_comment: str = None):
        self.name = name
        self.params = params # List of ParameterNode
        self.return_type = return_type # TypeNode
        self.body = body # List of StatementNode
        self.doc_comment = doc_comment # Documentation comment

class StructFieldNode(Node):
    def __init__(self, name: str, type_node: TypeNode):
        self.name = name
        self.type_node = type_node

class StructDefinitionNode(Node):
    def __init__(self, name: str, fields: list[StructFieldNode]):
        self.name = name
        self.fields = fields

class ImportNode(Node):
    def __init__(self, module_name: str, items: list[str] = None):
        self.module_name = module_name
        self.items = items or [] # Empty means import whole module

class PackageMetadataNode(Node):
    def __init__(self, version: str = "0.1.0", description: str = None, author: str = None, license: str = "MIT"):
        self.version = version
        self.description = description
        self.author = author
        self.license = license

class PackageNode(Node):
    def __init__(self, name: str, functions: list[FunctionDefinitionNode], structs: list[StructDefinitionNode] = None,
                 imports: list[ImportNode] = None, metadata: PackageMetadataNode = None):
        self.name = name
        self.functions = functions # List of FunctionDefinitionNode
        self.structs = structs or [] # List of StructDefinitionNode
        self.imports = imports or [] # List of ImportNode
        self.metadata = metadata or PackageMetadataNode() # Package metadata
