# main.py
import sys
import os
from .parser import parse
from .transpiler import transpile_to_python, transpile_to_r

def main():
    if len(sys.argv) < 3:
        print("Usage: python -m compiler.main <input_file.rpx> <target_language>")
        print("Target languages: python, r, both")
        sys.exit(1)

    input_file = sys.argv[1]
    target = sys.argv[2]

    if target not in ["python", "r", "both"]:
        print(f"Error: Target language '{target}' not supported. Choose 'python', 'r', or 'both'.")
        sys.exit(1)

    try:
        with open(input_file, 'r') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    
    print(f"--- SOURCE ---\n{source}\n--- END SOURCE ---")

    try:
        ast = parse(source)
        print("--- PARSED AST ---")
        print(repr(ast))
        print("--- END AST ---")

    except Exception as e:
        print(f"Error parsing {input_file}: {e}")
        # For Lark parsing errors, print more details if available
        if hasattr(e, 'line') and hasattr(e, 'column'):
            print(f"Error at line {e.line}, column {e.column}.")
        if hasattr(e, 'get_context'):
            print(f"Context:\n{e.get_context(source, 20)}") # Show 20 chars of context
        sys.exit(1)

    # Create output directory
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Transpile to target language(s)
    try:
        if target == "python" or target == "both":
            python_pkg_dir = transpile_to_python(ast, output_dir)
            print(f"✓ Python package generated: {python_pkg_dir}")

        if target == "r" or target == "both":
            r_pkg_dir = transpile_to_r(ast, output_dir)
            print(f"✓ R package generated: {r_pkg_dir}")

        print(f"\nPackage generation complete! Check the '{output_dir}' directory.")

    except Exception as e:
        print(f"Error during transpilation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 

if __name__ == "__main__":
    main()
