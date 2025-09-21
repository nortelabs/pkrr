#!/usr/bin/env python3

import sys
import os
# Add the parent directory to the path so we can import compiler modules
sys.path.insert(0, '/Users/mmoise/Documents/Projects/rpx')

def debug_type_parsing():
    try:
        print("=== Debugging Type Parsing ===")

        # Import parser
        from compiler.parser import parse

        # Test the actual simple_loop.rpx file
        rpx_code = '''package simple_loops

function test_modulo(num: Integer): Boolean {
  return num % 2 == 0;
}'''

        print(f"RPX source code:\n{rpx_code}")

        print("Parsing...")
        ast = parse(rpx_code)
        print("✓ Code parsed successfully")

        # Show the function details
        for func in ast.functions:
            print(f"\nFunction: {func.name}")
            print(f"Return type name: '{func.return_type.name}'")
            print(f"Return type object: {func.return_type}")

            # Show parameter types
            for param in func.params:
                print(f"Parameter {param.name}: type name = '{param.type_node.name}', type object = {param.type_node}")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_type_parsing()