from typing import List, Tuple
from array import *
import subprocess

#Variable 1x : tiger
#Variable 2x : notiger
#Variable 3x : croco
#Variable 4x : nocroco
#Variable 5x : shark
#Variable 6x : noshark
#Variable 7x : sea
#Variable 8x : nosea
#Variable 9x : land/non(land)
#Variable 10x : noland
#Variable 11x : safe
#Variable 12x : unsafe

g_i=0
g_t=1
g_nt=2
g_c=3
g_nc=4
g_sh=5
g_nsh=6
g_se=7
g_nse=8
g_l=9
g_nl=10
g_safe=11
g_nsafe=12
 

#---------------------------------------------
#fonction Dimacs
#---------------------------------------------
def clauses_to_dimacs(clauses: List[List[int]], boardSize: int) -> str:
    print("debut clause to dimacs")
    s = f"p cnf {boardSize*nbVariable} {len(clauses)}\n"
    for i in range(len(clauses)):
        for j in range(len(clauses[i])):
            s += f"{clauses[i][j]} "
            #print(s)
        s += "0\n"
    print("fin clause to dimacs")
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

#---------------------------------------
#fonction utilitaires de conversion
#---------------------------------------
   
nbVariable = 12
nbLine = 3
nbColumn = 3
boardSize = nbColumn * nbLine
constraintsList= []

def cell_to_variable(i : int, j : int) -> int:
    return (nbVariable) * (i * nbColumn + j )

#---------------------------------------------
#Contraintes liées aux animaux:
#---------------------------------------------
#s=shark, c=croco, t=tiger
#ns=noshark, nc=nocroco, nt=notiger
#se=sea,l=land
#nse=nosea,nl=noland

#Variable 1x : tiger
#Variable 2x : notiger
#Variable 3x : croco
#Variable 4x : nocroco
#Variable 5x : shark
#Variable 6x : noshark
#Variable 7x : sea
#Variable 8x : nosea
#Variable 9x : land
#Variable 10x : noland
#Variable 11x : safe
#Variable 12x : unsafe


def create_tiger_constraints(var:List[List[int]]) -> List[List[int]]:
    t=var[1]
    nt=var[2]
    nc=var[4]
    nsh=var[6]
    constraintsList.append([-t,nc]) # t->nc
    constraintsList.append([-t,nsh]) # t->nsh
    constraintsList.append([-t,-nt]) # t-> -nt
    print(f"tigre: {constraintsList}")
    return constraintsList

def create_croco_constraints(var:List[List[int]]) -> List[List[int]]:
    nt=var[2]
    c=var[3]
    nc=var[4]
    nsh=var[6]
    constraintsList.append([-c,nt]) # c->nt
    constraintsList.append([-c,nsh]) # c->nsh 
    constraintsList.append([-c,-nc]) # c->-nc
    return constraintsList

def create_shark_constraints(var:List[List[int]]) -> List[List[int]]:
    nt=var[2]
    nc=var[4]
    sh=var[5]
    nsh=var[6]
    constraintsList.append([-sh,nt]) # sh -> nt
    constraintsList.append([-sh,nc]) # sh -> nc
    constraintsList.append([-sh,-nsh]) # sh -> nsh
    return constraintsList

#---------------------------------------------
#Contraintes liées au terrain:
#---------------------------------------------
#s=sea, l=land
#ns=nosea, nl=noland
def create_field_constraints(var:List[List[int]]) -> List[List[int]]:
    se=var[7]
    nse=var[8]
    l=var[9]
    nl=var[10]
    constraintsList.append([-se,nl]) #sea -> noland
    constraintsList.append([-nl,se]) #noland -> sea
    constraintsList.append([-l,nse]) #land -> nosea
    constraintsList.append([-nse,l]) #nosea  -> land
    constraintsList.append([-nse,-se]) #nosea -> -sea
    constraintsList.append([-nl,-l]) #noland -> -land
    return constraintsList

#---------------------------------------------
#Contraintes liées à safe et unsafe:
#---------------------------------------------
#safe donne pastigre pascroco pasrequin
#unsafe donne requin ou croco ou tigree

def create_safe_constraints(var:List[List[int]]) -> List[List[int]]:
    t=var[1]
    nt=var[2]
    c=var[3]
    nc=var[4]
    sh=var[5]
    nsh=var[6]
    safe=var[11]
    nsafe=var[12]
    # safe <-> notiger ^ nocroco ^ noshark
        # notiger ^ nocroco ^ noshark -> safe
    constraintsList.append([safe,-nt,-nc,-nsh])  
        # safe -> notiger ^ nocroco ^ noshark
    constraintsList.append([-safe,nt]) # 
    constraintsList.append([-safe,nc]) #
    constraintsList.append([-safe,nsh]) #
    #unsafe <-> requin V croco V tigre
        #unsafe -> requin V croco V tigre
    constraintsList.append([nsafe,sh,c,t])
        #requin V croco V tigre -> unsafe 
    constraintsList.append([nsafe,-t]) # 
    constraintsList.append([nsafe,-c]) #
    constraintsList.append([nsafe,-sh]) #
    return constraintsList

#---------------------------------------------
#Contraintes liées aux animaux et au terrain:
#---------------------------------------------

#genre si terre alors pas de requin et si mer alors pas de tigre

def create_field_and_animals_constraints(var:List[List[int]]) -> List[List[int]]:
    t=var[1]
    nt=var[2]
    sh=var[5]
    nsh=var[6]
    se=var[7]
    nse=var[8]
    l=var[9]
    nl=var[10]
    constraintsList.append([-se,nt]) # sea -> notigre
    constraintsList.append([-t,nse]) # tigre -> nosea
    constraintsList.append([-l,nsh]) # land -> noshark
    constraintsList.append([-sh,nl]) # shark -> noland
    return constraintsList
#---------------------------------------------
#Contraintes toutes les contraintes:
#---------------------------------------------

def create_all_constraints()->List[List[int]]:
    tab_var=[g_i, g_t, g_nt, g_c, g_nc, g_sh, g_nsh, g_se, g_nse, g_l, g_nl, g_safe, g_nsafe]
    
    constraintsList = []
    while(tab_var[0]<boardSize):
        constraintsList += create_tiger_constraints(tab_var)
        constraintsList += create_shark_constraints(tab_var)
        constraintsList += create_croco_constraints(tab_var)
        constraintsList += create_field_constraints(tab_var)
        constraintsList += create_safe_constraints(tab_var)
        constraintsList += create_field_and_animals_constraints(tab_var)
        tab_var[0]=tab_var[0]+1
        j=1
        print(tab_var[0])
        while(j<=nbVariable):
            tab_var[j]=tab_var[j]+nbVariable
            j=j+1
    print("fin create all constraints")
    print(f"taille: {len(constraintsList)}")
    return constraintsList

#---------------------------------------------
#Contraintes liées au terrain:
#---------------------------------------------
#s=shark, c=croco, t=tiger
#ns=noshark, nc=nocroco, nt=notiger
#se=sea,l=land
#nse=nosea,nl=noland


clauses_to_dimacs(create_all_constraints(),boardSize)
print(cell_to_variable(0,1))
#print(len(create_all_constraints()))

        
