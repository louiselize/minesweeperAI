#from Projet.ia02.client.functions import neighbour_cells
#from Projet.ia02.client.functions import neighbour_cells
#from Projet.ia02.client.conversion import cell_to_variable
from typing import List, Tuple
import subprocess
from pprint import pprint
from constraints import *
import constraints
from conversion import *
from functions import *
from solveurSAT import *
from crocomine_client import CrocomineClient
from operator import itemgetter



#---------------------------------------------












#DEPRECATED : see mainN.py
















#---------------------------------------------


#---------------------------------------------
#INFORMATIONS
#---------------------------------------------

#Pour lancer le serveur : 
# clic droit dossier ia02
#open in integrated terminal
#.\server\win64\crocomine-lite-beta4.exe :8000 ./grids/ 
#Pour lancer le client : 
# terminal > split terminal
#cd client
# python lefichier.py (leur code exemple c'est exemple.py et nous main.py)

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
 

#---------------------------------------------
#Fonction principale de test
#---------------------------------------------
def test(nbVariable):

    server = "http://localhost:8000"
    group = "Groupe 30"
    members = "Hugo LESOBRE et Louise LIZE"
    croco = CrocomineClient(server, group, members)

    #on passe les deux premières grilles
    croco.new_grid()
    croco.new_grid()
    croco.new_grid()
    croco.new_grid()
    NbGridDone=0
    while(NbGridDone<8):
        NbGridDone=NbGridDone+1
        status, msg, grid_infos = croco.new_grid()
        nbColumn=grid_infos["n"]
        nbLine=grid_infos["m"]
        boardSize=nbLine*nbColumn
        start=grid_infos['start']
        nbAnimals = grid_infos["shark_count"]+ grid_infos["croco_count"] + grid_infos["tiger_count"]
        nbShark=grid_infos["shark_count"]
        nbCroco=grid_infos["croco_count"]
        nbTiger=grid_infos["tiger_count"]
        constraintsNoCrocoDone=0
        constraintsNoTigerDone=0
        constraintsNoSharkDone=0
        aleatoireMoment=0
        remainingCase = []
        #f = open("const.cnf","w")
        #input()
        #f.close()
        for i in range(nbLine):
            for j in range(nbColumn):
                remainingCase += [[i,j]]

        visited = []
        fieldKnown = []
        allInfo = []
        nbtour=-5
        notvisited=-1
        
        #creation des contraintes du jeu avec les regles de departs
        constraintsList = []
        constraintsDone=[]
        constraintsList += create_all_constraints(boardSize,nbVariable)

        print(status, msg)
        pprint(grid_infos)

        status, msg, infos = croco.discover(start[0],start[1])
        print(status, msg)
        print("a")
        pprint(infos)
        print("-------")
        print(allInfo)
        allInfo+= infos

        #Creation du premier tableau des cases visitées
        """for cmpt in range(len(infos)):
            inf=infos[cmpt]
            fieldKnown += [inf["pos"]]
            if('prox_count' in inf):
                visited += [inf["pos"]]
        """
        while(status=="OK"):
        
            
            #on recupere toutes les infos que l'on a et l'on en cree des contraintes
            for cpt in range(len(allInfo)):
                inf=allInfo[cpt]
                pos=inf["pos"]
                field=inf["field"]
                #1 : contrainte sur les fields que l'on connait (cases visites et '?')
                if(pos not in fieldKnown):
                    constraintsList += create_board_field_constraints(pos[0],pos[1],nbVariable,nbColumn,field)
                    fieldKnown += [pos]


                #2: contraintes sur les cases déjà visites (car on connait mtn les nb d'animaux, et on sait qu'elles sont safe)
                if('prox_count' in inf and pos not in constraintsDone): #si la case a été visitée...
                    prox_count=inf["prox_count"]   
                    constraintsList += create_neighbour_constraints(pos[0],pos[1],nbLine,nbColumn,boardSize,nbVariable,prox_count,field) #contraintes sur le nb d'animaux
                    constraintsList += create_visited_cells_constraints(pos[0],pos[1],nbVariable,nbColumn) #elles sont safe
                    visited += [pos]
                    del remainingCase[remainingCase.index(pos)] 
                    constraintsDone +=[pos]
                
                
            #3 : au cas ou on bloque, gerer la contrainte du nombre de case
            print("nbtour",nbtour," notvisited",notvisited)
            if(nbtour==notvisited and aleatoireMoment==0):
                #nbremainingCase = boardSize-(len(constraintsDone)+(nbAnimals-nbTiger-nbCroco-nbShark))
                constraintsList += create_number_animals_constraints(remainingCase,nbTiger,nbCroco,nbShark,nbLine,nbColumn,boardSize,nbVariable)
                aleatoireMoment=1
            elif(nbtour==notvisited and aleatoireMoment==1):
                combi_pos_animal=[]
                nbSea=0
                nbField=0
                for case in range(len(allInfo)):
                    
                    infoCase=allInfo[case]
                    if not 'prox_count' in infoCase:
                        if infoCase["field"]=="sea":
                            nbSea+=1
                        else:
                            nbField+=1

                        casesVoisines=neighbour_cells(infoCase["pos"][0],infoCase["pos"][1],nbLine,nbColumn)
                        nbAnimaux=neighbour_cells_info(casesVoisines,infoCase,allInfo)
                        combi_act=[infoCase["pos"],nbAnimaux,infoCase["field"]]
                        #pprint(infoCase["prox_count"])
                        combi_pos_animal.append(combi_act)
                    
                pprint(combi_pos_animal)
                print(f"nbSea {nbSea} ")
                print(f"nbField {nbField}")
                for case in combi_pos_animal:
                    if case[2]=="sea":
                        case[1]/=nbSea
                    else:
                        case[1]/=nbField
                #pprint(combi_pos_animal)
                combi_pos_animal.sort(reverse=True,key=itemgetter(1)) #Classe de proba la + haute à + faible. (Permettre d'être en O(1) sur le pop)
                pprint(combi_pos_animal)
                #foundCorrectRandom=False
                pos_a_tester=combi_pos_animal.pop()[0]
                print("ALEA")
                status, msg, infos = croco.discover(pos_a_tester[0],pos_a_tester[1])
                aleatoireMoment=0
                #print("///////////////////////////////////////////")
                print(status, msg)
                pprint(infos)
                allInfo+=infos
                #print(allInfo)
                visited += [pos_a_tester]
                #print("///////////////////////////////////////////")
                print("boucle finale ppour gagner")

                #while(not foundCorrectRandom):
                #    pos_a_tester=combi_pos_animal.pop()[0] #O(1) -- Prends la dernère case de la liste contenant une des positions avec la + faible proba
                #    pprint(pos_a_tester)
                #    cell_to_variable(pos_a_tester[0],pos_a_tester[1],nbVariable,nbColumn)

               
                print("nous sommes mtn dans la gestion de l'aléatoire")

            # FONCTION POUR TESTER CHAQUE CASE ET S'IL ELLES SONT UNSAT -> DISCOVER / GUESS   
        
            nbtour=0
            notvisited=0
            for cpt in range(len(fieldKnown)):
                
            #si plus d'animaux, tout découvrir

                if(nbTiger==0 and nbCroco==0 and nbShark==0):
                    cpt=0
                    while(status!="GG"):
                        cmpt=remainingCase[cpt]
                        status, msg, infos = croco.discover(cmpt[0],cmpt[1])
                        print(status, msg)
                        pprint(infos)
                        cpt=cpt+1
                        print("boucle finale ppour gagner")
               
               
                # si le nb d'animaux restants = 0 faire des contraintes de nocroco
                #constraintsNoAnimalDone sert à ne passer qu'une fois dans la boucle et ne pas rajouter 
                #des contraintes en boucle
                if(nbCroco==0 and constraintsNoCrocoDone==0):
                    constraintsList+= create_no_Croco_constraints(remainingCase,nbLine,nbColumn,boardSize,nbVariable)
                    constraintsNoCrocoDone=1
                

                if(nbShark==0 and constraintsNoSharkDone==0):
                    constraintsList+= create_no_Shark_constraints(remainingCase,nbLine,nbColumn,boardSize,nbVariable)
                    constraintsNoSharkDone=1
                    

                if(nbTiger==0 and constraintsNoTigerDone==0):
                    constraintsList+= create_no_Tiger_constraints(remainingCase,nbLine,nbColumn,boardSize,nbVariable)
                    constraintsNoTigerDone=1

                
                            
                            
                        
                    
                else:
                    cell=fieldKnown[cpt]
                    if cell not in visited:
                        notvisited=notvisited+1
                        #
                        #
                        # A FAIRE : TESTER SI LA CASE EST MERE OU TERRE
                        # COMME CA ON EVITE UN APPEL A GOPHERSAT 
                        #
                        # A FAIRE 2 : SI IL N'Y A PLUS DE CROCO DE TIGRE OU DE SHARK, NE PAS APPELER GOPHERSAT POUR CET/CES ANIMAL/ANIMAUX
                        #
                        #

                        #NO ANIMAL TEST
                        noanimal = []
                        noanimal.append((cell_to_variable(cell[0],cell[1],nbVariable,nbColumn)))
                        noanimal.append((cell_to_variable(cell[0],cell[1],nbVariable,nbColumn))+2)
                        noanimal.append((cell_to_variable(cell[0],cell[1],nbVariable,nbColumn))+4)
                        constraintsList += [noanimal] #ajout no croco
                        #input()
                        write_dimacs_file(clauses_to_dimacs(constraintsList,nbVariable*boardSize),"const.cnf") 
                        #input()
                        res=exec_gophersat("const.cnf")
                        
                        #si unsat -> il y a un shark, sinon on ne sait pas
                        #ainsi si unsat -> le découvrir
                        del constraintsList[-1] #retirer la derniere contrainte ajouter
                        if not res[0]: # Non SAT => Nocroco & Noshark & Notiger
                            status, msg, infos = croco.discover(cell[0],cell[1])
                            print(status, msg)
                            pprint(infos)
                            allInfo+=infos
                            #print(allInfo)
                            visited += [cell]
                            
                            constraintsList+=[[(cell_to_variable(cell[0],cell[1],nbVariable,nbColumn)+1)]]
                            constraintsList+=[[(cell_to_variable(cell[0],cell[1],nbVariable,nbColumn))+3]]
                            constraintsList+=[[(cell_to_variable(cell[0],cell[1],nbVariable,nbColumn))+5]]

                        
                        #CROCO TEST
                        else :
                            constraintsList += [[(cell_to_variable(cell[0],cell[1],nbVariable,nbColumn)+3)]] #ajout no croco
                            write_dimacs_file(clauses_to_dimacs(constraintsList,nbVariable*boardSize),"const.cnf") 
                            res=exec_gophersat("const.cnf")
                            #si unsat -> il y a un shark, sinon on ne sait pas
                            #ainsi si unsat -> le découvrir
                        
                            del constraintsList[-1] #retirer la derniere contrainte ajouter
                            if not res[0]:
                                status, msg, infos = croco.guess(cell[0],cell[1],"C")
                                print(status, msg)
                                pprint(infos)
                                allInfo+=infos
                                #print(allInfo)
                                visited += [cell]
                                constraintsList+=[[(cell_to_variable(cell[0],cell[1],nbVariable,nbColumn)+2)]]
                                nbCroco = nbCroco-1
                                del remainingCase[remainingCase.index(cell)] 



                            #SHARK TEST
                            else:
                                constraintsList += [[(cell_to_variable(cell[0],cell[1],nbVariable,nbColumn)+5)]] #ajout no shark
                                write_dimacs_file(clauses_to_dimacs(constraintsList,nbVariable*boardSize),"const.cnf") 
                                res=exec_gophersat("const.cnf")
                                #si unsat -> il y a un shark, sinon on ne sait pas
                                #ainsi si unsat -> le découvrir
                                del constraintsList[-1] #retirer la derniere contrainte ajouter
                                if not res[0]:
                                    status, msg, infos = croco.guess(cell[0],cell[1],'S')
                                    print(status, msg)
                                    pprint(infos)
                                    allInfo+=infos
                                    #print(allInfo)
                                    visited += [cell]
                                    constraintsList+=[[(cell_to_variable(cell[0],cell[1],nbVariable,nbColumn)+4)]]
                                    #nbrequin=nbrequin+1
                                    nbShark=nbShark-1
                                    #if(cell[0]==1 and cell[1]==8):
                                    #  print("case : ",cell[0]," ", cell[1], " : ",constraintsList)
                                    del remainingCase[remainingCase.index(cell)]

                                
                                #TIGER TEST
                                else:
                                    #print(res)
                                    constraintsList += [[(cell_to_variable(cell[0],cell[1],nbVariable,nbColumn)+1)]] #ajout no tiger
                                    write_dimacs_file(clauses_to_dimacs(constraintsList,nbVariable*boardSize),"const.cnf") 
                                    res=exec_gophersat("const.cnf")
                                    #si unsat -> il y a un shark, sinon on ne sait pas
                                    #ainsi si unsat -> le découvrir
                                    if(cell[0]==5 and cell[1]==1):
                                        print(res)
                                        print(cell_to_variable(cell[0],cell[1],nbVariable,nbColumn))
                                        print(cell_to_variable(3,1,nbVariable,nbColumn))
                                        print(cell_to_variable(3,2,nbVariable,nbColumn))
                                        print(cell_to_variable(3,3,nbVariable,nbColumn))
                                        print(cell_to_variable(4,1,nbVariable,nbColumn))
                                        print(cell_to_variable(4,2,nbVariable,nbColumn))
                                        print(cell_to_variable(4,3,nbVariable,nbColumn))
                                        print(cell_to_variable(5,1,nbVariable,nbColumn))
                                        print(cell_to_variable(5,2,nbVariable,nbColumn))
                                        print(cell_to_variable(5,3,nbVariable,nbColumn))


                                    del constraintsList[-1] #retirer la derniere contrainte ajouter
                                    if not res[0]:
                                        status, msg, infos = croco.guess(cell[0],cell[1],'T')
                                        print(status, msg)
                                        pprint(infos)
                                        allInfo+=infos
                                        #print(allInfo)
                                        visited += [cell]
                                        constraintsList+=[[(cell_to_variable(cell[0],cell[1],nbVariable,nbColumn))]]
                                        nbTiger=nbTiger-1
                                        del remainingCase[remainingCase.index(cell)]                      

                                    
                                        


                                    else: 
                                        nbtour=nbtour+1

                    for cpt in range(len(allInfo)):
                                            inf=allInfo[cpt]
                                            pos=inf["pos"]
                                            field=inf["field"]
                                            #1 : contrainte sur les fields que l'on connait (cases visites et '?')
                                            if(pos not in fieldKnown):
                                                constraintsList += create_board_field_constraints(pos[0],pos[1],nbVariable,nbColumn,field)
                                                fieldKnown += [pos]


                                            #2: contraintes sur les cases déjà visites (car on connait mtn les nb d'animaux, et on sait qu'elles sont safe)
                                            if('prox_count' in inf and pos not in constraintsDone): #si la case a été visitée...
                                                prox_count=inf["prox_count"]   
                                            
                                                constraintsList += create_neighbour_constraints(pos[0],pos[1],nbLine,nbColumn,boardSize,nbVariable,prox_count,field) #contraintes sur le nb d'animaux
                                                constraintsList += create_visited_cells_constraints(pos[0],pos[1],nbVariable,nbColumn) #elles sont safe
                                                visited += [pos]
                                                constraintsDone +=[pos]
                                                del remainingCase[remainingCase.index(pos)]                      




#-----MAIN------
        
nbVariable=7
#test(nbVariable)
print((cell_to_variable(3,0,nbVariable,15)))
print((cell_to_variable(3,1,nbVariable,15)))
print((cell_to_variable(3,2,nbVariable,15)))
print((cell_to_variable(4,0,nbVariable,15)))
print((cell_to_variable(4,2,nbVariable,15)))
print((cell_to_variable(5,0,nbVariable,15)))
print((cell_to_variable(5,1,nbVariable,15)))
print((cell_to_variable(5,2,nbVariable,15)))