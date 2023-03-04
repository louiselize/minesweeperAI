from typing import List, Tuple

#Ajouter variable tigre, requi et croco et si c'est pas unsat on fait +1

def randomChoose(constraintsList : List[List[int]], allInfo, fieldKnown):
    #Repérer les cases en bordures k
        #Pour chaque k prendre ses voisins qui ne sont pas découverts et récupérer le terrain
        for cpt in range(len(allInfo)):
            inf=allInfo[cpt]
            pos=inf["pos"]
            field=inf["field"]
            if field not in fieldKnown:
                constraintsList += [[(cell_to_variable(cell[0],cell[1],nbVariable,nbColumn)+5)]] #ajout no shark
                write_dimacs_file(clauses_to_dimacs(constraintsList,nbVariable*boardSize),"const.cnf") 
                res=exec_gophersat("const.cnf")
                #si unsat -> il y a un shark, sinon on ne sait pas
                #ainsi si unsat -> le découvrir
                del constraintsList[-1] #retirer la derniere contrainte ajouter
                if not res[0]:
                    status, msg, infos = croco.guess(cell[0],cell[1],'S')
                    allInfo+=infos
                    #print(allInfo)
                    visited += [cell]
                    constraintsList+=[[(cell_to_variable(cell[0],cell[1],nbVariable,nbColumn)+4)]]
                    #nbrequin=nbrequin+1
                    nbShark=nbShark-1
                    #if(cell[0]==1 and cell[1]==8):
                    #  print("case : ",cell[0]," ", cell[1], " : ",constraintsList)
                    del remainingCase[remainingCase.index(cell)]