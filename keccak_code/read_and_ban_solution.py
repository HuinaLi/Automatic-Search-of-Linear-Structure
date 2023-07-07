import argparse

solution_sign = "s SATISFIABLE"
line_split = "v"
state_x = 5
state_y = 5
lane_z = 64
state = state_x*state_y*lane_z

"""shift symmetry"""
def shiftZ(X: list, r0: int) -> list:
    Y = []
    for y in range(state_y):
        for x in range(state_x):
            for z in range(lane_z):
                # shift (z)
                Y.append(X[lane_z*state_x*y + lane_z*x + (z-r0) % lane_z])
    return Y

def index_(x: int, y: int, z: int) -> int:
    """return the index of coordinates (x, y, z)

    Args:
        x (int): x coordinate
        y (int): y coordinate
        z (int): z coordinate

    Returns:
        int: index of (x, y, z)
    """
    x, y, z = x%5, y%5, z%lane_z
    return lane_z * (5 * y + x) + z

def index_xy(x: int, y: int) -> int:
    """return the index of coordinates x, y

    Args:
        x (int): x coordinate
        y (int): y coordinate

    Returns:
        int: index of x, y
    """
    x, y = x%5, y%5
    return lane_z * (5 * y + x)

def index_xz(x: int, z: int) -> int:
    """return the index of coordinates x, z

    Args:
        x (int): x coordinate
        z (int): z coordinate

    Returns:
        int: index of x, z
    """
    x, z = x%5, z%lane_z
    return lane_z * x + z

"""read solution from solution file"""
def read_sol(sol_path: str, ROUNDS: int, DIGEST: int) -> list:
    # var number of A,B,C,D,G
    var_num = 3*ROUNDS*state + 2*ROUNDS*5*lane_z
    # extract the solution from cnf solution file
    f = open(sol_path, "r")
    contents = f.read()
    # find solution_sign "s SATISFIABLE"
    i = contents.find(solution_sign)
    if i < 0:
        return None

    i += len(solution_sign) + 1
    # get the contents after "s SATISFIABLE"
    lines = contents[i:].split(line_split)
    sol = []
    # get the solution of A,B,C,D,G
    for line in lines:
        vars = line.split()
        for var in vars:
            v = 0 if int(var) < 0 else 1
            sol.append(v)
        if len(sol) >= var_num:
            break
    sol = sol[:var_num]
    print("sol"+ str(sol))
    # return A,B,C
    A = []
    B = []
    C = []
    G = []
    D = []
   # Q = []
    for r in range(ROUNDS):
        A.append(sol[3*r*state : (3*r+1)*state])
        B.append(sol[(3*r+1)*state : (3*r+2)*state])
        C.append(sol[(3*r+2)*state : (3*r+3)*state])
        G.append(sol[3*ROUNDS*state +  5*lane_z*r : 3*ROUNDS*state + (r+1)*5*lane_z])
        D.append(sol[3*ROUNDS*state + ROUNDS*5*lane_z + r*5*lane_z : 3*ROUNDS*state + ROUNDS*5*lane_z + (r+1)*5*lane_z])
        #Q.append(sol[3*ROUNDS*state + 2*ROUNDS*5*lane_z + r*5*lane_z : 3*ROUNDS*state + 2*ROUNDS*5*lane_z + (r+1)*5*lane_z])
    print("---------------------------------------------------")
    print("-------------Keccak-"+str(DIGEST)+"----------------")
    k = 0
    for i in range(state):
        if A[0][i] == 1:
            k += 1
    print("Var_num = " + str(k))

    d = 0
    for r in range(ROUNDS):
        for i in range(5*lane_z):
            if D[r][i] == 1:
                d += 1
    print("D_num = " + str(d))
    print("DF_num = " + str(k-d))

    #q = 0
    #for r in range(ROUNDS):
    #    for i in range(5*lane_z):
    #        if Q[r][i] == 1:
    #            q += 1
    #print("Q_num = " + str(q))
    #print("Complexity = " + str((DIGEST-k+d+q)//2))
    print("---------------------------------------------------")
    for r in range(ROUNDS):
        print("A{}: ".format(r))
        print_xyz_state(A[r])
    
        print("B{}: ".format(r))
        print_xyz_state(B[r])

        print("C{}: ".format(r))
        print_xyz_state(C[r])

        print("G{}: ".format(r))
        print_xz_state(G[r])

        print("D{}: ".format(r))
        print_xz_state(D[r])

        #print("Q{}: ".format(r))
        #print_xz_state(Q[r])

    print("---------------------------------------------------")
    return A

"""get banned solution list"""
def ban_sol(a: list) -> list:
    # shift the solution
    ban_list = []

    for z in range(lane_z):
        ban = []
        for ai in a:
            ban.append(shiftZ(ai, z))
        ban_list.append(ban)
    # we got 64 solutions to ban
    return ban_list

"""add ban solution list to cnf"""
def add_ban2cnf(cnf_path: str, ban_list: list) -> None:
    # add 64 ban solutions to cnf
    # line_cnt = 64
    line_cnt = len(ban_list)

    # ban cnf string
    ban_cnf = ""
    # add each solution
    for ban in ban_list:
        # each solution is A0,A1..
        for r in range(len(ban)):
            ai = ban[r]
            # the first index of ai in cnf
            # a0: 1 - 1600
            # a2: 1600*3+1 - 1600*4
            # ar: 1600*3*r+1 - 1600*(3*r+1)
            offset = 3*r*state + 1
            for i in range(len(ai)):
                v = ai[i]
                if v:
                    ban_cnf += "-" + str(i + offset) + " "
                else:
                    ban_cnf += str(i + offset) + " "
        ban_cnf += "0\n"
    # read previous cnf
    f = open(cnf_path, "r")
    pre_cnf = f.read()
    f.close()
    # find the first line
    index_1st = pre_cnf.find("\n")
    line_1st = pre_cnf[:index_1st + 1].split()
    # modify first line
    line_1st[3] = str(int(line_1st[3]) + line_cnt)
    line_1st = " ".join(line_1st) + "\n"
    new_cnf = line_1st + pre_cnf[index_1st + 1:] + ban_cnf
    # write ban to cnf
    f = open(cnf_path, "w")
    f.write(new_cnf)
    f.close()

def print_xyz_state(X: list) -> None:
    """print a state in column form

    Args:
        X (list): input state
    """
    # print 5*64 columns
    for z in range(lane_z):
        
        lane_print = ""
        for y in range(state_y):
            # now start convert binary column to int
            # get the binary column
            for x in range(state_x):
                lane_print += str(X[index_(x,y,z)]) if X[index_(x,y,z)] else "0"
        print(lane_print)
    print("------")

def print_xz_state(X: list) -> None:
    """print a state in column form

    Args:
        X (list): input state
    """
    # print 5*64 columns
    for z in range(lane_z):
        
        lane_print = ""
        for x in range(state_x):
            lane_print += str(X[index_xz(x,z)]) if X[index_xz(x,z)] else "0"
        print(lane_print)
    print("------")

if __name__ == "__main__":
    parse = argparse.ArgumentParser(description="add banned solutions to cnf")
    parse.add_argument("-c", "--cnf", type=str, help="cnf file")
    parse.add_argument("-s", "--solution", type=str, help="solution file")
    parse.add_argument("-r", "--rounds", type=int, help="rounds of the solution")
    parse.add_argument("-d", "--digest", type=int, help="the digest of keccak")
    args = parse.parse_args()

    a = read_sol(args.solution, args.rounds, args.digest)
    if not a:
        raise ValueError("solution not found")
    ban_list = ban_sol(a)
    add_ban2cnf(args.cnf, ban_list)