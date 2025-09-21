#!/usr/bin/env python3

import sys
import os
# Add the parent directory to the path so we can import compiler modules
sys.path.insert(0, '/Users/mmoise/Documents/Projects/rpx')

def test_complex_loops():
    try:
        print("=== Testing Complex For Loop Scenarios ===")

        # Import parser and transpiler
        from compiler.parser import parse
        from compiler.transpiler import transpile_to_python, transpile_to_r

        # Test different range variations
        test_cases = [
            {
                "name": "Range with start and end",
                "code": '''package test_loops

function test_range_start_end(): Integer {
  var sum: Integer = 0;
  for i in range(2, 8) {
    sum = sum + i;
  }
  return sum;
}'''
            },
            {
                "name": "Range with start, end, and step",
                "code": '''package test_loops

function test_range_step(): Integer {
  var sum: Integer = 0;
  for i in range(0, 10, 2) {
    sum = sum + i;
  }
  return sum;
}'''
            },
            {
                "name": "Nested for loops",
                "code": '''package test_loops

function test_nested_loops(): Integer {
  var total: Integer = 0;
  for i in range(3) {
    for j in range(2) {
      total = total + i + j;
    }
  }
  return total;
}'''
            }
        ]

        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. Testing: {test_case['name']}")
            print(f"RPX code:\n{test_case['code']}")

            # Parse
            ast = parse(test_case['code'])
            print("✓ Parsed successfully")

            # Transpile to Python
            python_dir = transpile_to_python(ast, output_dir='/Users/mmoise/Documents/Projects/rpx/output')
            print(f"✓ Python transpilation successful: {python_dir}")

            # Read and display Python code
            with open(f'{python_dir}/core.py', 'r') as f:
                python_code = f.read()
            print(f"Python code:\n{python_code}")

            # Transpile to R
            r_dir = transpile_to_r(ast, output_dir='/Users/mmoise/Documents/Projects/rpx/output')
            print(f"✓ R transpilation successful: {r_dir}")

            # Read and display R code
            with open(f'{r_dir}/R/test_loops.R', 'r') as f:
                r_code = f.read()
            print(f"R code:\n{r_code}")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complex_loops()
    print(f"\nComplex for loop test {'PASSED' if success else 'FAILED'}")