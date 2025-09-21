#!/usr/bin/env python3

# Standalone test for RPX for loops
import sys

# Check if lark is available
try:
    from lark import Lark, Transformer, v_args, Token
    print("✓ Lark is available")
except ImportError:
    print("✗ Lark not available - install with: pip install lark")
    sys.exit(1)

# Simplified RPX grammar for testing
test_grammar = r'''
    ?start: package_definition

    package_definition: "package" NAME function_definition*

    function_definition: "function" NAME "(" ")" ":" type "{" statement* "}"

    type: "Integer" | "String" | "Boolean"

    statement: return_statement | for_statement

    return_statement: "return" expression ";"
    for_statement: "for" NAME "in" function_call "{" statement* "}"

    function_call: NAME "(" [expression_list] ")"
    expression_list: expression ("," expression)*

    ?expression: NAME | NUMBER

    %import common.CNAME -> NAME
    %import common.SIGNED_NUMBER -> NUMBER
    %import common.WS
    %ignore WS
'''

# Test the grammar
try:
    print("Testing grammar compilation...")
    parser = Lark(test_grammar, parser='lalr')
    print("✓ Grammar compiled successfully")

    # Test basic package parsing
    print("Testing basic parsing...")
    basic_code = 'package test function main(): Integer { return 5; }'
    tree = parser.parse(basic_code)
    print("✓ Basic parse successful:", tree)

    # Test for loop parsing
    print("Testing for loop parsing...")
    loop_code = '''package test_loops
    function test(): Integer {
        for i in range(5) {
            return i;
        }
    }'''
    tree = parser.parse(loop_code)
    print("✓ For loop parse successful:", tree)

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()