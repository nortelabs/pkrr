# parser.py
from lark import Lark, Transformer, v_args, Token
from .ast import (
    PackageNode, FunctionDefinitionNode, ParameterNode, TypeNode, 
    ReturnStatementNode, LiteralNode, VariableAccessNode, BinaryOpNode,
    ExpressionNode # Import base class for type hinting if needed
)

rpx_grammar = r'''
    ?start: package_definition

    package_definition: "package" NAME "{" function_definition* "}"

    function_definition: "function" NAME "(" [param_list] ")" ":" type "{" return_statement "}"
    param_list: parameter ("," parameter)*
    parameter: NAME ":" type

    type: "Integer" | "Number" | "String" | "Boolean"

    return_statement: "return" expression ";"

    ?expression: comparison
    ?comparison: addition (COMP_OPERATOR addition)*
    ?addition: multiplication (ADD_OPERATOR multiplication)*
    ?multiplication: primary (MUL_OPERATOR primary)*
    ?primary: literal 
            | NAME -> variable_access
            | "(" expression ")"

    literal: SIGNED_NUMBER -> number_literal
           | STRING        -> string_literal
           | "true"        -> true_literal
           | "false"       -> false_literal

    COMP_OPERATOR: ">" | "<" | "==" | "!=" | ">=" | "<="
    ADD_OPERATOR: "+" | "-"
    MUL_OPERATOR: "*" | "/"

    %import common.CNAME -> NAME
    %import common.SIGNED_NUMBER
    %import common.ESCAPED_STRING -> STRING
    %import common.WS
    %ignore WS
'''

class RpxTransformer(Transformer):
    def NAME(self, token):
        return str(token)

    def type(self, items):
        return TypeNode(str(items[0]))

    @v_args(inline=True)
    def number_literal(self, value_token):
        val_str = str(value_token)
        if '.' in val_str or 'e' in val_str.lower():
            return LiteralNode(float(val_str), TypeNode("Number"))
        else:
            return LiteralNode(int(val_str), TypeNode("Integer"))

    @v_args(inline=True)
    def string_literal(self, value_token):
        return LiteralNode(str(value_token)[1:-1], TypeNode("String")) # Remove quotes

    @v_args(inline=True)
    def true_literal(self, _):
        return LiteralNode(True, TypeNode("Boolean"))

    @v_args(inline=True)
    def false_literal(self, _):
        return LiteralNode(False, TypeNode("Boolean"))

    @v_args(inline=True)
    def variable_access(self, name_token):
        return VariableAccessNode(str(name_token))
    
    # Helper for binary operations
    def _build_binary_op(self, items):
        if len(items) == 1:
            return items[0]
        left = items[0]
        for i in range(1, len(items), 2):
            operator = str(items[i])
            right = items[i+1]
            left = BinaryOpNode(left, operator, right)
        return left

    comparison = _build_binary_op
    addition = _build_binary_op
    multiplication = _build_binary_op

    @v_args(inline=True)
    def return_statement(self, expression):
        return ReturnStatementNode(expression)

    def parameter(self, items):
        return ParameterNode(name=str(items[0]), type_node=items[1])

    def param_list(self, items):
        return items # List of ParameterNode

    def function_definition(self, items):
        # Grammar: "function" NAME "(" [param_list] ")" ":" type "{" return_statement "}"
        # items[0] is NAME (str due to NAME transformer)
        # items[1] can be param_list (a list of ParameterNode) or type (if param_list is absent)
        # items[2] can be type or return_statement
        # items[3] can be return_statement

        func_name = items[0]
        
        current_idx = 1
        param_nodes = []
        # Check if the current item is a list of ParameterNode (result of param_list)
        if current_idx < len(items) and isinstance(items[current_idx], list) and \
           (not items[current_idx] or isinstance(items[current_idx][0], ParameterNode)):
            param_nodes = items[current_idx]
            current_idx += 1
        
        # The next item must be the return type (TypeNode)
        if current_idx >= len(items) or not isinstance(items[current_idx], TypeNode):
            raise SyntaxError(f"Expected return type (TypeNode) for function {func_name}, got {items[current_idx] if current_idx < len(items) else 'nothing'}. Items: {items}")
        ret_type_node = items[current_idx]
        current_idx += 1

        # The next item must be the return statement (ReturnStatementNode)
        if current_idx >= len(items) or not isinstance(items[current_idx], ReturnStatementNode):
            raise SyntaxError(f"Expected return statement (ReturnStatementNode) for function {func_name}, got {items[current_idx] if current_idx < len(items) else 'nothing'}. Items: {items}")
        ret_stmt_node = items[current_idx]
        
        return FunctionDefinitionNode(name=func_name, params=param_nodes, return_type=ret_type_node, body=[ret_stmt_node])

    def package_definition(self, items):
        # Grammar: "package" NAME "{" function_definition* "}"
        # items[0] is NAME (str due to NAME transformer)
        # items[1] is a list of FunctionDefinitionNode (from function_definition*)
        
        package_name = items[0]
        # function_definition* results in a list. If no functions, it's an empty list.
        function_nodes = items[1]
        
        return PackageNode(name=package_name, functions=function_nodes)

    def start(self, items):
        return items[0] # The PackageNode


def parse(text: str):
    parser = Lark(rpx_grammar, parser='lalr', transformer=RpxTransformer(), debug=False)
    return parser.parse(text)
