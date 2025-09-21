#!/usr/bin/env python3

import sys
import os
# Add the parent directory to the path so we can import compiler modules
sys.path.insert(0, '/Users/mmoise/Documents/Projects/rpx')

def test_example_files():
    try:
        print("=== Testing RPX Example Files ===")

        # Import parser and transpiler
        from compiler.parser import parse
        from compiler.transpiler import transpile_to_python, transpile_to_r

        # Test the actual simple_loop.rpx file
        print("\n1. Testing examples/simple_loop.rpx...")

        with open('/Users/mmoise/Documents/Projects/rpx/examples/simple_loop.rpx', 'r') as f:
            rpx_code = f.read()

        print(f"RPX source code:\n{rpx_code}")

        print("Parsing...")
        ast = parse(rpx_code)
        print("✓ simple_loop.rpx parsed successfully")

        # Show the AST structure
        print(f"\nAST structure:")
        for func in ast.functions:
            print(f"  Function: {func.name}")
            print(f"  Parameters: {[p.name + ':' + p.type_node.name for p in func.params]}")
            print(f"  Return type: {func.return_type.name}")
            print(f"  Body statements: {len(func.body)}")
            for i, stmt in enumerate(func.body):
                print(f"    {i+1}. {type(stmt).__name__}")
                if hasattr(stmt, 'variable') and hasattr(stmt, 'iterable'):
                    # This is a for loop
                    print(f"       For loop: {stmt.variable} in {stmt.iterable}")

        print("\n2. Testing Python transpilation...")
        python_dir = transpile_to_python(ast, output_dir='/Users/mmoise/Documents/Projects/rpx/output')
        print(f"✓ Python code generated at: {python_dir}")

        print("\n3. Testing R transpilation...")
        r_dir = transpile_to_r(ast, output_dir='/Users/mmoise/Documents/Projects/rpx/output')
        print(f"✓ R code generated at: {r_dir}")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_example_files()
    print(f"\nExample file test {'PASSED' if success else 'FAILED'}")