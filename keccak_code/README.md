Contents of the files:

code files:
1. keccak_optimal_ls.py: the code to describe model initialization and  generate initial state CNF.

2. get_cons.py: the code to generate all contraints in CNF form.

3. get_allcons_cnf.py: the code to generate all contraints of n rounds in CNF form.

4. combine_cons_xor_cnf.py: the code to combine n-round linear structure model's CNF including: 
1). Initial state CNFs (generete using keccak_optimal_ls.py), 
2). All constraints CNFs (using get_allcons_cnf.py), 

5. combine_object_cnf.py: the code to generate the final n-round linear structure search SAT model by combining Initial state's CNFs and All constraints' CNFs, as well as Objective funcition's CNFs.

6. read_and_ban_solution.py: the code to solve our model, we incorporate the concept of rotational symmetry here, in this way, the solver will exclude rotationally-equivalent solutions and continue searching for new ones that are distinct.

7. dc_anf2cnf_and_combine.sh: the code to help me automatically return all solutions with detailed  search time.

result folder:
1. keccak256_2.5r.log: the result to print 2.5-round linear structures on keccak256.

1. keccak512_1.5r.log: the result to print 2.5-round linear structures on keccak512.

note that: our model returns huge solutions, for save memory, we only provide a part of the solutions for the check.