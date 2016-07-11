def strip_arc(f):
    if f[:3] == "arc":
        return "a" + f[3:]
    return f

