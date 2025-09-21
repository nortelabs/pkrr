"""test_loops core functions"""

def test_nested_loops() -> int:
    total: int = 0
    for i in range(3):
        for j in range(2):
            total = ((total + i) + j)
    return total

