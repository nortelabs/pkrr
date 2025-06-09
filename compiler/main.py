# main.py
import sys
from .parser import parse
# from .transpiler import transpile_to_python, transpile_to_r # Temporarily remove transpiler imports

def main():
    if len(sys.argv) < 2: # Changed to 2, as target_language is not used for now
        print("Usage: python -m compiler.main <input_file.rpx>")
        sys.exit(1)

    input_file = sys.argv[1]
    # target = sys.argv[2] # Temporarily remove target

    # if target not in ["python", "r"]:
    #     print(f"Error: Target language '{target}' not supported. Choose 'python' or 'r'.")
    #     sys.exit(1)

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
        # Consider re-raising for more detailed traceback in debug mode
        # import traceback
        # traceback.print_exc()
        sys.exit(1)

    # Transpilation logic removed for now
    # if target == "python":
    #     output = transpile_to_python(ast)
    # elif target == "r":
    #     output = transpile_to_r(ast)
    # else:
    #     print(f"Internal Error: Unknown target language '{target}'")
    #     sys.exit(1)

    # print("--- TRANSPILER OUTPUT (repr) ---")
    # print(repr(output))
    # print("--- END OUTPUT ---")
    
    # if not output or output.strip().startswith("#") and len(output.strip().splitlines()) <=3 :
    #     print("Warning: Transpiler output is empty or only comments.")
    # else:
    #     if target == "python":
    #         print(output) 

if __name__ == "__main__":
    main()
