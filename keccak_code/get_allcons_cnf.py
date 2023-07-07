#-------------------------------------------------------------------------------
# Name:     Keccak224/256/384/512
# Purpose:  Generate all contraints of n rounds in CNF form -->list
#           All CNFconsists of three parts: 
#           1. initial state CNF (generete using keccak_optimal_ls.py),
#           2. sbox and Constraint CNF (using get_allcons_cnf.py), 
#           3. Objective Function CNF (using PySat,https://pysathq.github.io/) 
# Author:   Anonymous
# Created:  30-11-2022
# Version:  1st
#-------------------------------------------------------------------------------
import sys
import math

ROUNDS = 2
state = 1600
lane_z = state//25


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
    z = (x + lane_z)%lane_z
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

## 3 clauses
cnf_col_1 = [
    [-3], 
    [1, -2], 
    [2, -1]
]

## 5 clauses
cnf_col_2 = [
    [1, -4],
    [-4, -3],
    [1, 2, -3],
    [2, 3, -1],
    [4, 3, -2]
]

## 7 clauses
cnf_col_3 = [
    [-5, -4], 
    [1, 2, -5], 
    [5, 4, -2], 
    [5, 4, -3], 
    [1, 2, 3, -4], 
    [1, 3, 4, -2], 
    [2, 3, 4, -1]
]

## 9 clauses
cnf_col_4 = [
    [-6, -5],
    [6, 5, -2], 
    [6, 5, -3], 
    [6, 5, -4], 
    [1, 2, 3, -6], 
    [1, 2, 3, 4, -5], 
    [1, 2, 4, 5, -3], 
    [1, 3, 4, 5, -2], 
    [2, 3, 4, 5, -1]
]
## 11 clauses [A0,A1,A2,A3,A4,G,D]
cnf_col_5 = [
    [-7, -6], 
    [7, 6, -2], 
    [7, 6, -3], 
    [7, 6, -4], 
    [7, 6, -5], 
    [1, 2, 3, 4, -7], 
    [1, 2, 3, 4, 5, -6], 
    [1, 2, 3, 5, 6, -4], 
    [1, 2, 4, 5, 6, -3], 
    [1, 3, 4, 5, 6, -2], 
    [2, 3, 4, 5, 6, -1]
]

## 4 clauses [A,G,G,B]
cnf_atob = [
    [4, -1], 
    [4, -2], 
    [4, -3], 
    [1, 2, 3, -4]
]

## 15 clauses [C0,C1,C2,C3,C4,A0,A1,A2,A3,A4]
cnf_ctoa = [
    [6, -1], 
    [7, -2], 
    [8, -3], 
    [9, -4], 
    [10, -5], 
    [-1, -2], 
    [-1, -5], 
    [-2, -3], 
    [-3, -4], 
    [-4, -5], 
    [1, 2, 3, -6], 
    [1, 2, 5, -10], 
    [1, 4, 5, -9], 
    [2, 3, 4, -7], 
    [3, 4, 5, -8]
]



## 20 clauses
cnf_sim_ctoa = [
    [6, -1], 
    [7, -2], 
    [8, -3], 
    [9, -4], 
    [10, -5], 
    [-1, -2], 
    [-1, -5], 
    [-2, -3], 
    [-3, -4], 
    [-4, -5], 
    [1, 2, 3, -6], 
    [1, 2, 5, -10], 
    [1, 4, 5, -9], 
    [2, 3, 4, -7], 
    [3, 4, 5, -8], 
    [1, -6, -7, -8], 
    [2, -7, -8, -9], 
    [3, -8, -9, -10], 
    [4, -6, -9, -10], 
    [5, -6, -7, -10]

]


## 5 clauses [C0,C1,C2,C3,C4]
cnf_c = [
    [-1, -2],
    [-1, -5],
    [-2, -3],
    [-3, -4],
    [-4, -5]
]
## 6 clauses
cnf_sim_c = [
    [-1, -2], 
    [-1, -5], 
    [-2, -3], 
    [-3, -4], 
    [-4, -5], 
    [1, 2, 3, 4, 5]
]
## 8 clauses
cnf_two_c = [
    [1,2,3], 
    [1,4,5], 
    [3,4,5], 
    [-1,-2], 
    [-1,-5], 
    [-2,-3], 
    [-3,-4], 
    [-4,-5]
]

## 14 clauses [C0,C1,C2,C3,C4]
cnf_c_quar = [
    [6, -1, -2], 
    [6, -1, -5], 
    [6, -2, -3], 
    [6, -3, -4], 
    [6, -4, -5], 
    [1, 2, 4, -6], 
    [1, 3, 4, -6], 
    [1, 3, 5, -6], 
    [2, 3, 5, -6], 
    [-1, -2, -5], 
    [-2, -3, -4], 
    [-3, -4, -5], 
    [2, 3, -1, -4, -6], 
    [4, 5, -1, -3, -6]
]

## 9 clauses
cnf_col_5_k = [
    [6, -2], 
    [6, -3], 
    [6, -4], 
    [6, -5], 
    [1, 3, 4, -6], 
    [1, 2, 3, 5, -6], 
    [1, 2, 4, 5, -3], 
    [2, 3, 4, 5, -1], 
    [4, -1, -2, -3, -5]
]

## 2 clauses
cnf_a_eq_b = [
    [1,-2],
    [2,-1]
]

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
    # cnf_col_5:[A0,A1,A2,A3,A4,G,D]
    # cnf_atob:   [A,G,G,B]
    # cnf_ctoa:   [C0,C1,C2,C3,C4,A0,A1,A2,A3,A4]
    # cnf_c:      [C0,C1,C2,C3,C4]
    ############################################

## cnf_col_4: 9 clauses 
row = [0]*6
for r in range(1): 
    for x in range (3):
        for z in range (lane_z):   
            # column [A0,A1,A2,A3,G,D]
            row = [3*r*state + index_(x,0,z),3*r*state + index_(x,1,z),3*r*state + index_(x,2,z),3*r*state + index_(x,3,z), 3*ROUNDS*state + r*5*lane_z + index_xz(x,z), 3*ROUNDS*state + ROUNDS*5*lane_z + r*5*lane_z + index_xz(x,z)]
    
            for i in range (len(cnf_col_4)):
                CNF_clause= ""
                for j in range(len(cnf_col_4[i])):
                    temp = int(cnf_col_4[i][j])
                    if temp > 0 :
                        CNF_clause += str(row[ temp-1] + 1) + " "
                    else:
                        CNF_clause += str(-1 * row[abs(temp+1)]-1) + " "
                CNF_clause += '0'
                print(CNF_clause)

## cnf_col_3: 7 clauses 
row = [0]*5
for r in range(1): 
    for x in range (3,5):
        for z in range (lane_z):   
            # column [A0,A1,A2,G,D]
            row = [3*r*state + index_(x,0,z), 3*r*state + index_(x,1,z),3*r*state + index_(x,2,z),3*ROUNDS*state + r*5*lane_z + index_xz(x,z), 3*ROUNDS*state + ROUNDS*5*lane_z + r*5*lane_z + index_xz(x,z)]
    
            for i in range (len(cnf_col_3)):
                CNF_clause= ""
                for j in range(len(cnf_col_3[i])):
                    temp = int(cnf_col_3[i][j])
                    if temp > 0 :
                        CNF_clause += str(row[ temp-1] + 1) + " "
                    else:
                        CNF_clause += str(-1 * row[abs(temp+1)]-1) + " "
                CNF_clause += '0'
                print(CNF_clause)           
"""
## cnf_col_5: 11 clauses 
row = [0]*7
for r in range(1,ROUNDS): 
    for x in range (5):
        for z in range (lane_z):   
            # column [A0,A1,A2,A3,A4,G,D]
            row = [3*r*state + index_(x,0,z),3*r*state + index_(x,1,z),3*r*state + index_(x,2,z),3*r*state + index_(x,3,z),3*r*state + index_(x,4,z), 3*ROUNDS*state + r*5*lane_z + index_xz(x,z), 3*ROUNDS*state + ROUNDS*5*lane_z + r*5*lane_z + index_xz(x,z)]
    
            for i in range (len(cnf_col_5)):
                CNF_clause= ""
                for j in range(len(cnf_col_5[i])):
                    temp = int(cnf_col_5[i][j])
                    if temp > 0 :
                        CNF_clause += str(row[ temp-1] + 1) + " "
                    else:
                        CNF_clause += str(-1 * row[abs(temp+1)]-1) + " "
                CNF_clause += '0'
                print(CNF_clause)
"""
## cnf_atob: 4 clauses    
row = [0]*4
for r in range(1): 
    for x in range(5):
        for y in range(5):
            for z in range (lane_z):   
                # [A,G,G,B]
                row = [3*r*state + index_(x,y,z),3*ROUNDS*state + r*5*lane_z + index_xz(x-1,z),3*ROUNDS*state + r*5*lane_z + index_xz(x+1,z-1),(3*r+1)*state + index_(x,y,z)]
        
                for i in range (len(cnf_atob)):
                    CNF_clause= ""
                    for j in range(len(cnf_atob[i])):
                        temp = int(cnf_atob[i][j])
                        if temp > 0 :
                            CNF_clause += str(row[ temp-1] + 1) + " "
                        else:
                            CNF_clause += str(-1 * row[abs(temp+1)]-1) + " "
                    CNF_clause += '0'
                    print(CNF_clause)  
## cnf_ctoa: 16 clauses only add in the first round
## cnf_two_ctoa: 13 clauses
## cnf_sim_ctoa: 20 clauses
row = [0]*10
for r in range(ROUNDS-1): 
    for y in range(5):
        for z in range (lane_z):   
            # [C0,C1,C2,C3,C4,A0,A1,A2,A3,A4] 
            row = [(3*r+2)*state + index_(0,y,z),(3*r+2)*state + index_(1,y,z), (3*r+2)*state + index_(2,y,z),(3*r+2)*state + index_(3,y,z),(3*r+2)*state + index_(4,y,z),3*(r+1)*state + index_(0,y,z),3*(r+1)*state + index_(1,y,z),3*(r+1)*state + index_(2,y,z),3*(r+1)*state + index_(3,y,z),3*(r+1)*state + index_(4,y,z)]
    
            for i in range (len(cnf_sim_ctoa)):
                CNF_clause= ""
                for j in range(len(cnf_sim_ctoa[i])):
                    temp = int(cnf_sim_ctoa[i][j])
                    if temp > 0 :
                        CNF_clause += str(row[ temp-1] + 1) + " "
                    else:
                        CNF_clause += str(-1 * row[abs(temp+1)]-1) + " "
                CNF_clause += '0'
                print(CNF_clause)     


## cnf_col_5_k: 9 clauses 
row = [0]*6
for r in range(1,ROUNDS): 
    for x in range (5):
        for z in range (lane_z):   
            # column [A0,A1,A2,A3,A4,D]
            row = [3*r*state + index_(x,0,z),3*r*state + index_(x,1,z),3*r*state + index_(x,2,z),3*r*state + index_(x,3,z),3*r*state + index_(x,4,z),  3*ROUNDS*state + ROUNDS*5*lane_z + r*5*lane_z + index_xz(x,z)]
    
            for i in range (len(cnf_col_5_k)):
                CNF_clause= ""
                for j in range(len(cnf_col_5_k[i])):
                    temp = int(cnf_col_5_k[i][j])
                    if temp > 0 :
                        CNF_clause += str(row[ temp-1] + 1) + " "
                    else:
                        CNF_clause += str(-1 * row[abs(temp+1)]-1) + " "
                CNF_clause += '0'
                print(CNF_clause)

## cnf_a_eq_b: 2 clauses    
row = [0]*2
for r in range(1,ROUNDS): 
    for x in range(5):
        for y in range(5):
            for z in range (lane_z):   
                # [A,B]
                row = [3*r*state + index_(x,y,z),(3*r+1)*state + index_(x,y,z)]
        
                for i in range (len(cnf_a_eq_b)):
                    CNF_clause= ""
                    for j in range(len(cnf_a_eq_b[i])):
                        temp = int(cnf_a_eq_b[i][j])
                        if temp > 0 :
                            CNF_clause += str(row[ temp-1] + 1) + " "
                        else:
                            CNF_clause += str(-1 * row[abs(temp+1)]-1) + " "
                    CNF_clause += '0'
                    print(CNF_clause) 
"""
## cnf_c_quar: 14 clauses only add in the second round
row = [0]*5
for r in range(ROUNDS-1,ROUNDS): 
    for y in range(5):
        for z in range (lane_z):   
            # [C0,C1,C2,C3,C4,Q] 
            row = [(3*r+2)*state + index_(0,y,z),(3*r+2)*state + index_(1,y,z), (3*r+2)*state + index_(2,y,z),(3*r+2)*state + index_(3,y,z),(3*r+2)*state + index_(4,y,z),3*ROUNDS*state + 2*ROUNDS*5*lane_z + r*5*lane_z + index_xz(y,z)]
    
            for i in range (len(cnf_c_quar)):
                CNF_clause= ""
                for j in range(len(cnf_c_quar[i])):
                    temp = int(cnf_c_quar[i][j])
                    if temp > 0 :
                        CNF_clause += str(row[ temp-1] + 1) + " "
                    else:
                        CNF_clause += str(-1 * row[abs(temp+1)]-1) + " "
                CNF_clause += '0'
                print(CNF_clause)     
"""
## cnf_c: 5 clauses
## cnf_two_c: 8 clauses only add in the first round
row = [0]*5
for r in range(ROUNDS-1,ROUNDS): 
    for y in range(5):
        for z in range (lane_z):   
            # [C0,C1,C2,C3,C4] 
            row = [(3*r+2)*state + index_(0,y,z),(3*r+2)*state + index_(1,y,z), (3*r+2)*state + index_(2,y,z),(3*r+2)*state + index_(3,y,z),(3*r+2)*state + index_(4,y,z)]
    
            for i in range (len(cnf_two_c)):
                CNF_clause= ""
                for j in range(len(cnf_two_c[i])):
                    temp = int(cnf_two_c[i][j])
                    if temp > 0 :
                        CNF_clause += str(row[ temp-1] + 1) + " "
                    else:
                        CNF_clause += str(-1 * row[abs(temp+1)]-1) + " "
                CNF_clause += '0'
                print(CNF_clause)   