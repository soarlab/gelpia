def strip_arc(f):
    d = {"arccos"  : "acos",
         "arcsin"  : "asin",
         "arctan"  : "atan",
         "arccosh" : "acosh",
         "argcosh" : "acosh",
         "arcosh"  : "acosh",
         "arcsinh" : "asinh",
         "argsinh" : "asinh",
         "arsinh"  : "asinh",
         "arctanh" : "atanh",
         "argtanh" : "atanh",
         "artanh"  : "atanh"}
    if f in d.keys():
        return d[f]
    return f

