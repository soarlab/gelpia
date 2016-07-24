def strip_arc(f):
    d = {"arccos"  : "acos",
         "arcos"   : "acos",
         "arcsin"  : "asin",
         "arsin"   : "asin",
         "arctan"  : "atan",
         "artan"   : "atan",
         "arccosh" : "acosh",
         "arcosh"  : "acosh",
         "arcsinh" : "asinh",
         "arsinh"  : "asinh",
         "arctanh" : "atanh",
         "artanh"  : "atanh"}
    if f in d.keys():
        return d[f]
    return f

