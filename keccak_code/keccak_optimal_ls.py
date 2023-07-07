#-------------------------------------------------------------------------------
# Name:     Keccak224/256/384/512
# Purpose:  Model initialization: generate initial state CNF
#           All CNF consists of three parts: 
#           1. initial state CNF (generete using keccak_optimal_ls.py),
#           2. sbox and Constraint CNF (using get_allcons_cnf.py), 
#           3. Objective Function CNF (using PySat,https://pysathq.github.io/) 
# Author:   Anonymous
# Created:  25-11-2022
# Version:  1st

#-------------------------------------------------------------------------------
from sage.all import *
from copy import copy, deepcopy
from sage.rings.polynomial.pbori.pbori import *
from sage.rings.polynomial.pbori import *
from random import randint
from sage.sat.boolean_polynomials import solve as solve_sat
from sage.sat.converters.polybori import CNFEncoder
from sage.sat.solvers.dimacs import DIMACS
import sys
import logging
import argparse


# create logger
logger = logging.getLogger("XOR model: Keccak512_one_round")
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter("c:%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)

# state size
state = 1600
lane_z = state // 25
# rotation offsets
rho_offsets = [[0,    36,     3,    41,    18],
                [1,    44,    10,    45,     2],
                [62,    6,    43,    15,    61],
                [28,   55,    25,    21,    56],
                [27,   20,    39,     8,    14]]
# constants of iota
constants = [0x0000000000000001, 0x0000000000008082,
        0x800000000000808A, 0x8000000080008000,
        0x000000000000808B, 0x0000000080000001,
        0x8000000080008081, 0x8000000000008009,
        0x000000000000008A, 0x0000000000000088,
        0x0000000080008009, 0x000000008000000A,
        0x000000008000808B, 0x800000000000008B,
        0x8000000000008089, 0x8000000000008003,
        0x8000000000008002, 0x8000000000000080,
        0x000000000000800A, 0x800000008000000A,
        0x8000000080008081, 0x8000000000008080,
        0x0000000080000001, 0x8000000080008008]

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

def index_x(x: int)-> int:
    """return the index of coordinates x

    Args:
        x (int): x coordinate

    Returns:
        int: index of x
    """
    x = (x + 5)%5
    return x

def index_z(z: int)-> int:
    """return the index of coordinates z

    Args:
        z (int): z coordinate

    Returns:
        int: index of z
    """
    z = (x + 64)%64
    return z

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

def single_lane(lane: list, offset: int) -> list:
    """cycle left shift

    Args:
        lane (list): input lane
        offset (int): shift offset

    Raises:
        ValueError: lane size error

    Returns:
        list: lane after shift
    """
    if len(lane) != lane_z:
        raise ValueError("lane size should be {}, not {}".format(lane_z, len(lane)))
    offset %= lane_z
    return lane[lane_z - offset:lane_z] + lane[0:lane_z - offset]

def single_plane(plane: list, dx: int, dz: int) -> list:
    """cycle left shift plane <<< (dx, dz)

    Args:
        plane (list): input plane
        dx (int): shift x offset
        dz (int): shift z offset

    Returns:
        list: plane after shift
    """
    P = []
    for i in range(5):
        for k in range(lane_z):
            P.append(plane[index_xz(i-dx, k-dz)])
    return P

def theta(X: list) -> list:
    """theta map

    Args:
        X (list): input state

    Returns:
        list: output state after theta
    """
    P = []
    # get the column parity of the state
    for i in range(5 * lane_z):
        col = R(0)
        for j in range(5):
            col += X[i+j*5*lane_z]
        P.append(col)
    # cycle left shift the column parity
    E1 = single_plane(P, 1, 0)  # P <<< (1, 0)
    E2 = single_plane(P, -1, 1) # P <<< (-1, 1)

    Y = X.copy()
    for i in range(state):
        Y[i] += E1[i%(5*lane_z)] + E2[i%(5*lane_z)]
    return Y

def inv_theta(X: list) -> list:
    """inverse of theta map

    Args:
        X (list): input state

    Returns:
        list: output state after inverse theta
    """
    P = []
    # get the column parity of the state
    for i in range(5*lane_z):
        col = R(0)
        for j in range(5):
            col += X[i+j*5*lane_z]
        P.append(col)
    # the indexes below represent the inverse matrix
    # if (theta_inv_index[x] >> z) & 1 = 1, then output[i][j][k] += y=0to4Σ input[i-x][y][k-z]
    # you can compute the inverse polynomial of theta referring to keccak reference
    theta_inv_index = [0xDE26BC4D789AF134, 0x09AF135E26BC4D78, 0xEBC4D789AF135E26, 
                        0x7135E26BC4D789AF, 0xCD789AF135E26BC4]
    Y = X.copy()
    for z in range(lane_z):
        for x in range(5):
            # if (theta_inv_index[x] >> z) & 1 = 1
            if (theta_inv_index[x] >> z) & 1:
                for i in range(5):
                    for j in range(5):
                        for k in range(lane_z):
                            # output[i][j][k] += y=0to4Σ input[i-x][y][k-z]
                            Y[index_(i, j, k)] += P[index_xz(i-x, k-z)]
    return Y

def rho(X: list) -> list:
    """rho map

    Args:
        X (list): input state

    Returns:
        list: output state after rho
    """
    Y = [R(0) for _ in range(state)]
    for x in range(5):
        for y in range(5):
            # rotation the lane
            Y[index_xy(x,y):index_xy(x,y) + lane_z] = \
                        single_lane(X[index_xy(x,y):index_xy(x,y) + lane_z], rho_offsets[x][y])
    return Y

def inv_rho(X: list) -> list:
    """inverse of rho map

    Args:
        X (list): input state

    Returns:
        list: output state after inverse rho
    """
    Y = [R(0) for _ in range(state)]
    for x in range(5):
        for y in range(5):
            # rotation the lane
            Y[index_xy(x,y):index_xy(x,y) + lane_z] = \
                        single_lane(X[index_xy(x,y):index_xy(x,y) + lane_z], -rho_offsets[x][y])
    return Y

def pi(X: list) -> list:
    """pi map
        M = 0 1
            2 3

    Args:
        X (list): input state

    Returns:
        list: output state after pi
    """
    Y = [R(0) for i in range(state)]
    for y in range(5):
        for x in range(5):
            px, py = y, 2*x + 3*y
            for z in range(lane_z):
                Y[index_(px, py, z)] = X[index_(x, y, z)]
    return Y
 
def inv_pi(X: list) -> list:
    """inverse of pi map
        M^-1 = 1 3
               1 0

    Args:
        X (list): input state

    Returns:
        list: output state after inverse pi
    """
    Y = [R(0) for i in range(state)]
    for y in range(5):
        for x in range(5):
            px, py = x + 3*y, x
            for z in range(lane_z):
                Y[index_(px, py, z)] = X[index_(x, y, z)]
    return Y

def chi(X: list) -> list:
    """chi map

    Args:
        X (list): input state

    Returns:
        list: output state after chi
    """
    Y = [R(0) for i in range(state)]
    # 5 bits as a row, each row uses a 5-bits row_chi
    for z in range(lane_z):
        for y in range(5):
            for x in range(5):
                # get the row
                row = [X[index_(x+i, y, z)] for i in range(3)]
                Y[index_(x, y, z)] = row[0] + (1+row[1]) * row[2]
    return Y

def inv_chi(X: list) -> list:
    """inverse of chi map

    Args:
        X (list): input state

    Returns:
        list: output state after inverse chi
    """
    Y = [R(0) for i in range(state)]
    # 5 bits as a row, each row uses a 5-bits row_chi
    for z in range(lane_z):
        for y in range(5):
            for x in range(5):
                # get the row
                row = [X[index_(x+i, y, z)] for i in range(5)]
                Y[index_(x, y, z)] = row[0] + (row[1]+1) * (row[2] + (row[3]+1)*row[4])
    return Y

def addConst(X: list, r: int) -> list:
    """iota map

    Args:
        X (list): input state
        r (int): current round number

    Returns:
        list: output state after iota map
    """
    Y = X.copy()
    for i in range(lane_z):
        if (constants[r] >> i) & 0x1:
            Y[i] += 1
    return Y

def keccak_round(X: list, r: int) -> list:
    """the keccak round function

    Args:
        X (list): input state
        r (int): current round number

    Returns:
        list: output state after a keccak round
    """
    for i in range(r):
        X = theta(X)
        X = rho(X)
        X = pi(X)
        X = chi(X)
        X = addConst(X, i)
    return X

def inv_round(X: list, r: int) -> list:
    """the keccak round inverse function

    Args:
        X (list): input state
        r (int): current round number

    Returns:
        list: output state after a keccak inverse round
    """
    for i in range(r):
        X = addConst(X, r-1-i)
        X = inv_chi(X)
        X = inv_pi(X)
        X = inv_rho(X)
        X = inv_theta(X)
    return X

def print_state(X):
    for i in range(25):
        # print a row at a time
        row_print = ""
        # now start convert binary state to hex form
        # get the binary state
        state_binary = X[lane_z * i : lane_z * i + lane_z]
        # the length of a word should be the multiple of 4
        if len(state_binary) % 4 != 0:
            logger.error("the length of a word should be the multiple of 4")
            exit(1)
        # compute hex every 4 bits
        state_hex = ""
        for k in range(len(state_binary) // 4):
            # compute 4 bits int value
            tmp = 0
            for bit in range(4):
                tmp += (int(state_binary[k * 4 + bit]) << bit)
            # convert in value to hex and remove "0x", then add to the state
            state_hex = hex(tmp)[2:] + state_hex
        # padding "0x"
        state_hex = "0x" + state_hex
        # add the state to the row, delimiter is " "(space)
        row_print += state_hex + " "
        logger.info(row_print)



if __name__ == '__main__':
    # Target param 
    Digest = 512
    Capacity = 2 * Digest
    Rate = state - Capacity
    ROUNDS = 1
    R = declare_ring([Block('x', 3*ROUNDS*state + 3*ROUNDS*5*lane_z   ), 'u'], globals())
    A = [[R(x(i + 3*r*state)) for i in range(state) ] for r in range(ROUNDS) ]               
    B = [[R(x(i + (3*r+1)*state)) for i in range(state) ] for r in range(ROUNDS) ]  
    C = [[R(x(i + (3*r+2)*state)) for i in range(state) ] for r in range(ROUNDS) ]         
    G = [[R(x(i + 3*ROUNDS*state + 5*lane_z*r)) for i in range(5*lane_z) ] for r in range(ROUNDS) ]  
    D = [[R(x(i + 3*ROUNDS*state + ROUNDS*5*lane_z + 5*lane_z*r)) for i in range(5*lane_z) ] for r in range(ROUNDS) ] 
    Quar = [[R(x(i + 3*ROUNDS*state + 2*ROUNDS*5*lane_z + 5*lane_z*r)) for i in range(5*lane_z) ] for r in range(ROUNDS) ] 
    Q = set()
    ################INV#########################
    # 2r: numvars
    # A[0]      v 1    -  1600
    # B[0]      v 1601 -  3200
    # C[0]      v 3201 -  4800
    # A[1]      v 4801 -  6400
    # B[1]      v 6401 -  8000
    # C[1]      v 8001 -  9600
    # G[0]      v 9601 -  9920
    # G[1]      v 9921 - 10240
    # D[0]      v 10241 - 10560
    # D[1]      v 10561 - 10880
    # Quar[0]   v 10881 - 11200
    # Quar[1]   v 11201 - 11520
    ############################################
    ## A[rate:state] = R(0), 1 means the bit contains a variable; otherwise A[i] = 0, means a constant
    ## prepare INV state A_x,y,z--A[0][i] = R(0)
    for i in range(Rate,state):
        Q.add(A[0][i])
        A[0][i] = R(0)
    #############################################
    # A[0]---theta-->B[0]---rhopi-->C[0]---chi-->A[1]
    # A[1]---theta-->B[1]---rhopi-->C[1]
    # XOR model only is constructed  in rhopi operation B[r]---rhopi-->C[r].
    #logger.info(B)
    for r in range(ROUNDS):
        B[r] = rho(B[r])
        B[r] = pi(B[r])
        for i in range(state):
            Q.add(B[r][i] + C[r][i]) 
    """
    for q in Q:
        print(q)
    logger.info("finished")
    """
    solver = DIMACS(filename = "/home/n2107349e/SAT/preimage/Complex_LS/keccak512/keccak512_1r_XOR.cnf")
    e = CNFEncoder(solver, R)
    e(list(Q))
    solver.write()
    