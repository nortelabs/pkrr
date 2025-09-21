#!/usr/bin/env python3

from lark import Lark
from compiler.parser import rpx_grammar, RpxTransformer

def test_grammar():
    print("Testing Lark grammar compilation...")
    try:
        parser = Lark(rpx_grammar, parser='lalr', debug=True)
        print("✓ Grammar compiled successfully")
        return parser
    except Exception as e:
        print(f"✗ Grammar compilation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_simple_parse(parser):
    if not parser:
        return

    print("\nTesting simple parsing...")
    simple_code = 'package test function main(): Integer { return 5; }'
    try:
        tree = parser.parse(simple_code)
        print("✓ Simple parse successful")
        print(f"Parse tree: {tree}")
        return tree
    except Exception as e:
        print(f"✗ Simple parse failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_transform(parser):
    if not parser:
        return

    print("\nTesting with transformer...")
    simple_code = 'package test function main(): Integer { return 5; }'
    try:
        parser_with_transformer = Lark(rpx_grammar, parser='lalr', transformer=RpxTransformer(), debug=True)
        result = parser_with_transformer.parse(simple_code)
        print("✓ Transform successful")
        print(f"AST: {result}")
        return result
    except Exception as e:
        print(f"✗ Transform failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    parser = test_grammar()
    test_simple_parse(parser)
    test_transform(parser)