# parser.py
from lark import Lark, Transformer, v_args
from .ast import AppNode, WidgetNode

rpx_grammar = r'''
    start: app
    app: "app" NAME "{" widget+ "}"
    widget: NAME param_list? ("{" widget* "}")?
    param_list: "(" [param ("," param)*] ")"
    param: STRING
    NAME: /[a-zA-Z_][a-zA-Z0-9_]*/
    STRING: /"(\\.|[^\\"])*"/  | /'(\\.|[^\\'])*'/
    %import common.WS
    %ignore WS
'''

class RpxTransformer(Transformer):
    def start(self, items):
        # The 'start' rule has one child (the 'app' node), return it directly.
        # print("[DEBUG] start items:", items)
        return items[0]

    def app(self, items):
        # print("[DEBUG] app items:", items)
        name = items[0]
        widgets = items[1:]
        return AppNode(name, widgets)
    def widget(self, items):
        # print("[DEBUG] widget items:", items)
        name = items[0]
        args = []
        children = []
        for item in items[1:]:
            if isinstance(item, list):
                # Could be param_list or children
                if all(isinstance(x, str) for x in item):
                    args = item
                else:
                    children = item
            elif isinstance(item, WidgetNode):
                children.append(item)
        return WidgetNode(name, args, children)
    def param_list(self, items):
        return items
    def param(self, items):
        # Remove quotes from string
        s = items[0]
        return s[1:-1]

parser = Lark(rpx_grammar, parser="lalr", transformer=RpxTransformer())

def parse(text):
    return parser.parse(text)
