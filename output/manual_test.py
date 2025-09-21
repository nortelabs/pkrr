#!/usr/bin/env python3

import sys
import os
# Add the parent directory to the path so we can import compiler modules
sys.path.insert(0, '/Users/mmoise/Documents/Projects/rpx')

def manual_test_for_loops():
    try:
        print("=== Manual Testing For Loop Implementation ===")

        # Import parser
        from compiler.parser import parse
        print("✓ Parser imported successfully")

        # Test simple for loop
        simple_loop = '''package simple_loops

function test_range(): Integer {
  var total: Integer = 0;

  for i in range(5) {
    total = total + i;
  }

  return total;
}'''

        print("\n1. Testing simple for loop parsing...")
        ast = parse(simple_loop)
        print("✓ Simple for loop parsed successfully")
        print(f"AST: {ast}")

        # Test transpilation
        from compiler.transpiler import transpile_to_python, transpile_to_r

        print("\n2. Testing Python transpilation...")
        python_code = transpile_to_python(ast)
        print("✓ Python transpilation successful")
        print(f"Python code generated at: {python_code}")

        print("\n3. Testing R transpilation...")
        r_code = transpile_to_r(ast)
        print("✓ R transpilation successful")
        print(f"R code generated at: {r_code}")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = manual_test_for_loops()
    print(f"\nManual for loop test {'PASSED' if success else 'FAILED'}")