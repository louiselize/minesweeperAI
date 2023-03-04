import constraints
from conversion import *
from functions import *
from typing import List, Tuple
from itertools import combinations



#_____________________________________________
#---------------------------------------------
# PARTIE 1 : CONTRAINTE DE BASE DE NOTRE JEU
#---------------------------------------------
#_____________________________________________

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
#Variable 7x : sea (-sea = land)

i=0
t=1
nt=2
c=3
nc=4
sh=5
nsh=6
se=7


#---------------------------------------------
#Contraintes liées aux animaux:
#---------------------------------------------


def create_tiger_constraints(boardSize : int, nbVariable : int) -> List[List[int]]:
    constraintsList=[]
    i=0
    t=1
    nt=2
    nc=4
    nsh=6
    while(i<boardSize) :

        constraintsList.append([-t,nc]) # t->nc
        constraintsList.append([-t,nsh]) # t->nsh
        constraintsList.append([-t,-nt]) # t-> -nt
        t=t+nbVariable
        nc=nc+nbVariable
        nsh=nsh+nbVariable
        nt=nt+nbVariable
        i=i+1
    return constraintsList

def create_croco_constraints(boardSize : int, nbVariable : int) -> List[List[int]]:
    constraintsList=[]
    c=3
    nt=2
    nc=4
    nsh=6
    i=0
    while(i<boardSize) :
        constraintsList.append([-c,nt]) # c->nt
        constraintsList.append([-c,nsh]) # c->nsh 
        constraintsList.append([-c,-nc]) # c->-nc  
        c=c+nbVariable
        nc=nc+nbVariable
        nt=nt+nbVariable
        nsh=nsh+nbVariable
        i=i+1
    return constraintsList

def create_shark_constraints(boardSize : int, nbVariable : int) -> List[List[int]]:
    constraintsList=[]
    sh=5
    nt=2
    nc=4
    nsh=6
    i=0
    while(i<boardSize) :
        constraintsList.append([-sh,nt]) # sh -> nt
        constraintsList.append([-sh,nc]) # sh -> nc
        constraintsList.append([-sh,-nsh]) # sh -> nsh
        sh=sh+nbVariable
        nsh=nsh+nbVariable
        nt=nt+nbVariable
        nc=nc+nbVariable
        i=i+1
    return constraintsList



#---------------------------------------------
#Contraintes liées aux animaux et au terrain:
#---------------------------------------------

def create_field_and_animals_constraints(boardSize : int, nbVariable : int) -> List[List[int]]:
    constraintsList=[]
    i=0
    t=1
    nt=2
    sh=5
    nsh=6
    se=7
    
    while(i<boardSize) :
        constraintsList.append([-t,-se]) # tigre -> -sea : -t ou -se
        constraintsList.append([-sh,se]) # shark -> sea : -sh ou se
        constraintsList.append([-se,nt]) # sea -> notiger : -se ou nt
        constraintsList.append([se,nsh]) # -sea -> noshark : se ou nsh
        se=se+nbVariable
        
        nt=nt+nbVariable
        t=t+nbVariable

        nsh=nsh+nbVariable
        sh=sh+nbVariable
        
        i=i+1
    return constraintsList


#---------------------------------------------------
#Contraintes de toutes les contraintes de la grille:
#---------------------------------------------------

def create_all_constraints(boardSize : int, nbVariable : int)->List[List[int]]:
    List = []
    List += create_tiger_constraints(boardSize, nbVariable)
    List += create_shark_constraints(boardSize, nbVariable)
    List += create_croco_constraints(boardSize, nbVariable)
    List += create_field_and_animals_constraints(boardSize, nbVariable)
    return List



#_______________________________________________________
#---------------------------------------------
#PARTIE 2 : Contraintes relatives aux infos de la grille
#---------------------------------------------
#_______________________________________________________




#---------------------------------------------
#1) ---------- CONTRAINTE FIELD --------------
#---------------------------------------------
def create_board_field_constraints(i : int, j : int, nbVariable :int, nbColumn:int, field: str):
    constraintsList=[]
    var=cell_to_variable(i,j,nbVariable,nbColumn)

    if(field=="sea"):
        constraintsList = [[var+6]] #+6 car sea est la 7eme variable
    elif(field=="land"):
                constraintsList = [[(var+6)*(-1)]] #+6 car sea est la 7eme variable

    return constraintsList


#---------------------------------------------
#2) ---------- CONTRAINTE VOISINAGE ----------
#---------------------------------------------

# Exemple pour mieux comprendre à quoi sert la fonction : 
# il y a 3 animaux dans le voisinages ↔ il y a 5 cases sans animaux

def create_neighbour_constraints(i : int, j :int, nbLine : int, nbColumn : int, boardSize : int, nbVariable : int, prox_count: Tuple[int], field : str) -> List[List[int]]:
    constraintsList = []
    combi = []
    neighbour =  neighbour_cells(i,j,nbLine,nbColumn)
    cmpt=0    
    while(cmpt<len(neighbour)):
        pos=neighbour[cmpt]
        c=cell_to_variable(pos[0],pos[1],nbVariable,nbColumn)
        combi += [c]
        cmpt=cmpt+1

    #croco constaints :
    nbCroco=prox_count[2]
    if(nbCroco==0):
        for cpt in combi:
            constraintsList+=[[cpt+3]] 

    elif(nbCroco>=1):
        crocoNeighbour = []
        #comme on a deux équivalences, on crée deux listes : → et ←
        constraintsCrocoList1 = []
        constraintsCrocoList2 = []
        #On crée un tableau pour avoir toutes les cases opposées aux cases qui ont des animaux
        opposite=[]
        for cpt in range(len(combi)):
            val=combi[cpt]+2  #+2 car croco est notre 3 ème variable
            crocoNeighbour += [val]

        crocoCombi=list(combinations(crocoNeighbour,nbCroco))
        for i in range(len(crocoCombi)):
            for v in crocoNeighbour:
                if v not in crocoCombi[i]:
                    for j in crocoCombi[i]:
                        constraintsCrocoList1.append(j+1)
                    constraintsCrocoList1.append(v+1)
                    opposite.append(v)
                if(len(constraintsCrocoList1)>0):
                    constraintsList += [constraintsCrocoList1]
                constraintsCrocoList1=[]
            for j in crocoCombi[i]:
                constraintsCrocoList2.append(j)
                for n in opposite:
                    constraintsCrocoList2.append(n)   
                constraintsList += [constraintsCrocoList2]
                constraintsCrocoList2=[]   
            opposite=[]           
              


    #shark constraints :
    nbtiger=prox_count[0]
    if(nbtiger==0):
        for cpt in combi:
            constraintsList+=[[cpt+1]]
    
    nbshark=prox_count[1]
    if(nbshark==0):
            for cpt in combi:
                constraintsList+=[[cpt+5]] 
            

    if(nbshark>=1):
            sharkNeighbour = []
            #comme on a deux équivalences, on crée deux listes : → et ←
            constraintssharkList1 = []
            constraintssharkList2 = []
            #On crée un tableau pour avoir toutes les cases opposées aux cases qui ont des animaux
            opposite=[]
            for cpt in range(len(combi)):
                val=combi[cpt]+4  #+4 car shark est notre 5 ème variable
                sharkNeighbour += [val]
            #for cpt in range(boardSize) :
            sharkCombi=list(combinations(sharkNeighbour,nbshark))
            for i in range(len(sharkCombi)):
                for v in sharkNeighbour:
                    if v not in sharkCombi[i]:
                        for j in sharkCombi[i]:
                            constraintssharkList1.append(j+1)
                        constraintssharkList1.append(v+1)
                        opposite.append(v)
                    if(len(constraintssharkList1)>0):
                        constraintsList += [constraintssharkList1]
                    constraintssharkList1=[]
                for j in sharkCombi[i]:
                    constraintssharkList2.append(j)
                    for n in opposite:
                        constraintssharkList2.append(n)   
                    constraintsList += [constraintssharkList2]
                    constraintssharkList2=[]   
                opposite=[] 
        

    
    if(nbtiger>=1):
            tigerNeighbour = []
            #comme on a deux équivalences, on crée deux listes : → et ←
            constraintstigerList1 = []
            constraintstigerList2 = []
            #On crée un tableau pour avoir toutes les cases opposées aux cases qui ont des animaux
            opposite=[]

            for cpt in range(len(combi)):
                val=combi[cpt] # tiger est notre 1 ème variable
                tigerNeighbour += [val]
            #for cpt in range(boardSize) :
            tigerCombi=list(combinations(tigerNeighbour,nbtiger))
            for i in range(len(tigerCombi)):
                for v in tigerNeighbour:
                    if v not in tigerCombi[i]:
                        for j in tigerCombi[i]:
                            constraintstigerList1.append(j+1)
                        constraintstigerList1.append(v+1)
                        opposite.append(v)
                    if(len(constraintstigerList1)>0):
                        constraintsList += [constraintstigerList1]
                    constraintstigerList1=[]
                for j in tigerCombi[i]:
                    constraintstigerList2.append(j)
                    for n in opposite:
                        constraintstigerList2.append(n)   
                    constraintsList += [constraintstigerList2]
                    constraintstigerList2=[]   
                opposite=[]    
            
        
        
    return constraintsList


#---------------------------------------------
#3) ---------- CONTRAINTE VISITE -----------
# IL N'Y A PAS D'ANIMAL SUR LES CASES VISITEES
#---------------------------------------------

   
def create_visited_cells_constraints(i :int,j:int,nbVariable:int,nbColumn:int):
    constraintsList=[]
    var=cell_to_variable(i,j,nbVariable,nbColumn)
    constraintsList += [[var+1]] # notiger
    constraintsList += [[var+3]] # nocroco
    constraintsList += [[var+5]] # noshark

    return constraintsList

#---------------------------------------------
#4) ---------- CONTRAINTE NO CROCO -----------
# IL N'Y A PAS DE CROCO SUR LES CASES RESTANTES
#---------------------------------------------    
def create_no_Croco_constraints(remainingCase :List[List[int]],nbLine :int ,nbColumn:int,boardSize:int,nbVariable:int)-> List[List[int]]:

    constraintsList=[]   
    for cmpt in range(len(remainingCase)):
        pos=remainingCase[cmpt]
        c=cell_to_variable(pos[0],pos[1],nbVariable,nbColumn)
        constraintsList += [[c+3]]
    
    return constraintsList

#5) ---------- CONTRAINTE NO SHARK -----------
# IL N'Y A PAS DE REQUIN SUR LES CASES RESTANTES
#---------------------------------------------    
def create_no_Shark_constraints(remainingCase :List[List[int]],nbLine :int ,nbColumn:int,boardSize:int,nbVariable:int)-> List[List[int]]:

    constraintsList=[]   
    for cmpt in range(len(remainingCase)):
        pos=remainingCase[cmpt]
        c=cell_to_variable(pos[0],pos[1],nbVariable,nbColumn)
        constraintsList += [[c+5]]
    
    return constraintsList

#5) ---------- CONTRAINTE NO TIGER -----------
# IL N'Y A PAS DE TIGRE SUR LES CASES RESTANTES
#---------------------------------------------    
def create_no_Tiger_constraints(remainingCase :List[List[int]],nbLine :int ,nbColumn:int,boardSize:int,nbVariable:int)-> List[List[int]]:

    constraintsList=[]   
    
    for cmpt in range(len(remainingCase)):
        pos=remainingCase[cmpt]
        c=cell_to_variable(pos[0],pos[1],nbVariable,nbColumn)
        constraintsList += [[c+1]]
    
    return constraintsList


#---------------------------------------------
#7) -------- CONTRAINTE NB ANIMAUX -----------
# En fin de jeu quand on ne peut plus avancer
#---------------------------------------------
def create_number_animals_constraints(remainingCase : List[List[int]],nbTiger : int,nbCroco:int,nbShark:int,nbLine:int,nbColumn:int,boardSize:int,nbVariable:int)-> List[List[int]]:
    combi=[] 
    constraintsList=[]   
    for cmpt in range(len(remainingCase)):
        pos=remainingCase[cmpt]
        c=cell_to_variable(pos[0],pos[1],nbVariable,nbColumn)
        combi += [c]
        
    #TRAITEMENT DES CROCOS
    if(nbShark>0):
        constraintssharkList1=[]
        constraintssharkList2=[]
        sharkConstraints = []
        opposite=[]

        for cpt in range(len(combi)):
                val=combi[cpt]+4 # shark est notre 5 ème variable
                sharkConstraints += [val]
        
        sharkCombi=list(combinations(sharkConstraints,nbShark))
        for i in range(len(sharkCombi)):
                for v in sharkConstraints:
                    if v not in sharkCombi[i]:
                        for j in sharkCombi[i]:
                            constraintssharkList1.append(j+1)
                        constraintssharkList1.append(v+1)
                        opposite.append(v)
                    if(len(constraintssharkList1)>0):
                        constraintsList += [constraintssharkList1]
                    constraintssharkList1=[]
                for j in sharkCombi[i]:
                    constraintssharkList2.append(j)
                    for n in opposite:
                        constraintssharkList2.append(n)   
                    constraintsList += [constraintssharkList2]
                    constraintssharkList2=[]   
                opposite=[] 
    #TRAITEMENT DES CROCOS
    if(nbCroco>0):
        constraintscrocoList1=[]
        constraintscrocoList2=[]
        crocoConstraints = []
        opposite=[]

        for cpt in range(len(combi)):
                val=combi[cpt]+2 # croco est notre 3 ème variable
                crocoConstraints += [val]
        
        crocoCombi=list(combinations(crocoConstraints,nbCroco))
        for i in range(len(crocoCombi)):
                for v in crocoConstraints:
                    if v not in crocoCombi[i]:
                        for j in crocoCombi[i]:
                            constraintscrocoList1.append(j+1)
                        constraintscrocoList1.append(v+1)
                        opposite.append(v)
                    if(len(constraintscrocoList1)>0):
                        constraintsList += [constraintscrocoList1]
                    constraintscrocoList1=[]
                for j in crocoCombi[i]:
                    constraintscrocoList2.append(j)
                    for n in opposite:
                        constraintscrocoList2.append(n)   
                    constraintsList += [constraintscrocoList2]
                    constraintscrocoList2=[]   
                opposite=[] 
    #TRAITEMENT DES TigerS
    if(nbTiger>0):
        constraintsTigerList1=[]
        constraintsTigerList2=[]
        TigerConstraints = []
        opposite=[]

        for cpt in range(len(combi)):
                val=combi[cpt] # Tiger est notre 1 ème variable
                TigerConstraints += [val]
        
        TigerCombi=list(combinations(TigerConstraints,nbTiger))
        for i in range(len(TigerCombi)):
                for v in TigerConstraints:
                    if v not in TigerCombi[i]:
                        for j in TigerCombi[i]:
                            constraintsTigerList1.append(j+1)
                        constraintsTigerList1.append(v+1)
                        opposite.append(v)
                    if(len(constraintsTigerList1)>0):
                        constraintsList += [constraintsTigerList1]
                    constraintsTigerList1=[]
                for j in TigerCombi[i]:
                    constraintsTigerList2.append(j)
                    for n in opposite:
                        constraintsTigerList2.append(n)   
                    constraintsList += [constraintsTigerList2]
                    constraintsTigerList2=[]   
                opposite=[] 
        
    return constraintsList


def create_number_sharks_constraints(remainingCase,nbShark :int ,nbLine:int,nbColumn:int,boardSize:int,nbVariable:int):
    combi=[] 
    constraintsList=[]   
    for cmpt in range(len(remainingCase)):
        pos=remainingCase[cmpt]
        c=cell_to_variable(pos[0],pos[1],nbVariable,nbColumn)
        combi += [c]
    if(nbShark>0):
        constraintssharkList1=[]
        constraintssharkList2=[]
        sharkConstraints = []
        opposite=[]

        for cpt in range(len(combi)):
                val=combi[cpt]+4 # shark est notre 5 ème variable
                sharkConstraints += [val]
        
        sharkCombi=list(combinations(sharkConstraints,nbShark))
        for i in range(len(sharkCombi)):
                for v in sharkConstraints:
                    if v not in sharkCombi[i]:
                        for j in sharkCombi[i]:
                            constraintssharkList1.append(j+1)
                        constraintssharkList1.append(v+1)
                        opposite.append(v)
                    if(len(constraintssharkList1)>0):
                        constraintsList += [constraintssharkList1]
                    constraintssharkList1=[]
                for j in sharkCombi[i]:
                    constraintssharkList2.append(j)
                    for n in opposite:
                        constraintssharkList2.append(n)   
                    constraintsList += [constraintssharkList2]
                    constraintssharkList2=[]   
                opposite=[]
    return constraintsList
def create_number_tigers_constraints(remainingCase,nbTiger :int ,nbLine:int,nbColumn:int,boardSize:int,nbVariable:int):
    combi=[] 
    constraintsList=[]   
    for cmpt in range(len(remainingCase)):
        pos=remainingCase[cmpt]
        c=cell_to_variable(pos[0],pos[1],nbVariable,nbColumn)
        combi += [c]
    if(nbTiger>0):
        constraintsTigerList1=[]
        constraintsTigerList2=[]
        TigerConstraints = []
        opposite=[]

        for cpt in range(len(combi)):
                val=combi[cpt] # Tiger est notre 1 ème variable
                TigerConstraints += [val]
        
        TigerCombi=list(combinations(TigerConstraints,nbTiger))
        for i in range(len(TigerCombi)):
                for v in TigerConstraints:
                    if v not in TigerCombi[i]:
                        for j in TigerCombi[i]:
                            constraintsTigerList1.append(j+1)
                        constraintsTigerList1.append(v+1)
                        opposite.append(v)
                    if(len(constraintsTigerList1)>0):
                        constraintsList += [constraintsTigerList1]
                    constraintsTigerList1=[]
                for j in TigerCombi[i]:
                    constraintsTigerList2.append(j)
                    for n in opposite:
                        constraintsTigerList2.append(n)   
                    constraintsList += [constraintsTigerList2]
                    constraintsTigerList2=[]   
                opposite=[] 
        
    return constraintsList


def create_number_crocos_constraints(remainingCase,nbCroco :int ,nbLine:int,nbColumn:int,boardSize:int,nbVariable:int):
    combi=[] 
    constraintsList=[]   
    for cmpt in range(len(remainingCase)):
        pos=remainingCase[cmpt]
        c=cell_to_variable(pos[0],pos[1],nbVariable,nbColumn)
        combi += [c]
    if(nbCroco>0):
        constraintscrocoList1=[]
        constraintscrocoList2=[]
        crocoConstraints = []
        opposite=[]

        for cpt in range(len(combi)):
                val=combi[cpt]+2 # croco est notre 3 ème variable
                crocoConstraints += [val]
        
        crocoCombi=list(combinations(crocoConstraints,nbCroco))
        for i in range(len(crocoCombi)):
                for v in crocoConstraints:
                    if v not in crocoCombi[i]:
                        for j in crocoCombi[i]:
                            constraintscrocoList1.append(j+1)
                        constraintscrocoList1.append(v+1)
                        opposite.append(v)
                    if(len(constraintscrocoList1)>0):
                        constraintsList += [constraintscrocoList1]
                    constraintscrocoList1=[]
                for j in crocoCombi[i]:
                    constraintscrocoList2.append(j)
                    for n in opposite:
                        constraintscrocoList2.append(n)   
                    constraintsList += [constraintscrocoList2]
                    constraintscrocoList2=[]   
                opposite=[] 
    return constraintsList