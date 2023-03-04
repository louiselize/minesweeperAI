from functions import *
from constraints import *
from solveurSAT import *
from functions import cell_to_variable
from crocomine_client import CrocomineClient

def noAnimal_test(cell : List[int],nbVariable:int,nbColumn:int,boardSize:int,constraintsList :List[List[int]],visited:List[List[int]],croco,status):

    isSat=1
    noanimal = []
    infos=[]
    noanimal.append((cell_to_variable(cell[0],cell[1],nbVariable,nbColumn)))
    noanimal.append((cell_to_variable(cell[0],cell[1],nbVariable,nbColumn))+2)
    noanimal.append((cell_to_variable(cell[0],cell[1],nbVariable,nbColumn))+4)
    constraintsList += [noanimal] #ajout no croco
    write_dimacs_file(clauses_to_dimacs(constraintsList,nbVariable*boardSize),"const.cnf") 
    res=exec_gophersat("const.cnf")
    del constraintsList[-1] #retirer la derniere contrainte ajouter

    if not res[0]: # Non SAT => Nocroco & Noshark & Notiger
        status, msg, infos = croco.discover(cell[0],cell[1])
        #print(status, msg)
        #pprint(infos)
        visited += [cell]
        
                                                    
        constraintsList+=[[(cell_to_variable(cell[0],cell[1],nbVariable,nbColumn)+1)]]
        constraintsList+=[[(cell_to_variable(cell[0],cell[1],nbVariable,nbColumn))+3]]
        constraintsList+=[[(cell_to_variable(cell[0],cell[1],nbVariable,nbColumn))+5]]
        isSat=0
    return isSat,constraintsList,infos,visited,status

def is_there_tiger_test(cell : List[int],nbVariable:int,nbColumn:int,boardSize:int,constraintsList :List[List[int]],visited:List[List[int]],croco,nbTiger,remainingCase,status):
    isSat=1
    infos=[]
    constraintsList += [[(cell_to_variable(cell[0],cell[1],nbVariable,nbColumn)+1)]] #ajout no tiger
    write_dimacs_file(clauses_to_dimacs(constraintsList,nbVariable*boardSize),"const.cnf") 
    res=exec_gophersat("const.cnf")
    #si unsat -> il y a un shark, sinon on ne sait pas
    #ainsi si unsat -> le découvrir
    del constraintsList[-1] #retirer la derniere contrainte ajouter

    if not res[0]:
        status, msg, infos = croco.guess(cell[0],cell[1],'T')
        #print(status, msg)
        #pprint(infos)
        visited += [cell]
        constraintsList+=[[(cell_to_variable(cell[0],cell[1],nbVariable,nbColumn))]]
        nbTiger=nbTiger-1
        del remainingCase[remainingCase.index(cell)] 
        isSat=0
    return isSat,constraintsList,infos,visited,nbTiger,remainingCase,status

def is_there_Croco_test(cell : List[int],nbVariable:int,nbColumn:int,boardSize:int,constraintsList :List[List[int]],visited:List[List[int]],croco,nbCroco,remainingCase,status):
    isSat=1
    infos=[]
    constraintsList += [[(cell_to_variable(cell[0],cell[1],nbVariable,nbColumn)+3)]] #ajout no croco
    write_dimacs_file(clauses_to_dimacs(constraintsList,nbVariable*boardSize),"const.cnf") 
    res=exec_gophersat("const.cnf")
    #si unsat -> il y a un croco, sinon on ne sait pas
    #ainsi si unsat -> le découvrir
                                            
    del constraintsList[-1] #retirer la derniere contrainte ajouter
    if not res[0]:
        status, msg, infos = croco.guess(cell[0],cell[1],"C")
        #print(status, msg)
        #pprint(infos)
        visited += [cell]
        constraintsList+=[[(cell_to_variable(cell[0],cell[1],nbVariable,nbColumn)+2)]]
        nbCroco = nbCroco-1
        del remainingCase[remainingCase.index(cell)]
        isSat=0
    return isSat,constraintsList,infos,visited,nbCroco,remainingCase,status

def is_there_Shark_test(cell : List[int],nbVariable:int,nbColumn:int,boardSize:int,constraintsList :List[List[int]],visited:List[List[int]],croco,nbShark,remainingCase,status):
    isSat=1
    infos=[]
    constraintsList += [[(cell_to_variable(cell[0],cell[1],nbVariable,nbColumn)+5)]] #ajout no shark    
    write_dimacs_file(clauses_to_dimacs(constraintsList,nbVariable*boardSize),"const.cnf") 
    res=exec_gophersat("const.cnf")
   
    #si unsat -> il y a un shark, sinon on ne sait pas
    #ainsi si unsat -> le découvrir
    del constraintsList[-1] #retirer la derniere contrainte ajouter
    if not res[0]:
        status, msg, infos = croco.guess(cell[0],cell[1],'S')
        #print(status, msg)
        #pprint(infos)
        visited += [cell]
        constraintsList+=[[(cell_to_variable(cell[0],cell[1],nbVariable,nbColumn)+4)]]
        nbShark=nbShark-1
        del remainingCase[remainingCase.index(cell)]
        isSat=0
    return isSat,constraintsList,infos,visited,nbShark,remainingCase,status
