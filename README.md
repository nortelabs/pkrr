# RPX - R and Python Package Compiler

RPX is a cross-platform package compiler that generates both R and Python packages from a single codebase. Write once, compile to both languages!

## Features

- **Single Source**: Write mathematical functions once in RPX syntax
- **Dual Output**: Generate both Python and R packages automatically
- **Type Safety**: Strong typing with automatic type mapping between languages
- **Package Structure**: Creates complete, installable packages with proper metadata

## Usage

```bash
# Compile to both R and Python packages
python3 -m compiler.main examples/hello.rpx both

# Compile to Python only
python3 -m compiler.main examples/hello.rpx python

# Compile to R only
python3 -m compiler.main examples/hello.rpx r
```

## RPX Syntax

```rpx
package math_utils

// Function with parameters and types
function add(a: Number, b: Number): Number {
  return a + b;
}

// Function with integer types
function multiply(val1: Integer, val2: Integer): Integer {
    return val1 * val2;
}

// Function returning boolean
function is_greater(x: Number, y: Number): Boolean {
  return x > y;
}

// Function with no parameters
function get_pi(): Number {
    return 3.14159;
}
```

## Supported Types

- `Integer` → Python `int` / R `integer`
- `Number` → Python `float` / R `numeric`
- `String` → Python `str` / R `character`
- `Boolean` → Python `bool` / R `logical`

## Generated Output

### Python Package Structure
```
output/
├── setup.py
└── your_package/
    ├── __init__.py
    └── core.py
```

### R Package Structure
```
output/
└── your_package/
    ├── DESCRIPTION
    ├── NAMESPACE
    └── R/
        └── your_package.R
```

## Installation

```bash
pip3 install lark
```

## Example

See `examples/hello.rpx` for a complete example that generates a mathematical utilities package for both Python and R.