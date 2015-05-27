import subprocess
import rewriter.reader


def rewrite(fun_exp, variables):
    '''
    Returns a function usable by GELPIA which is a compiled
    function of fun_def
    '''
    return rewriter.reader.get_body(fun_exp, variables)
