

import sys

try:
    import gelpia_logging as logging
    import color_printing as color
except ModuleNotFoundError:
    sys.path.append("../")
    import gelpia_logging as logging
    import color_printing as color

from expression_walker import walk

logger = logging.make_module_logger(color.blue("simplify"),
                                    logging.HIGH)



def simplify(exp, inputs):
    """ Applies algebraic simplifications to the expression """

    # Constants
    C_OR_V  = {"Const", "Variable"}
    NEG_ONE = ("Integer", "-1")
    ZERO    = ("Integer", "0")
    ONE     = ("Integer", "1")
    TWO     = ("Integer", "2")
    PI      = ("SymbolicConst", "pi")
    TWO_PI  = ("SymbolicConst", "two_pi")
    HALF_PI = ("SymbolicConst", "half_pi")
    EXP1    = ("SymbolicConst", "exp1")

    def _add(work_stack, count, args):
        assert(args[0] == "+")
        assert(len(args) == 3)
        l, r = args[1], args[2]

        # Collapse integer expressions
        if l[0] == "Integer" and r[0] == "Integer":
            logger("Combined integer add")
            work_stack.append((True, count, ("Integer", str(int(l[1])+int(r[1])))))
            return

        # 0 + x -> x
        if l == ZERO:
            logger("Eliminated Zero in add")
            work_stack.append((True, count, r))
            return
        # x + 0 -> x
        if r == ZERO:
            logger("Eliminated Zero in add")
            work_stack.append((True, count, l))
            return

        # x + x:
        # if x==pi      -> two_pi
        # if x==half_pi -> pi
        # else          -> 2*x
        if l == r:
            if l == PI:
                logger("Replaced pi+pi with two_pi")
                work_stack.append((True, count, TWO_PI))
                return
            if l == HALF_PI:
                logger("Replaced half_pi+half_pi with pi")
                work_stack.append((True, count, PI))
                return
            logger("x + x -> 2*x\n\tx = {}", l)
            work_stack.append((True, count, ("*", TWO, l)))
            return

        # (-x) + y:
        #  if x==y -> 0
        #  else    -> y-x
        if l[0] == "neg":
            if l[1] == r:
                logger("(-x) + x -> 0\n\tx = {}", r)
                work_stack.append((True, count, ZERO))
                return
            logger("(-x) + y -> y-x\n\tx = {}\n\ty = {}", l[1], r)
            work_stack.append((True, count, ("-", r, l[1])))
            return
        # x + (-y):
        #  if x==y -> 0
        #  else    -> x-y
        if r[0] == "neg":
            if r[1] == l:
                logger("x + (-x) -> 0\n\tx = {}", l)
                work_stack.append((True, count, ZERO))
                return
            logger("x + (-y) -> x-y\n\tx = {}\n\ty = {}", l, r[1])
            work_stack.append((True, count, ("-", l, r[1])))
            return

        # (x+y) + x -> (2*x)+y
        if l[0] == "+" and l[1] == r:
            logger("(x+y) + x -> (2*x)+y\n\tx = {}\n\ty = {}", r, l[2])
            work_stack.append((True, count,  ("+", ("*", r, TWO), l[2])))
            return
        # (x+y) + y -> (2*y)+x
        if l[0] == "+" and l[2] == r:
            logger("(x+y) + y -> (2*y)+x\n\tx = {}\n\ty = {}", l[1], r)
            work_stack.append((True, count,  ("+", ("*", r, TWO), l[1])))
            return
        # x + (x+y) -> (2*x)+y
        if r[0] == "+" and r[1] == l:
            logger("x + (x+y) -> (2*x)+y\n\tx = {}\n\ty = {}", l, r[2])
            work_stack.append((True, count,  ("+", ("*", l, TWO), r[2])))
            return
        # x + (y+x) -> (2*x)+y
        if r[0] == "+" and r[2] == l:
            logger("x + (y+x) -> (2*x)+y\n\tx = {}\n\ty = {}", l, r[1])
            work_stack.append((True, count,  ("+", ("*", l, TWO), r[1])))
            return

        # (x-y) + x -> (2*x)-y
        if l[0] == "-" and l[1] == r:
            logger("(x-y) + x -> (2*x)-y\n\tx = {}\n\ty = {}", r, l[2])
            work_stack.append((True, count,  ("-", ("*", r, TWO), l[2])))
            return
        # (x-y) + y -> x
        if l[0] == "-" and l[2] == r:
            logger("(x-y) + y -> x\n\tx = {}\n\ty = {}", l[1], r)
            work_stack.append((True, count,  l[1]))
            return
        # x + (x-y) -> (2*x)-y
        if r[0] == "-" and r[1] == l:
            logger("x + (x-y) -> (2*x)-y\n\tx = {}\n\ty = {}", l, r[2])
            work_stack.append((True, count,  ("-", ("*", l, TWO), r[2])))
            return
        # x + (y-x) -> y
        if r[0] == "-" and r[2] == l:
            logger("x + (y-x) -> y\n\tx = {}\n\ty = {}", l, r[1])
            work_stack.append((True, count,  r[1]))
            return

        # x + (n*x) -> (n+1)*x
        if r[0] == "*" and l == r[2]:
            logger("x + (n*x) -> (n+1)*x\n\tx = {}\n\tn = {}", l, r[1])
            if r[1][0] == "Integer":
                work_stack.append((True, count,  ("*", ("Integer", str(int(r[1][1])+1)), l)))
                return
            work_stack.append((True, count,  ("*", ("+", r[1], ONE), l)))
            return
        # x + (x*n) -> (n+1)*x
        if r[0] == "*" and l == r[1]:
            logger("x + (x*n) -> (n+1)*x\n\tx = {}\n\tn = {}", l, r[2])
            if r[2][0] == "Integer":
                work_stack.append((True, count,  ("*", ("Integer", str(int(r[2][1])+1)), l)))
                return
            work_stack.append((True, count,  ("*", ("+", r[2], ONE), l)))
            return
        # (n*x) + x -> (n+1)*x
        if l[0] == "*" and r == l[2]:
            logger("(n*x) + x-> (n+1)*x\n\tx = {}\n\tn = {}", r, l[1])
            if l[1][0] == "Integer":
                work_stack.append((True, count,  ("*", ("Integer", str(int(l[1][1])+1)), r)))
                return
            work_stack.append((True, count,  ("*", ("+", l[1], ONE), r)))
            return
        # (x*n) + x -> (n+1)*x
        if l[0] == "*" and r == l[1]:
            logger("(x*n) + x-> (n+1)*x\n\tx = {}\n\tn = {}", r, l[2])
            if l[2][0] == "Integer":
                work_stack.append((True, count,  ("*", ("Integer", str(int(l[2][1])+1)), r)))
                return
            work_stack.append((True, count,  ("*", ("+", l[2], ONE), r)))
            return

        work_stack.append((True, count, tuple(args)))
        return

    def _sub(work_stack, count, args):
        assert(args[0] == "-")
        assert(len(args) == 3)
        l, r = args[1], args[2]

        # Collapse integer expressions
        if l[0] == "Integer" and r[0] == "Integer":
            logger("Combined integer sub")
            work_stack.append((True, count, ("Integer", str(int(l[1])-int(r[1])))))
            return

        # 0 - x -> -x
        if l == ZERO:
            logger("Eliminated Zero in subtract")
            work_stack.append((True, count, ("neg", r)))
            return
        # x - 0 -> x
        if r == ZERO:
            logger("Eliminated Zero in subtract")
            work_stack.append((True, count, l))
            return

        # x - x -> 0
        if l == r:
            logger("x - x -> 0\n\tx = {}", l)
            work_stack.append((True, count, ZERO))
            return

        # x - (-y):
        #  if x==y -> 2*x
        #  else    -> x+y
        if r[0] == "neg":
            if l == r[1]:
                logger("x - (-x) -> 2*x\n\tx = {}", l)
                work_stack.append((True, count, ("*", TWO, l)))
                return
            logger("x - (-y) -> x+y\n\tx = {}\n\ty = {}", l, r[1])
            work_stack.append((True, count, ("+", l, r[1])))
            return
        # (-x) - y
        #  if x==y -> -(2*x)
        #  else    -> -(x+y)
        if r[0] == "neg":
            if l[1] == r:
                logger("(-x) - x -> -(2*x)\n\tx = {}", r)
                work_stack.append((True, count, ("neg", ("*", TWO, l))))
                return
            logger("(-x) - y -> -(x+y)\n\tx = {}\n\ty = {}", l[1], r)
            work_stack.append((True, count, ("neg", ("+", l[1], r))))
            return

        # x - (x+y) -> -y
        if r[0] == "+" and l == r[1]:
            logger("x - (x+y) -> -y\n\tx = {}\n\ty = {}", l, r[2])
            work_stack.append((True, count, ("neg", r[2])))
            return
        # x - (y+x) -> -y
        if r[0] == "+" and l == r[2]:
            logger("x - (y+x) -> -y\n\tx = {}\n\ty = {}", l, r[1])
            work_stack.append((True, count, ("neg", r[1])))
            return
        # (x+y) - x -> y
        if l[0] == "+" and l[1] == r:
            logger("(x+y) - x -> y\n\tx = {}\n\ty = {}", r, l[2])
            work_stack.append((True, count, l[2]))
            return
        # (x+y) - y -> x
        if l[0] == "+" and l[2] == r:
            logger("(x+y) - y -> x\n\tx = {}\n\ty = {}", l[1], r)
            work_stack.append((True, count, l[1]))
            return

        # x - (x-y) -> y
        if r[0] == "-" and l == r[1]:
            logger("x - (x-y) -> y\n\tx = {}\n\ty = {}", l, r[2])
            work_stack.append((True, count, r[2]))
            return
        # x - (y-x) -> (2*x)-y
        if r[0] == "-" and l == r[2]:
            logger("x - (y-x) -> (2*x)-y\n\tx = {}\n\ty = {}", l, r[1])
            work_stack.append((True, count, ("-", ("*", TWO, l), r[1])))
            return
        # (x-y) - x -> -y
        if l[0] == "-" and l[1] == r:
            logger("(x-y) - x -> -y\n\tx = {}\n\ty = {}", r, l[2])
            work_stack.append((True, count, ("neg", l[2])))
            return
        # (x-y) - y -> x-(2*y)
        if l[0] == "-" and l[2] == r:
            logger("(x-y) - y -> x-(2*y)\n\tx = {}\n\ty = {}", l[1], r)
            work_stack.append((True, count, ("-", l[1], ("*", TWO, r))))
            return

        # x - (n*x) -> (n-1)*x
        if r[0] == "*" and l == r[2]:
            logger("x - (n*x) -> (n-1)*x\n\tx = {}\n\tn = {}", l, r[1])
            if r[1][0] == "Integer":
                work_stack.append((True, count, ("*", ("Integer", str(int(r[1][1])-1)), l)))
                return
            work_stack.append((True, count, ("*", ("-", r[1], ONE), l)))
            return
        # x - (x*n) -> (n-1)*x
        if r[0] == "*" and l == r[1]:
            logger("x - (x*n) -> (n-1)*x\n\tx = {}\n\tn = {}", l, r[2])
            if r[2][0] == "Integer":
                work_stack.append((True, count, ("*", ("Integer", str(int(r[2][1])-1)), l)))
                return
            work_stack.append((True, count, ("*", ("-", r[2], ONE), l)))
            return
        # (n*x) - x -> (n-1)*x
        if l[0] == "*" and r == l[2]:
            logger("(n*x) - x -> (n-1)*x\n\tx = {}\n\tn = {}", r, l[1])
            if l[1][0] == "Integer":
                work_stack.append((True, count, ("*", ("Integer", str(int(l[1][1])-1)), r)))
                return
            work_stack.append((True, count, ("*", ("-", l[1], ONE), r)))
            return
        # (x*n) - x -> (n-1)*x
        if l[0] == "*" and r == l[1]:
            logger("(x*n) - x -> (n-1)*x\n\tx = {}\n\tn = {}", r, l[2])
            if l[2][0] == "Integer":
                work_stack.append((True, count, ("*", ("Integer", str(int(l[2][1])-1)), r)))
                return
            work_stack.append((True, count, ("*", ("-", l[2], ONE), r)))
            return

        work_stack.append((True, count, tuple(args)))
        return

    def _mul(work_stack, count, args):
        assert(args[0] == "*")
        assert(len(args) == 3)
        l, r = args[1], args[2]

        # Collapse integer expressions
        if l[0] == "Integer" and r[0] == "Integer":
            logger("Combined integer mul")
            work_stack.append((True, count, ("Integer", str(int(l[1])*int(r[1])))))
            return

        # 1 * x -> x
        if l == ONE:
            logger("Eliminated One in multiply")
            work_stack.append((True, count, r))
            return
        # x * 1 -> x
        if r == ONE:
            logger("Eliminated One in multiply")
            work_stack.append((True, count, l))
            return

        # (-1) * x -> -x
        if l == NEG_ONE:
            logger("Eliminated Negative One in multiply")
            work_stack.append((True, count, ("neg", r)))
            return
        # x * (-1) -> -x
        if r == NEG_ONE:
            logger("Eliminated Negative One in multiply")
            work_stack.append((True, count, ("neg", l)))
            return

        # x * x -> x^2
        if r == l:
            logger("x * x -> x^2\n\tx = {}\n", r)
            work_stack.append((True, count, ("pow", l, TWO)))
            return

        # (x^n) * x -> x^(n+1)
        if l[0] == "pow" and l[1] == r:
            logger("(x^n) * x -> x^(n+1)\n\tx = {}\n", r)
            work_stack.append((True, count, ("pow", r, ("Integer", str(int(l[2][1])+1)))))
            return
        # x * (x^n) -> x^(n+1)
        if r[0] == "pow" and l == r[1]:
            logger("x * (x^n) -> x^(n+1)\n\tx = {}\n", l)
            work_stack.append((True, count, ("pow", l, ("Integer", str(int(r[2][1])+1)))))
            return
        # (x^n) * (x^m) -> x^(n+m)
        if r[0] == "pow" and l[0] == "pow" and l[1] == r[1]:
            logger("(x^n) * (x^m) -> x^(n+m)\n\tx = {}\n", l[1])
            work_stack.append((True, count, ("pow", l[1], ("Integer", str(int(l[2][1])+int(r[2][1]))))))
            return

        # 2 * x:
        # if x==pi -> two_pi
        # if x==half_pi -> pi
        # else pass
        if l == TWO:
            if r == PI:
                logger("Replaced 2*pi with two_pi")
                work_stack.append((True, count, TWO_PI))
                return
            if r == HALF_PI:
                logger("Replaced 2*half_pi with pi")
                work_stack.append((True, count, PI))
                return
        # x * 2:
        # if x==pi -> two_pi
        # if x==half_pi -> pi
        # else pass
        if r == TWO:
            if l == PI:
                logger("Replaced pi*2 with two_pi")
                work_stack.append((True, count, TWO_PI))
                return
            if l == HALF_PI:
                logger("Replaced half_pi*2 with pi")
                work_stack.append((True, count, PI))
                return

        work_stack.append((True, count, tuple(args)))
        return

    def _pow(work_stack, count, args):
        assert(args[0] in {"pow", "powi"})
        assert(len(args) == 3)
        l, r = args[1], args[2]

        # Collapse integer expressions
        if l[0] == "Integer" and r[0] == "Integer":
            logger("Combined integer pow")
            work_stack.append((True, count, ("Integer", str(int(l[1])**int(r[1])))))
            return

        # x ^ 1 -> x
        if r == ONE:
            logger("Eliminated One in power")
            work_stack.append((True, count, l))
            return

        # abs(x) ^ (2*n) -> x^(2*n)
        if l[0] == "abs" and r[0] == "Integer" and int(r[1])%2==0:
            logger("abs(x) ^ (2*n) -> x^(2*n)\n\tx = {}", l[1])
            work_stack.append((True, count, ("pow", l[1], r)))
            return

        # (-x) ^ (2*n) -> x^(2*n)
        if l[0] == "neg" and r[0] == "Integer" and int(r[1])%2==0:
            logger("(-x) ^ (2*n) -> x^(2*n)\n\tx = {}", l[1])
            work_stack.append((True, count, ("pow", l[1], r)))
            return

        work_stack.append((True, count, tuple(args)))
        return

    def _neg(work_stack, count, args):
        assert(args[0] == "neg")
        assert(len(args) == 2)
        arg = args[1]

        # Collapse integer expressions
        if arg[0] == "Integer":
            logger("Combined integer neg")
            work_stack.append((True, count, ("Integer", str(-int(arg[1])))))
            return

        # -(-x) -> x
        if arg[0] == "neg":
            logger("Eliminated double negative in negative")
            work_stack.append((True, count, arg[1]))
            return

        work_stack.append((True, count, tuple(args)))
        return

    def _abs(work_stack, count, args):
        assert(args[0] == "abs")
        assert(len(args) == 2)
        arg = args[1]

        # Collapse integer expressions
        if arg[0] == "Integer":
            logger("Combined integer abs")
            work_stack.append((True, count, ("Integer", str(abs(int(arg[1]))))))
            return

        # abs(-x)     -> abs(x)
        # abs(abs(x)) -> abs(x)
        if arg[0] == "neg" or arg[0] == "abs":
            logger("Eliminated double abs in abs")
            work_stack.append((True, count, ("abs", arg[1])))
            return

        # abs(x^(2*n)) -> x^2n
        if arg[0] == "pow" and int(arg[2][1])%2 == 0:
            logger("abs(x^(2*n)) -> x^2n\n\tx = {}", arg[1])
            work_stack.append((True, count, arg))
            return

        work_stack.append((True, count, tuple(args)))
        return

    def _cos(work_stack, count, args):
        assert(args[0] ==  "cos")
        assert(len(args) == 2)
        arg = args[0]

        # cos(-x) -> cos(x)
        if arg[0] == "neg":
            logger("cos(-x) -> cos(x)\n\tx = {}", arg[1])
            work_stack.append((True, count, ("cos", arg[1])))
            return

        work_stack.append((True, count, tuple(args)))
        return

    def _cosh(work_stack, count, args):
        assert(args[0] == "cosh")
        assert(len(args) == 2)
        arg = args[1]

        # cosh(-x) -> cosh(x)
        if arg[0] == "neg":
            logger("cosh(-x) -> cosh(x)\n\tx = {}", arg[1])
            work_stack.append((True, count, ("cosh", arg[1])))
            return

        work_stack.append((True, count, ("cosh", arg)))
        return

    def _exp(work_stack, count, args):
        assert(args[0] == "exp")
        assert(len(args) == 2)
        arg = args[1]

        # exp(1) -> exp1
        if arg == ONE:
            logger("replaced exp(1) with exp1")
            work_stack.append((True, count, EXP1))
            return

        work_stack.append((True, count, ("exp", arg)))
        return

    def _variable(work_stack, count, args):
        assert(args[0] == "Variable")
        assert(len(args) == 3)
        val = args[2]

        if val[0] in C_OR_V:
            work_stack.append((True, count, val))
            return

        work_stack.append((True, count, tuple(args[0:2])))
        return

    my_contract_dict = {
        "+":        _add,
        "-":        _sub,
        "*":        _mul,
        "Variable": _variable,
        "abs":      _abs,
        "cos":      _cos,
        "cosh":     _cosh,
        "exp":      _exp,
        "neg":      _neg,
        "pow":      _pow,
        "powi":     _pow,
    }

    exp = walk(dict(), my_contract_dict, exp)

    return exp




def main(argv):
    logging.set_log_filename(None)
    logging.set_log_level(logging.HIGH)
    try:
        from function_to_lexed import function_to_lexed
        from lexed_to_parsed import lexed_to_parsed
        from pass_lift_inputs_and_inline_assigns import lift_inputs_and_inline_assigns
        from pass_utils import get_runmain_input

        data = get_runmain_input(argv)
        logging.set_log_level(logging.NONE)

        tokens = function_to_lexed(data)
        tree = lexed_to_parsed(tokens)
        exp, inputs = lift_inputs_and_inline_assigns(tree)

        logging.set_log_level(logging.HIGH)
        logger("raw: \n{}\n", data)
        exp = simplify(exp, inputs)
        logger("inputs:")
        for name, interval in inputs.items():
            logger("  {} = {}", name, interval)
        logger("expression:")
        logger("  {}", exp)

        return 0

    except KeyboardInterrupt:
        logger(color.green("Goodbye"))
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
