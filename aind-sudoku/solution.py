import copy

assignments = []

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def hidden_twins(values):
    """Eliminate values using the hidden twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers
    for unit in unitlist:
        # all boxes with at least two possibilities
        twins = [box for box in unit if len(values[box])>=2]
        # must be two or more boxes with two possibilities
        if len(twins)<2:
            continue
        # search all pairs of boxes
        for i in range(len(twins)-1):
            for j in range(i+1,len(twins)):
                # pair of boxes
                a = twins[i]
                b = twins[j] 
                # sets of values
                v = set(values[a])
                w = set(values[b])
                # get all peers in this unit
                for peer in unit:
                    if peer in [a,b]:
                        continue
                    # get value of peer box
                    x = set(values[peer])
                    # remove values that could exist elsewhere
                    v = v.difference(x)
                    w = w.difference(x)
                if v == w and len(v) == 2:
                    # hidden twins must take these two values
                    vals = ''.join(v)
                    assign_value(values,a,vals)
                    assign_value(values,b,vals)
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins in a unit
    for unit in unitlist:
        # all boxes with exactly two possibilities
        twins = [box for box in unit if len(values[box])==2]
        # must be two or more boxes with two possibilities
        if len(twins)<2:
            continue
        # search all pairs of boxes for value equality
        for i in range(len(twins)-1):
            for j in range(i+1,len(twins)):
                # pair of boxes
                a = twins[i]
                b = twins[j]
                # pair of values
                v = values[a]
                w = values[b]
                # test for equality
                if v == w:
                    # Eliminate the naked twins as possibilities for their peers
                    for peer in unit:
                        if peer in [a,b]:
                            continue
                        # get value of peer box
                        x=values[peer]
                        # don't try to update solved boxes
                        if len(w) == 1:
                            continue
                        # remove twin values from peer possibilities
                        y = x.replace(v[0],'').replace(v[1],'')
                        # update assignments if peer changed
                        if y != x:
                            assign_value(values,peer,y)
    return values

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a+b for a in A for b in B]

# common relations
rows = 'ABCDEFGHI'
cols = '123456789'
boxes = cross(rows,cols)
row_units=[cross(row,cols) for row in rows]
col_units=[cross(rows,col) for col in cols]
square_units = [cross(x,y) for x in ['ABC','DEF','GHI'] for y in ['123','456','789']]
diag_units = [[a+b for a,b in list(zip(rows[:],cols[:]))],[a+b for a,b in list(zip(rows,cols[::-1]))]]
unitlist = row_units + col_units + square_units + diag_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    values = ['123456789' if v=='.' else v for v in grid]
    return dict(zip(cross('ABCDEFGHI','123456789'),values))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return


def eliminate(values):
    """
    Removes resolved values from all peer candidate value lists
    Args:
        values(dict): The sudoku in dictionary form
    """
    for k in values:
        if len(values[k])==1:
            for peer in peers[k]:
                assign_value(values,peer,values[peer].replace(values[k],''))
    return values
    
def only_choice(values):
    """
    Resolves values where only one place for the value exists in a unit
    Args:
        values(dict): The sudoku in dictionary form
    """
    for unit in unitlist:
        for v in '123456789':
            i=0
            for box in unit:
                if v in values[box]:
                    i=1+i
                    k=box
            if i==1:
                assign_value(values,k,v)
    return values

def reduce_puzzle(values):
    """
    Uses all implemented strategies to constrain and resolve values in boxes
    Args:
        values(dict): The sudoku in dictionary form
    """
    # based on the implementation in classroom exercises, with modifications
    stalled=False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)
        values = hidden_twins(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        # fail if puzzle reduces to an illegal state
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    """
    Last resort to advance the puzzle when reduce_puzzle() fails to solve it
    Args:
        values(dict): The sudoku in dictionary form
    """
    # reduce puzzle
    reduced = reduce_puzzle(values)
    # fail if puzzle reduces to an illegal state
    if type(reduced) is bool:
        return False
    # check to see if this puzzle is solved
    unfilled = [box for box in boxes if len(reduced[box])>1]
    if len(unfilled) == 0:
        # return solved puzzle
        return reduced
    # find the box with the least alternatives to branch on
    min_size = min([len(reduced[box]) for box in unfilled])
    minima = [box for box in unfilled if len(reduced[box])==min_size]
    chosen = minima[0]
    alts = reduced[chosen]
    # branch into alternate sudokus for each possible version of the chosen box
    sudokus = [copy.deepcopy(reduced) for alt in alts]
    for alt, sudoku in zip(alts,sudokus):
        sudoku[chosen] = alt
        # recursively reduce and search 
        result = search(sudoku)
        # test for failure and move on to next branch if failed
        if type(result) == bool:
            continue
        # otherwise accept the current branch's guess as truth
        assign_value(sudoku,chosen,alt)
        return result
    # fail if search exhausted all branches
    return False

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    return search(values)

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    #failed test case
    diag_sudoku_grid = '.16.9........57..6........3..9......2......6..8..4........6..........6.....1..94.'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')

