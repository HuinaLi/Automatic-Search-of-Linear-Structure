import argparse
parse = argparse.ArgumentParser(description="combine 2 cnfs")
parse.add_argument("-f1", "--file1", type=str, help="original cnf file1")
parse.add_argument("-f2", "--file2", type=str, help="cnf file2")
parse.add_argument("-f3", "--file3", type=str, help="cnf file3")
parse.add_argument("-o", "--output", type=str, help="output cnf file")
parse.add_argument("-r", "--rounds", type=int, help="number of rounds")
args = parse.parse_args()

path1 = args.file1
path2 = args.file2
path3 = args.file3
path4 = args.output
rounds = args.rounds
# open file
f1 = open(path1, "r")
f2 = open(path2, "r")
f3 = open(path3, "r")
# file to write
f4 = open(path4, "w")
# buf to write
buf = ""
# read file
buf = f1.read()
buf += f2.read()
buf += f3.read()
# find the end of the first line
index_1st = buf.find("\n")
# combine
buf = buf[:index_1st + 1]  + buf[index_1st + 1:]
# modify first line
line_1st = buf[:index_1st + 1].split()
## 640<=256_kmt: 3376; 640<=320_kmt:3433; 640<=448_kmt:3586
line_1st[2] = str(int(line_1st[2]) + 6658  + 3586)
# compute the number of lines of file2
f2.seek(0)
line_num2 = len(f2.readlines())
# compute the number of lines of file3
f3.seek(0)
line_num3 = len(f3.readlines())
line_1st[3] = str(int(line_1st[3]) + line_num2 + line_num3 )
print(line_num2)
print(line_num3)
buf = " ".join(line_1st) + "\n" + buf[index_1st + 1:]

f4.write(buf)
# close
f1.close()
f2.close()
f3.close()
f4.close()