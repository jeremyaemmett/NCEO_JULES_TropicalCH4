def generate_indices(shape):

    print('shape: ', shape)

    """Given an array shape, generate a list of tuples representing all possible
       combinations of slices through the array.
    Args:
        shape (_type_): Array shape, as a list e.g. [np.int64(12), np.int64(4)]
    Returns:
        list: List of tuples representing slice combinations e.g. [(0, 0), (0, 1), (0, 2), (0, 3), ... (11, 3)]
    """

    if not shape:
        return [()]
    
    rest = generate_indices(shape[1:])

    return [(i,) + r for i in range(shape[0]) for r in rest]


def remove_parenthetical_substrings(string_with_parentheses):

    """Remove all closed parentheses, and anything enclosed by them, from a string.
    Args:
        string_with_parentheses (_type_): A string containing closed parentheses e.g. '(1)one(2)two'
    Returns:
        string: The same string with parentheses and enclosed substrings removed e.g. 'onetwo'
    """
    
    r, skip = [], 0
    for c in string_with_parentheses:
        if c=='(': skip+=1; r.append(' ') if skip==1 else None
        elif c==')' and skip>0: skip-=1
        elif skip==0: r.append(c)

    return ''.join(r)


def keyval2keylabel(keyname, keyval):

    """Given a variable key, convert a dimension on the axis to a descriptive string.
    Args:
        keyname (string): Variable key e.g. 'time'
        keyval (integer): Dimension along the key axis e.g. 2
    Returns:
        (string): A readable/plot-able string e.g. 'Mar'
    """

    if keyname == 'time': labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    if keyname == 'pool': labels = ['DPM', 'RPM', 'Micro. Bio', 'Humus']
    if keyname == 'soil': labels = ['0-0.1 m', '0.1-0.35 m', '0.35-1.0 m', '1.0-2.0 m']
    if keyname == 'pft':  labels = ['pft1', 'pft2', 'pft3', 'pft4', 'pft5', 'pft6', 'pft7', 'pft8', 'pft9', 'pft10', 'pft11', 'pft12', 'pft13']

    key_label = labels[keyval]

    return key_label