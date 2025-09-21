#!/usr/bin/env python3

# Minimal test to isolate the issue
try:
    from lark import Lark
    print("✓ Lark imported")

    # Test a minimal grammar
    minimal_grammar = '''
    ?start: "hello"
    '''

    parser = Lark(minimal_grammar, parser='lalr')
    print("✓ Minimal grammar compiled")

    result = parser.parse("hello")
    print("✓ Minimal parse successful:", result)

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()