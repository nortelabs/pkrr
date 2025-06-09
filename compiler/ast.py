# ast.py
# AST node definitions for rpx language

class Node:
    pass

class AppNode(Node):
    def __init__(self, name, body):
        self.name = name
        self.body = body
    def __repr__(self):
        return f"AppNode(name={repr(self.name)}, body={repr(self.body)})"

class WidgetNode(Node):
    def __init__(self, name, args=None, children=None):
        self.name = name
        self.args = args or []
        self.children = children or []
    def __repr__(self):
        return f"WidgetNode(name={repr(self.name)}, args={repr(self.args)}, children={repr(self.children)})"
