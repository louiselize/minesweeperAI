from typing import List, Tuple
import subprocess
import os

#---------------------------------------------
#fonction Dimacs
#---------------------------------------------
def clauses_to_dimacs(clauses: List[List[int]], nbVariableTotal: int) -> str:
    s = f"p cnf {nbVariableTotal} {len(clauses)}\n"
    for i in range(len(clauses)):
        for j in range(len(clauses[i])):
            s += f"{clauses[i][j]} "
        s += "0\n"
    return s

def write_dimacs_file(dimacs: str, filename: str):
    with open(filename, "w", newline="") as cnf:
        cnf.write(dimacs)


def exec_gophersat(
    filename: str, cmd: str = "gophersat", encoding: str = "utf8"
) -> Tuple[bool, List[int]]:
    result = subprocess.run(
        [cmd, filename], capture_output=True, check=True, encoding=encoding
    )
    string = str(result.stdout)
    lines = string.splitlines()

    if lines[1] != "s SATISFIABLE":
        return False, []

    model = lines[2][2:].split(" ")

    return True, [int(x) for x in model]


