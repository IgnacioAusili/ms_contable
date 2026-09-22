from decimal import Decimal
import ast


def preparar_formula(expresion):
    tree = ast.parse(expresion, mode="eval")

    transformador = ReemplazarNumeros()
    tree = transformador.visit(tree)
    ast.fix_missing_locations(tree)

    expresion_transformada = ast.unparse(tree)

    return expresion_transformada, transformador.numeros


class ReemplazarNumeros(ast.NodeTransformer):
    def __init__(self):
        self.numeros = {}

    def visit_Constant(self, node):
        if (
            isinstance(node.value, (int, float))
            and not isinstance(node.value, bool)
        ):
            identificador = f"_numero_{len(self.numeros) + 1}"
            self.numeros[identificador] = Decimal(str(node.value))

            return ast.copy_location(
                ast.Name(id=identificador, ctx=ast.Load()),
                node,
            )

        return node
