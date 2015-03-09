import subprocess

def rewrite(fun_name, fun_def):
    '''
    Returns a function usable by GELPIA which is a compiled
    function of fun_def
    '''
    with open(fun_name + ".cc", "w") as out:
        with open("prefix.cc") as p:
            for l in p:
                out.write(l)
        out.write(fun_def)
        out.write("\n}")
        
    subprocess.call(["clang++", "-dynamiclib", "-DFUN_NAME="+fun_name, "-O3", "-std=c++11", "-o", "lib" + fun_name + ".dylib", fun_name + ".cc"])
