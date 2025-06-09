# test_parser.py
import unittest
from compiler.parser import parse

class TestParser(unittest.TestCase):
    def test_simple_app(self):
        code = """
        app MyApp {
            widget MainScreen {
                Button Text
            }
        }
        """
        ast = parse(code)
        self.assertEqual(ast.name, "MyApp")
        self.assertEqual(ast.body[0].name, "MainScreen")

if __name__ == "__main__":
    unittest.main()
