"""simple_loops core functions"""

def test_range() -> int:
    total: int = 0
    for i in range(5):
        total = (total + i)
    return total

