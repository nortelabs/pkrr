# main.py
import sys
from .parser import parse
from .transpiler import transpile_to_python, transpile_to_r

def main():
    if len(sys.argv) < 3:
        print("Usage: python -m compiler.main <input.rpx> <target>")
        print("target: python | r")
        sys.exit(1)
    input_file = sys.argv[1]
    target = sys.argv[2]
    try:
        with open(input_file) as f:
            source = f.read()
    except Exception as e:
        print(f"Error reading file {input_file}: {e}")
        sys.exit(1)
    if not source.strip():
        print(f"Input file {input_file} is empty.")
        sys.exit(1)
    try:
        ast = parse(source)
        # print(f"[DEBUG_MAIN] Parsed AST: {repr(ast)}") # Debug print for AST
    except Exception as e:
        print(f"Error parsing {input_file}: {e}")
        sys.exit(1)
    if target == "python":
        output = transpile_to_python(ast)
    elif target == "r":
        output = transpile_to_r(ast)
    else:
        print("Unknown target: ", target)
        sys.exit(1)
    print("--- TRANSPILER OUTPUT (repr) ---")
    print(repr(output))
    print("--- END OUTPUT ---")
    if not output.strip() or output.strip().startswith('#'):
        print("Warning: Transpiler output is empty or only comments.")
    else:
        print(output)

if __name__ == "__main__":
    main()
