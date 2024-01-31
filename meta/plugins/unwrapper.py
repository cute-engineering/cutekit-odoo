import ast

class Unwrapper(ast.NodeTransformer):
    def visit_Call(self, node):
        node = self.generic_visit(node)

        if isinstance(node.func, ast.Name) and node.func.id == "__call_checker":
            keywords = []
            for i, key in node.keywords[2].value.keys:
                keywords.append(ast.keyword(arg=key, value=node.keywords[2].value.values[i]))

            return ast.Call(
                func=node.keywords[0].value,
                args=node.keywords[1].value.elts,
                keywords=keywords
            )
        
        return node

    def visit_Subscript(self, node):
        node = self.generic_visit(node)

        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == "__SafeWrapper":
            return ast.Subscript(
                value = node.value.keywords[0].value,
                slice = node.slice,
                ctx = node.ctx
            )

        return node

    def visit_Attribute(self, node):
        node = self.generic_visit(node)

        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == "__SafeWrapper":
            return ast.Attribute(
                value = node.value.keywords[0].value,
                attr = node.attr,
                ctx = ast.Load()
            )
        
        return node

def safeEvalUnwrap(code):
    return ast.unparse(Unwrapper().visit(ast.parse(code)))