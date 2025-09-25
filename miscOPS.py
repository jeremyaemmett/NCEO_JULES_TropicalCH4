def generate_indices(shape):

    if not shape:
        return [()]
    
    rest = generate_indices(shape[1:])
    return [(i,) + r for i in range(shape[0]) for r in rest]


def remove_parenthetical_substrings(s):
    r, skip = [], 0
    for c in s:
        if c=='(': skip+=1; r.append(' ') if skip==1 else None
        elif c==')' and skip>0: skip-=1
        elif skip==0: r.append(c)
    return ''.join(r)