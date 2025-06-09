# ast.py
# AST node definitions for rpx language

class Node:
    """Base class for all AST nodes."""
    def __repr__(self):
        attrs = {k: v for k, v in self.__dict__.items() if not k.startswith('_') and v is not None}
        return f"{self.__class__.__name__}({', '.join(f'{k}={repr(v)}' for k, v in attrs.items())})"

# Type System Nodes
class TypeNode(Node):
    def __init__(self, name: str):
        self.name = name # e.g., "Integer", "Number", "String", "Boolean"

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
        self.operator = operator # e.g., "+", "-", "*", "/", ">", "<", "=="
        self.right = right

# Statement Nodes
class StatementNode(Node):
    """Base class for all statement nodes."""
    pass

class ReturnStatementNode(StatementNode):
    def __init__(self, expression: ExpressionNode):
        self.expression = expression

# Definition Nodes
class ParameterNode(Node):
    def __init__(self, name: str, type_node: TypeNode):
        self.name = name
        self.type_node = type_node

class FunctionDefinitionNode(Node):
    def __init__(self, name: str, params: list[ParameterNode], return_type: TypeNode, body: list[StatementNode]):
        self.name = name
        self.params = params # List of ParameterNode
        self.return_type = return_type # TypeNode
        self.body = body # List of StatementNode (for now, just one ReturnStatementNode)

class PackageNode(Node):
    def __init__(self, name: str, functions: list[FunctionDefinitionNode]):
        self.name = name
        self.functions = functions # List of FunctionDefinitionNode
