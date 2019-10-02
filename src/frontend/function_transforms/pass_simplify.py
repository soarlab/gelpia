#!/usr/bin/env python3

import sys

import ian_utils as iu

from expression_walker import walk
from pass_utils import exp_to_str




def simplify(exp, inputs, assigns, consts=None):
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

    def log(func):
        iu.log(3, lambda : iu.cyan("simplify: ") + exp_to_str(func()))

    def _add(work_stack, count, args):
        assert(args[0] == "+")
        assert(len(args) == 3)
        l, r = args[1], args[2]

        # Collapse integer expressions
        if l[0] == "Integer" and r[0] == "Integer":
            log(lambda :"Combined integer add")
            work_stack.append((True, count, ("Integer", str(int(l[1])+int(r[1])))))
            return

        # 0 + x -> x
        if l == ZERO:
            log(lambda :"Eliminated Zero in add")
            work_stack.append((True, count, r))
            return
        # x + 0 -> x
        if r == ZERO:
            log(lambda :"Eliminated Zero in add")
            work_stack.append((True, count, l))
            return

        # x + x:
        # if x==pi      -> two_pi
        # if x==half_pi -> pi
        # else          -> 2*x
        if l == r:
            if l == PI:
                log(lambda :"Replaced pi+pi with two_pi")
                work_stack.append((True, count, TWO_PI))
                return
            if l == HALF_PI:
                log(lambda :"Replaced half_pi+half_pi with pi")
                work_stack.append((True, count, PI))
                return
            log(lambda :"x + x -> 2*x\n\tx = {}".format(l))
            work_stack.append((True, count, ("*", TWO, l)))
            return

        # (-x) + y:
        #  if x==y -> 0
        #  else    -> y-x
        if l[0] == "neg":
            if l[1] == r:
                log(lambda :"(-x) + x -> 0\n\tx = {}".format(r))
                work_stack.append((True, count, ZERO))
                return
            log(lambda :"(-x) + y -> y-x\n\tx = {}\n\ty = {}".format(l[1], r))
            work_stack.append((True, count, ("-", r, l[1])))
            return
        # x + (-y):
        #  if x==y -> 0
        #  else    -> x-y
        if r[0] == "neg":
            if r[1] == l:
                log(lambda :"x + (-x) -> 0\n\tx = {}".format(l))
                work_stack.append((True, count, ZERO))
                return
            log(lambda :"x + (-y) -> x-y\n\tx = {}\n\ty = {}".format(l, r[1]))
            work_stack.append((True, count, ("-", l, r[1])))
            return

        # (x+y) + x -> (2*x)+y
        if l[0] == "+" and l[1] == r:
            log(lambda :"(x+y) + x -> (2*x)+y\n\tx = {}\n\ty = {}".format(r, l[2]))
            work_stack.append((True, count,  ("+", ("*", r, TWO), l[2])))
            return
        # (x+y) + y -> (2*y)+x
        if l[0] == "+" and l[2] == r:
            log(lambda :"(x+y) + y -> (2*y)+x\n\tx = {}\n\ty = {}".format(l[1], r))
            work_stack.append((True, count,  ("+", ("*", r, TWO), l[1])))
            return
        # x + (x+y) -> (2*x)+y
        if r[0] == "+" and r[1] == l:
            log(lambda :"x + (x+y) -> (2*x)+y\n\tx = {}\n\ty = {}".format(l, r[2]))
            work_stack.append((True, count,  ("+", ("*", l, TWO), r[2])))
            return
        # x + (y+x) -> (2*x)+y
        if r[0] == "+" and r[2] == l:
            log(lambda :"x + (y+x) -> (2*x)+y\n\tx = {}\n\ty = {}".format(l, r[1]))
            work_stack.append((True, count,  ("+", ("*", l, TWO), r[1])))
            return

        # (x-y) + x -> (2*x)-y
        if l[0] == "-" and l[1] == r:
            log(lambda :"(x-y) + x -> (2*x)-y\n\tx = {}\n\ty = {}".format(r, l[2]))
            work_stack.append((True, count,  ("-", ("*", r, TWO), l[2])))
            return
        # (x-y) + y -> x
        if l[0] == "-" and l[2] == r:
            log(lambda :"(x-y) + y -> x\n\tx = {}\n\ty = {}".format(l[1], r))
            work_stack.append((True, count,  l[1]))
            return
        # x + (x-y) -> (2*x)-y
        if r[0] == "-" and r[1] == l:
            log(lambda :"x + (x-y) -> (2*x)-y\n\tx = {}\n\ty = {}".format(l, r[2]))
            work_stack.append((True, count,  ("-", ("*", l, TWO), r[2])))
            return
        # x + (y-x) -> y
        if r[0] == "-" and r[2] == l:
            log(lambda :"x + (y-x) -> y\n\tx = {}\n\ty = {}".format(l, r[1]))
            work_stack.append((True, count,  r[1]))
            return

        # x + (n*x) -> (n+1)*x
        if r[0] == "*" and l == r[2]:
            log(lambda :"x + (n*x) -> (n+1)*x\n\tx = {}\n\tn = {}".format(l, r[1]))
            if r[1][0] == "Integer":
                work_stack.append((True, count,  ("*", ("Integer", str(int(r[1][1])+1)), l)))
                return
            work_stack.append((True, count,  ("*", ("+", r[1], ONE), l)))
            return
        # x + (x*n) -> (n+1)*x
        if r[0] == "*" and l == r[1]:
            log(lambda :"x + (x*n) -> (n+1)*x\n\tx = {}\n\tn = {}".format(l, r[2]))
            if r[2][0] == "Integer":
                work_stack.append((True, count,  ("*", ("Integer", str(int(r[2][1])+1)), l)))
                return
            work_stack.append((True, count,  ("*", ("+", r[2], ONE), l)))
            return
        # (n*x) + x -> (n+1)*x
        if l[0] == "*" and r == l[2]:
            log(lambda :"(n*x) + x-> (n+1)*x\n\tx = {}\n\tn = {}".format(r, l[1]))
            if l[1][0] == "Integer":
                work_stack.append((True, count,  ("*", ("Integer", str(int(l[1][1])+1)), r)))
                return
            work_stack.append((True, count,  ("*", ("+", l[1], ONE), r)))
            return
        # (x*n) + x -> (n+1)*x
        if l[0] == "*" and r == l[1]:
            log(lambda :"(x*n) + x-> (n+1)*x\n\tx = {}\n\tn = {}".format(r, l[2]))
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
            log(lambda :"Combined integer sub")
            work_stack.append((True, count, ("Integer", str(int(l[1])-int(r[1])))))
            return

        # 0 - x -> -x
        if l == ZERO:
            log(lambda :"Eliminated Zero in subtract")
            work_stack.append((True, count, ("neg", r)))
            return
        # x - 0 -> x
        if r == ZERO:
            log(lambda :"Eliminated Zero in subtract")
            work_stack.append((True, count, l))
            return

        # x - x -> 0
        if l == r:
            log(lambda :"x - x -> 0\n\tx = {}".format(l))
            work_stack.append((True, count, ZERO))
            return

        # x - (-y):
        #  if x==y -> 2*x
        #  else    -> x+y
        if r[0] == "neg":
            if l == r[1]:
                log(lambda :"x - (-x) -> 2*x\n\tx = {}".format(l))
                work_stack.append((True, count, ("*", TWO, l)))
                return
            log(lambda :"x - (-y) -> x+y\n\tx = {}\n\ty = {}".format(l, r[1]))
            work_stack.append((True, count, ("+", l, r[1])))
            return
        # (-x) - y
        #  if x==y -> -(2*x)
        #  else    -> -(x+y)
        if r[0] == "neg":
            if l[1] == r:
                log(lambda :"(-x) - x -> -(2*x)\n\tx = {}".format(r))
                work_stack.append((True, count, ("neg", ("*", TWO, l))))
                return
            log(lambda :"(-x) - y -> -(x+y)\n\tx = {}\n\ty = {}".format(l[1], r))
            work_stack.append((True, count, ("neg", ("+", l[1], r))))
            return

        # x - (x+y) -> -y
        if r[0] == "+" and l == r[1]:
            log(lambda :"x - (x+y) -> -y\n\tx = {}\n\ty = {}".format(l, r[2]))
            work_stack.append((True, count, ("neg", r[2])))
            return
        # x - (y+x) -> -y
        if r[0] == "+" and l == r[2]:
            log(lambda :"x - (y+x) -> -y\n\tx = {}\n\ty = {}".format(l, r[1]))
            work_stack.append((True, count, ("neg", r[1])))
            return
        # (x+y) - x -> y
        if l[0] == "+" and l[1] == r:
            log(lambda :"(x+y) - x -> y\n\tx = {}\n\ty = {}".format(r, l[2]))
            work_stack.append((True, count, l[2]))
            return
        # (x+y) - y -> x
        if l[0] == "+" and l[2] == r:
            log(lambda :"(x+y) - y -> x\n\tx = {}\n\ty = {}".format(l[1], r))
            work_stack.append((True, count, l[1]))
            return

        # x - (x-y) -> y
        if r[0] == "-" and l == r[1]:
            log(lambda :"x - (x-y) -> y\n\tx = {}\n\ty = {}".format(l, r[2]))
            work_stack.append((True, count, r[2]))
            return
        # x - (y-x) -> (2*x)-y
        if r[0] == "-" and l == r[2]:
            log(lambda :"x - (y-x) -> (2*x)-y\n\tx = {}\n\ty = {}".format(l, r[1]))
            work_stack.append((True, count, ("-", ("*", TWO, l), r[1])))
            return
        # (x-y) - x -> -y
        if l[0] == "-" and l[1] == r:
            log(lambda :"(x-y) - x -> -y\n\tx = {}\n\ty = {}".format(r, l[2]))
            work_stack.append((True, count, ("neg", l[2])))
            return
        # (x-y) - y -> x-(2*y)
        if l[0] == "-" and l[2] == r:
            log(lambda :"(x-y) - y -> x-(2*y)\n\tx = {}\n\ty = {}".format(l[1], r))
            work_stack.append((True, count, ("-", l[1], ("*", TWO, r))))
            return

        # x - (n*x) -> (n-1)*x
        if r[0] == "*" and l == r[2]:
            log(lambda :"x - (n*x) -> (n-1)*x\n\tx = {}\n\tn = {}".format(l, r[1]))
            if r[1][0] == "Integer":
                work_stack.append((True, count, ("*", ("Integer", str(int(r[1][1])-1)), l)))
                return
            work_stack.append((True, count, ("*", ("-", r[1], ONE), l)))
            return
        # x - (x*n) -> (n-1)*x
        if r[0] == "*" and l == r[1]:
            log(lambda :"x - (x*n) -> (n-1)*x\n\tx = {}\n\tn = {}".format(l, r[2]))
            if r[2][0] == "Integer":
                work_stack.append((True, count, ("*", ("Integer", str(int(r[2][1])-1)), l)))
                return
            work_stack.append((True, count, ("*", ("-", r[2], ONE), l)))
            return
        # (n*x) - x -> (n-1)*x
        if l[0] == "*" and r == l[2]:
            log(lambda :"(n*x) - x -> (n-1)*x\n\tx = {}\n\tn = {}".format(r, l[1]))
            if l[1][0] == "Integer":
                work_stack.append((True, count, ("*", ("Integer", str(int(l[1][1])-1)), r)))
                return
            work_stack.append((True, count, ("*", ("-", l[1], ONE), r)))
            return
        # (x*n) - x -> (n-1)*x
        if l[0] == "*" and r == l[1]:
            log(lambda :"(x*n) - x -> (n-1)*x\n\tx = {}\n\tn = {}".format(r, l[2]))
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
            log(lambda :"Combined integer mul")
            work_stack.append((True, count, ("Integer", str(int(l[1])*int(r[1])))))
            return

        # 1 * x -> x
        if l == ONE:
            log(lambda :"Eliminated One in multiply")
            work_stack.append((True, count, r))
            return
        # x * 1 -> x
        if r == ONE:
            log(lambda :"Eliminated One in multiply")
            work_stack.append((True, count, l))
            return

        # (-1) * x -> -x
        if l == NEG_ONE:
            log(lambda :"Eliminated Negative One in multiply")
            work_stack.append((True, count, ("neg", r)))
            return
        # x * (-1) -> -x
        if r == NEG_ONE:
            log(lambda :"Eliminated Negative One in multiply")
            work_stack.append((True, count, ("neg", l)))
            return

        # x * x -> x^2
        if r == l:
            log(lambda :"x * x -> x^2\n\tx = {}\n".format(r))
            work_stack.append((True, count, ("pow", l, TWO)))
            return

        # (x^n) * x -> x^(n+1)
        if l[0] == "pow" and l[1] == r:
            log(lambda :"(x^n) * x -> x^(n+1)\n\tx = {}\n".format(r))
            work_stack.append((True, count, ("pow", r, ("Integer", str(int(l[2][1])+1)))))
            return
        # x * (x^n) -> x^(n+1)
        if r[0] == "pow" and l == r[1]:
            log(lambda :"x * (x^n) -> x^(n+1)\n\tx = {}\n".format(l))
            work_stack.append((True, count, ("pow", l, ("Integer", str(int(r[2][1])+1)))))
            return
        # (x^n) * (x^m) -> x^(n+m)
        if r[0] == "pow" and l[0] == "pow" and l[1] == r[1]:
            log(lambda :"(x^n) * (x^m) -> x^(n+m)\n\tx = {}\n".format(l[1]))
            work_stack.append((True, count, ("pow", l[1], ("Integer", str(int(l[2][1])+int(r[2][1]))))))
            return

        # 2 * x:
        # if x==pi -> two_pi
        # if x==half_pi -> pi
        # else pass
        if l == TWO:
            if r == PI:
                log(lambda :"Replaced 2*pi with two_pi")
                work_stack.append((True, count, TWO_PI))
                return
            if r == HALF_PI:
                log(lambda :"Replaced 2*half_pi with pi")
                work_stack.append((True, count, PI))
                return
        # x * 2:
        # if x==pi -> two_pi
        # if x==half_pi -> pi
        # else pass
        if r == TWO:
            if l == PI:
                log(lambda :"Replaced pi*2 with two_pi")
                work_stack.append((True, count, TWO_PI))
                return
            if l == HALF_PI:
                log(lambda :"Replaced half_pi*2 with pi")
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
            log(lambda :"Combined integer pow")
            work_stack.append((True, count, ("Integer", str(int(l[1])**int(r[1])))))
            return

        # x ^ 1 -> x
        if r == ONE:
            log(lambda :"Eliminated One in power")
            work_stack.append((True, count, l))
            return

        # abs(x) ^ (2*n) -> x^(2*n)
        if l[0] == "abs" and r[0] == "Integer" and int(r[1])%2==0:
            log(lambda :"abs(x) ^ (2*n) -> x^(2*n)\n\tx = {}".format(l[1]))
            work_stack.append((True, count, ("pow", l[1], r)))
            return

        # (-x) ^ (2*n) -> x^(2*n)
        if l[0] == "neg" and r[0] == "Integer" and int(r[1])%2==0:
            log(lambda :"(-x) ^ (2*n) -> x^(2*n)\n\tx = {}".format(l[1]))
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
            log(lambda :"Combined integer neg")
            work_stack.append((True, count, ("Integer", str(-int(arg[1])))))
            return

        # -(-x) -> x
        if arg[0] == "neg":
            log(lambda :"Eliminated double negative in negative")
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
            log(lambda :"Combined integer abs")
            work_stack.append((True, count, ("Integer", str(abs(int(arg[1]))))))
            return

        # abs(-x)     -> abs(x)
        # abs(abs(x)) -> abs(x)
        if arg[0] == "neg" or arg[0] == "abs":
            log(lambda :"Eliminated double abs in abs")
            work_stack.append((True, count, ("abs", arg[1])))
            return

        # abs(x^(2*n)) -> x^2n
        if arg[0] == "pow" and int(arg[2][1])%2 == 0:
            log(lambda :"abs(x^(2*n)) -> x^2n\n\tx = {}".format(arg[1]))
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
            log(lambda :"cos(-x) -> cos(x)\n\tx = {}".format(arg[1]))
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
            log(lambda :"cosh(-x) -> cosh(x)\n\tx = {}".format(arg[1]))
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
            log(lambda :"replaced exp(1) with exp1")
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

    exp = walk(dict(), my_contract_dict, exp, assigns)

    return exp








def main(argv):
    try:
        from lexed_to_parsed import parse_function
        from pass_lift_inputs_and_assigns import lift_inputs_and_assigns
        from pass_utils import get_runmain_input, print_exp
        from pass_utils import print_assigns, print_inputs

        data = get_runmain_input(argv)
        exp = parse_function(data)
        exp, inputs, assigns = lift_inputs_and_assigns(exp)
        iu.set_log_level(100)
        exp = simplify(exp, inputs, assigns)

        print()
        print()
        print_inputs(inputs)
        print()
        print_assigns(assigns)
        print()
        print_exp(exp)

    except KeyboardInterrupt:
        print("\nGoodbye")



if __name__ == "__main__":
    sys.exit(main(sys.argv))
