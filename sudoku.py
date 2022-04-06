import subprocess
from pprint import *
from itertools import *

Grid_1 = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]



def cell_to_variable(i, j, val):
    return  i * 81 + j * 9 + val


def variable_to_cell(var):
    var -= 1 
    return (var //81 % 9, var // 9 % 9, var % 9 + 1)


def at_least_one(vars):
    return vars[:]


def unique(vars):
    return list([vars] + [[-a,-b] for a,b in combinations(vars,2)])


############### CONSTRAINTS CREATION ###############
def create_cell_constraints(n=9):
    return [ item for sublist in [unique( [cell_to_variable(i,j,val) for val in range(1,n+1)] ) for j in range(n)  for i in range(n)] for item in sublist  ]


def create_line_constraints(n=9):
    return [[cell_to_variable(line,col,val) for col in range(n)] for line in range(n) for val in range(1,n+1)]


def create_column_constraints(n=9):
    return [[cell_to_variable(col,line,val) for col in range(n)] for line in range(n) for val in range(1,n+1)]


def create_box_constraints(n=9):           
    return [at_least_one( [cell_to_variable(line + 3*box_x ,col + 3*box_y,val) for line in range(3) for col in range(3)]) for box_x in range(3) for box_y in range(3) for val in range(1,10)]


def create_value_constraints(grid,n=9):
    return [[cell_to_variable(line,col,grid[line][col])] for line in range(n) for col in range(n) if grid[line][col] ]


def generate_problem(grid):
    return create_cell_constraints() + create_line_constraints() + create_column_constraints() + create_box_constraints() + create_value_constraints(grid)


def clauses_to_dimacs(clauses):
    res = "%s %s %s\n" % ('p cnf', '729', str(len(clauses)))
    for clause in clauses:
        sub = ''
        for elt in clause:
            sub = '%s %s' % (sub,elt)
        sub = "%s 0\n" % (sub)
        res = "%s%s" % (res, sub[1:])
    return res


def write_dimacs_file(dimacs: str, filename: str):
    with open(filename, "w", newline="") as cnf:
        cnf.write(dimacs)


def exec_gophersat( filename, cmd = "gophersat", encoding = "utf8" ):
    result = subprocess.run( [cmd, filename], capture_output=True, check=True, encoding=encoding )
    string = str(result.stdout)
    lines = string.splitlines()

    if lines[1] != "s SATISFIABLE":
        return False, []

    model = lines[2][2:].split(" ")

    return True, [int(x) for x in model]


def check_unique_solution_gophersat(filename, cmd="gophersat", encoding = "utf8"):
    result = subprocess.run( [cmd, '-count', filename], capture_output=True, check=True, encoding=encoding )
    string = str(result.stdout)
    lines = string.splitlines()

    res = lines[-1]
    return int(res) == 1


def model_to_grid(model):
    cells =  [variable_to_cell(a) for a in model if a > 0]
    grid_sol = [[0 for x in range(9)] for y in range(9)] 
    for tup in cells:
        grid_sol[tup[0]][tup[1]] = tup[2]
    return grid_sol


def print_grid(grid):
    print('-------------------------------')
    for line in range(9):
        print('|',end='')
        for col in range(9):
            if grid[line][col]:
                print(f" %s " % (grid[line][col]), end= '')
            else:
                print(f" . ", end= '')
            if (col+1)%3 == 0:
                print('|', end='')
        print('')
        if (line+1)%3 == 0 and line < 8:
            print('|---------|---------|---------|')
    print('-------------------------------')


def solve_sudoku(grid):
    print_grid(grid)
    print("               ⇊              ")
    clauses = generate_problem(grid)
    write_dimacs_file(clauses_to_dimacs(clauses),"sudoku.cnf")
    if not(check_unique_solution_gophersat("sudoku.cnf", "/home/romain/Documents/GI02/IA02/TP/TP03/gophersat")):
        print("Warning: Sudoku has multiple solutions.")
    solvable, model = exec_gophersat("sudoku.cnf", "/home/romain/Documents/GI02/IA02/TP/TP03/gophersat")
    if solvable:
        print_grid(model_to_grid(model))
        print("\nSudoku solved !")
    else:
        print("Sudoku grid cannot be solved.")



def main():
    solve_sudoku(Grid_1)
    

if __name__ == "__main__":
    main()
