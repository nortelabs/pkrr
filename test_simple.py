#!/usr/bin/env python3

# Simple test script to debug parsing issues
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing imports...")
    from compiler.ast import *
    print("✓ AST import successful")

    from lark import Lark, Transformer
    print("✓ Lark import successful")

    from compiler.parser import rpx_grammar, RpxTransformer
    print("✓ Parser imports successful")

    print("\nTesting grammar compilation...")
    parser = Lark(rpx_grammar, parser='lalr')
    print("✓ Grammar compiled successfully")

    print("\nTesting simple parse...")
    simple_code = 'package test function main(): Integer { return 5; }'
    tree = parser.parse(simple_code)
    print("✓ Simple parse successful")
    print(f"Parse tree: {tree}")

    print("\nTesting with transformer...")
    parser_with_transform = Lark(rpx_grammar, parser='lalr', transformer=RpxTransformer())
    result = parser_with_transform.parse(simple_code)
    print("✓ Transform successful")
    print(f"AST result: {result}")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()