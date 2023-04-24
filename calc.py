from __future__ import annotations
import operator
import unittest


class Lit:
    def __init__(self, num: int):
        self.num = num

    def add(self, lit: Lit) -> Expr:
        return Expr(self, '+', lit)

    def sub(self, lit: Lit) -> Expr:
        return Expr(self, '-', lit)

    def mul(self, lit: Lit) -> Expr:
        return Expr(self, '*', lit)

    def __repr__(self) -> str:
        return str(self.num)

    def simplify(self) -> Lit:
        return self

    def get_num(self) -> int:
        return self.num


class Var:
    def __init__(self, var: str):
        self.var = var

    def add(self, varOrLit: Lit | Var) -> Expr:
        return Expr(self, '+', varOrLit)

    def __repr__(self) -> str:
        return self.var

    def simplify(self) -> Var:
        return self


class Expr:
    def __init__(self, left: Lit | Var | Expr, operator: str, right: Lit | Var | Expr):
        self.__left = left
        self.__operator = operator
        self.__right = right

    def add(self, expr: Lit | Var | Expr) -> Expr:
        return Expr(self, '+', expr)

    def sub(self, expr: Lit | Var | Expr) -> Expr:
        return Expr(self, '-', expr)

    def mul(self, expr: Lit | Var | Expr) -> Expr:
        return Expr(self, '*', expr)

    def __repr__(self) -> str:
        return f'({self.__left} {self.__operator} {self.__right})'

    def simplify(self) -> Lit | Expr:
        simplified_left = self.__left.simplify()
        simplified_right = self.__right.simplify()

        if isinstance(simplified_left, Lit) and isinstance(simplified_right, Lit):
            if self.__operator == '+':
                return Expr.__operate(simplified_left, operator.add, simplified_right)
            elif self.__operator == '-':
                return Expr.__operate(simplified_left, operator.sub, simplified_right)
            elif self.__operator == '*':
                return Expr.__operate(simplified_left, operator.mul, simplified_right)
            else:
                raise Exception(f'unknown operator {self.__operator}')

        return Expr(simplified_left, self.__operator, simplified_right)

    @staticmethod
    def __operate(left: Lit, operator: Callable[[int, int], int], right: Lit) -> Lit:
        return Lit(operator(left.get_num(), right.get_num()))


class TestingCalc(unittest.TestCase):
    def eq(self, e, before, after):
        self.assertEqual(str(e), before)
        self.assertEqual(str(e.simplify()), after)
        self.assertEqual(str(e), before)

    def testLits(self):
        self.eq(Lit(2), "2", "2")
        self.eq(Lit(-1), "-1", "-1")

    def testAdding(self):
        self.eq(Lit(2).add(Lit(3)), "(2 + 3)", "5")
        self.eq(Lit(1).add(Lit(2)).add(Lit(3)), "((1 + 2) + 3)", "6")

    def testSub(self):
        self.eq(Lit(1).sub(Lit(2)).sub(Lit(3)), "((1 - 2) - 3)", "-4")

    def testMul(self):
        self.eq(Lit(1).mul(Lit(2)).mul(Lit(3)), "((1 * 2) * 3)", "6")

    def testGraph(self):
        x = Lit(4).add(Lit(5))
        self.eq(x.mul(x), "((4 + 5) * (4 + 5))", "81")

    def testVar(self):
        self.eq(Var("x"), "x", "x")
        self.eq(Var("x").add(Var("y")), "(x + y)", "(x + y)")
        self.eq(Var("x").add(Lit(1)), "(x + 1)", "(x + 1)")
        self.eq(Var("x").add(Lit(1).add(Lit(2))), "(x + (1 + 2))", "(x + 3)")
        self.eq(Var("x").add(Lit(1)).add(Lit(2)),
                "((x + 1) + 2)", "((x + 1) + 2)")


if __name__ == '__main__':
    unittest.main()
