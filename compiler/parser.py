# parser.py
from lark import Lark, Transformer, v_args, Token
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
    ExpressionNode, StatementNode # Import base classes for type hinting
)

rpx_grammar = r'''
    ?start: package_definition

    package_definition: [doc_comment] "package" NAME [package_metadata] [import_statement*] [struct_definition*] function_definition*

    package_metadata: "{" metadata_field* "}"
    metadata_field: NAME ":" STRING ";"

    import_statement: "import" (NAME | import_list) "from" NAME ";"
    import_list: "{" NAME ("," NAME)* "}"

    struct_definition: [doc_comment] "struct" NAME "{" struct_field* "}"
    struct_field: NAME ":" type ";"

    function_definition: [doc_comment] "function" NAME "(" [param_list] ")" ":" type "{" statement* "}"
    param_list: parameter ("," parameter)*
    parameter: NAME ":" type ["=" expression]

    type: basic_type
        | array_type
        | optional_type
        | union_type
        | NAME -> struct_type

    basic_type: "Integer" -> integer_type
              | "Number" -> number_type
              | "String" -> string_type
              | "Boolean" -> boolean_type

    array_type: "Array" "<" type ">"
    optional_type: "Optional" "<" type ">" | type "?"
    union_type: "Union" "<" type ("," type)* ">"

    statement: variable_declaration
             | assignment
             | if_statement
             | for_statement
             | while_statement
             | try_statement
             | switch_statement
             | return_statement
             | break_statement
             | continue_statement
             | throw_statement
             | expression_statement

    variable_declaration: "var" NAME ":" type ["=" expression] ";"
    assignment: (NAME | struct_access) "=" expression ";"
    if_statement: "if" expression "{" statement* "}" ["else" "{" statement* "}"]
    for_statement: "for" NAME "in" expression "{" statement* "}"
    while_statement: "while" expression "{" statement* "}"
    try_statement: "try" "{" statement* "}" catch_clause* ["finally" "{" statement* "}"]
    catch_clause: "catch" "(" NAME ":" NAME ")" "{" statement* "}"
    switch_statement: "switch" expression "{" case_clause* [default_clause] "}"
    case_clause: "case" expression ":" statement*
    default_clause: "default" ":" statement*
    return_statement: "return" expression ";"
    break_statement: "break" ";"
    continue_statement: "continue" ";"
    throw_statement: "throw" expression ";"
    expression_statement: expression ";"

    ?expression: logical_or
    ?logical_or: logical_and (OR_OP logical_and)*
    ?logical_and: comparison (AND_OP comparison)*
    ?comparison: addition (COMP_OP addition)*
    ?addition: multiplication (ADD_OP multiplication)*
    ?multiplication: postfix (MUL_OP postfix)*
    ?postfix: primary (postfix_op)*

    postfix_op: "." NAME -> field_access
              | "[" expression "]" -> array_index
              | "[" [expression] ":" [expression] "]" -> array_slice
              | "." NAME "(" [expression_list] ")" -> method_call

    ?primary: literal
            | array_literal
            | struct_instantiation
            | function_call
            | lambda_expression
            | NAME -> variable_access
            | "(" expression ")"

    function_call: NAME "(" [expression_list] ")"
    struct_instantiation: NAME "{" [field_assignment_list] "}"
    field_assignment_list: field_assignment ("," field_assignment)*
    field_assignment: NAME ":" expression
    lambda_expression: "(" [param_list] ")" "=>" expression

    array_literal: "[" [expression_list] "]"
    expression_list: expression ("," expression)*

    struct_access: expression "." NAME

    literal: SIGNED_NUMBER -> number_literal
           | STRING        -> string_literal
           | "true"        -> true_literal
           | "false"       -> false_literal

    doc_comment: DOC_COMMENT
    DOC_COMMENT: /\/\/\/.*$/

    COMP_OP: ">" | "<" | "==" | "!=" | ">=" | "<="
    ADD_OP: "+" | "-"
    MUL_OP: "*" | "/" | "%"
    AND_OP: "&&"
    OR_OP: "||"

    %import common.CNAME -> NAME
    %import common.SIGNED_NUMBER
    %import common.ESCAPED_STRING -> STRING
    %import common.WS
    %ignore WS
'''

class RpxTransformer(Transformer):
    def NAME(self, token):
        return str(token)

    # Type system
    def basic_type(self, items):
        return items[0]  # Already a TypeNode from specific type methods

    def array_type(self, items):
        element_type = items[0]
        return TypeNode("Array", element_type=element_type)

    def optional_type(self, items):
        if len(items) == 1:  # T? form
            return TypeNode(items[0].name, element_type=items[0].element_type, is_optional=True)
        else:  # Optional<T> form
            return TypeNode("Optional", element_type=items[0])

    def union_type(self, items):
        return TypeNode("Union", union_types=items)

    def struct_type(self, items):
        return TypeNode(str(items[0]))  # Struct name

    def integer_type(self, items):
        return TypeNode("Integer")

    def number_type(self, items):
        return TypeNode("Number")

    def string_type(self, items):
        return TypeNode("String")

    def boolean_type(self, items):
        return TypeNode("Boolean")

    def type(self, items):
        return items[0]

    # Literals
    @v_args(inline=True)
    def number_literal(self, value_token):
        val_str = str(value_token)
        if '.' in val_str or 'e' in val_str.lower():
            return LiteralNode(float(val_str), TypeNode("Number"))
        else:
            return LiteralNode(int(val_str), TypeNode("Integer"))

    @v_args(inline=True)
    def string_literal(self, value_token):
        return LiteralNode(str(value_token)[1:-1], TypeNode("String"))

    def true_literal(self, items):
        return LiteralNode(True, TypeNode("Boolean"))

    def false_literal(self, items):
        return LiteralNode(False, TypeNode("Boolean"))

    def array_literal(self, items):
        if items and len(items) > 0:
            elements = items[0] if isinstance(items[0], list) else []
        else:
            elements = []
        # Infer element type from first element, default to Integer
        element_type = TypeNode("Integer")
        if elements and hasattr(elements[0], 'type_node'):
            element_type = elements[0].type_node
        return ArrayLiteralNode(elements, element_type)

    def expression_list(self, items):
        return items

    # Expressions
    @v_args(inline=True)
    def variable_access(self, name_token):
        return VariableAccessNode(str(name_token))

    def array_access(self, items):
        array_var = VariableAccessNode(str(items[0]))
        index = items[1]
        return ArrayAccessNode(array_var, index)

    def function_call(self, items):
        function_name = str(items[0])
        args = items[1] if len(items) > 1 and items[1] else []
        return FunctionCallNode(function_name, args)

    # Binary operations helper
    def _build_binary_op(self, items):
        if len(items) == 1:
            return items[0]
        left = items[0]
        for i in range(1, len(items), 2):
            operator = str(items[i])
            right = items[i+1]
            left = BinaryOpNode(left, operator, right)
        return left

    logical_or = _build_binary_op
    logical_and = _build_binary_op
    comparison = _build_binary_op
    addition = _build_binary_op
    multiplication = _build_binary_op

    # Statements
    def variable_declaration(self, items):
        name = str(items[0])
        type_node = items[1]
        initial_value = items[2] if len(items) > 2 else None
        return VariableDeclarationNode(name, type_node, initial_value)

    def assignment(self, items):
        target = str(items[0])
        value = items[1]
        return AssignmentNode(target, value)

    def if_statement(self, items):
        condition = items[0]
        then_body = items[1] if isinstance(items[1], list) else [items[1]]
        else_body = items[2] if len(items) > 2 and isinstance(items[2], list) else (
            [items[2]] if len(items) > 2 else []
        )
        return IfStatementNode(condition, then_body, else_body)

    def for_statement(self, items):
        variable = str(items[0])
        iterable = items[1]
        body = items[2:] if len(items) > 2 else []
        return ForStatementNode(variable, iterable, body)

    def return_statement(self, items):
        return ReturnStatementNode(items[0])

    def expression_statement(self, items):
        return ExpressionStatementNode(items[0])

    def statement(self, items):
        return items[0]

    # Functions
    def parameter(self, items):
        name = str(items[0])
        type_node = items[1]
        default_value = items[2] if len(items) > 2 else None
        return ParameterNode(name=name, type_node=type_node, default_value=default_value)

    def param_list(self, items):
        return items

    def function_definition(self, items):
        func_name = str(items[0])
        current_idx = 1

        # Skip None values (when optional param_list is absent)
        while current_idx < len(items) and items[current_idx] is None:
            current_idx += 1

        param_nodes = []
        # Check if the current item is a list of ParameterNode
        if (current_idx < len(items) and isinstance(items[current_idx], list) and
            (not items[current_idx] or isinstance(items[current_idx][0], ParameterNode))):
            param_nodes = items[current_idx]
            current_idx += 1

        # Return type
        if current_idx >= len(items) or not isinstance(items[current_idx], TypeNode):
            raise SyntaxError(f"Expected return type for function {func_name}")
        ret_type_node = items[current_idx]
        current_idx += 1

        # Function body (list of statements)
        body = []
        while current_idx < len(items):
            if isinstance(items[current_idx], (StatementNode, ReturnStatementNode, VariableDeclarationNode,
                                              AssignmentNode, IfStatementNode, ForStatementNode, ExpressionStatementNode)):
                body.append(items[current_idx])
            current_idx += 1

        return FunctionDefinitionNode(name=func_name, params=param_nodes,
                                    return_type=ret_type_node, body=body)

    # New expression nodes
    def struct_access(self, items):
        struct_expr = items[0]
        field_name = str(items[1])
        return StructAccessNode(struct_expr, field_name)

    def struct_instantiation(self, items):
        struct_name = str(items[0])
        field_assignments = items[1] if len(items) > 1 else {}
        return StructInstantiationNode(struct_name, field_assignments)

    def field_assignment_list(self, items):
        return {assignment['field']: assignment['value'] for assignment in items}

    def field_assignment(self, items):
        field_name = str(items[0])
        value = items[1]
        return {'field': field_name, 'value': value}

    def lambda_expression(self, items):
        if len(items) == 1:  # No params
            params = []
            body = items[0]
        else:
            params = items[0] if items[0] else []
            body = items[1]
        return LambdaNode(params, body)

    # Postfix operations
    def postfix(self, items):
        expr = items[0]
        for op in items[1:]:
            if isinstance(op, dict):
                if op['type'] == 'field_access':
                    expr = StructAccessNode(expr, op['field'])
                elif op['type'] == 'array_index':
                    expr = ArrayAccessNode(expr, op['index'])
                elif op['type'] == 'array_slice':
                    expr = ArraySliceNode(expr, op.get('start'), op.get('end'))
                elif op['type'] == 'method_call':
                    if isinstance(expr, VariableAccessNode) and expr.name in ['String']:
                        expr = StringMethodCallNode(expr, op['method'], op['args'])
                    else:
                        expr = ArrayMethodCallNode(expr, op['method'], op['args'])
        return expr

    def field_access(self, items):
        return {'type': 'field_access', 'field': str(items[0])}

    def array_index(self, items):
        return {'type': 'array_index', 'index': items[0]}

    def array_slice(self, items):
        return {
            'type': 'array_slice',
            'start': items[0] if items[0] else None,
            'end': items[1] if len(items) > 1 and items[1] else None
        }

    def method_call(self, items):
        method_name = str(items[0])
        args = items[1] if len(items) > 1 and items[1] else []
        return {'type': 'method_call', 'method': method_name, 'args': args}

    # New statement nodes
    def while_statement(self, items):
        condition = items[0]
        body = items[1:] if len(items) > 1 else []
        return WhileStatementNode(condition, body)

    def break_statement(self, items):
        return BreakStatementNode()

    def continue_statement(self, items):
        return ContinueStatementNode()

    def try_statement(self, items):
        body = []
        catch_clauses = []
        finally_body = []

        current_section = 'body'
        for item in items:
            if isinstance(item, CatchClauseNode):
                catch_clauses.append(item)
            elif isinstance(item, list) and current_section == 'finally':
                finally_body = item
            elif isinstance(item, (StatementNode, ReturnStatementNode)):
                if current_section == 'body':
                    body.append(item)

        return TryStatementNode(body, catch_clauses, finally_body)

    def catch_clause(self, items):
        var_name = str(items[0])
        exception_type = str(items[1])
        body = items[2:] if len(items) > 2 else []
        return CatchClauseNode(exception_type, var_name, body)

    def throw_statement(self, items):
        return ThrowStatementNode(items[0])

    def switch_statement(self, items):
        expression = items[0]
        cases = []
        default_case = []

        for item in items[1:]:
            if isinstance(item, CaseNode):
                cases.append(item)
            elif isinstance(item, list):  # default case
                default_case = item

        return SwitchStatementNode(expression, cases, default_case)

    def case_clause(self, items):
        value = items[0]
        body = items[1:] if len(items) > 1 else []
        return CaseNode(value, body)

    def default_clause(self, items):
        return items  # Just return the statements

    # Import and metadata
    def import_statement(self, items):
        if isinstance(items[0], list):  # import list
            import_items = [str(item) for item in items[0]]
            module_name = str(items[1])
        else:  # single import
            import_items = [str(items[0])]
            module_name = str(items[1])
        return ImportNode(module_name, import_items)

    def import_list(self, items):
        return [str(item) for item in items]

    def package_metadata(self, items):
        metadata = {}
        for field in items:
            metadata[field['key']] = field['value']
        return PackageMetadataNode(**metadata)

    def metadata_field(self, items):
        key = str(items[0])
        value = str(items[1])[1:-1]  # Remove quotes
        return {'key': key, 'value': value}

    # Struct definition
    def struct_definition(self, items):
        doc_comment = None
        name = None
        fields = []

        for item in items:
            if isinstance(item, str) and item.startswith('///'):
                doc_comment = item
            elif isinstance(item, str):
                name = item
            elif isinstance(item, StructFieldNode):
                fields.append(item)

        return StructDefinitionNode(name, fields)

    def struct_field(self, items):
        name = str(items[0])
        type_node = items[1]
        return StructFieldNode(name, type_node)

    # Documentation
    def doc_comment(self, items):
        return str(items[0])[3:].strip()  # Remove /// and whitespace

    # Package
    def package_definition(self, items):
        doc_comment = None
        package_name = None
        metadata = None
        imports = []
        structs = []
        functions = []

        for item in items:
            if isinstance(item, str) and item.startswith('///'):
                doc_comment = item
            elif isinstance(item, str):
                package_name = item
            elif isinstance(item, PackageMetadataNode):
                metadata = item
            elif isinstance(item, ImportNode):
                imports.append(item)
            elif isinstance(item, StructDefinitionNode):
                structs.append(item)
            elif isinstance(item, FunctionDefinitionNode):
                functions.append(item)

        return PackageNode(name=package_name, functions=functions, structs=structs, imports=imports, metadata=metadata)

    def start(self, items):
        return items[0]


def parse(text: str):
    parser = Lark(rpx_grammar, parser='lalr', transformer=RpxTransformer(), debug=False)
    return parser.parse(text)
