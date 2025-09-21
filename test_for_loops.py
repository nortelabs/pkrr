#!/usr/bin/env python3

# Test for loop implementation
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_for_loops():
    try:
        print("Testing for loop implementation...")

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

        print("Testing simple for loop parsing...")
        ast = parse(simple_loop)
        print("✓ Simple for loop parsed successfully")
        print(f"AST: {ast}")

        # Test transpilation
        from compiler.transpiler import transpile_to_python, transpile_to_r

        print("\nTesting Python transpilation...")
        python_code = transpile_to_python(ast)
        print("✓ Python transpilation successful")
        print(f"Python code:\n{python_code}")

        print("\nTesting R transpilation...")
        r_code = transpile_to_r(ast)
        print("✓ R transpilation successful")
        print(f"R code:\n{r_code}")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_for_loops()
    print(f"\nFor loop test {'PASSED' if success else 'FAILED'}")