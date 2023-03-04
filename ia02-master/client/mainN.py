#from Projet.ia02.client.functions import neighbour_cells
#from Projet.ia02.client.functions import neighbour_cells
#from Projet.ia02.client.conversion import cell_to_variable
from typing import List, Tuple
import subprocess
from pprint import pprint
from collections import namedtuple
from constraints import *
import constraints
from conversion import *
from functions import *
from solveurSAT import *
from crocomine_client import *
from crocomine_client import CrocomineClient
from operator import itemgetter
from testAndSearch import *
import time 

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
# python lefichier.py (mainN.py)

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

    server = "http://croco.lagrue.ninja:80"
    group = "Groupe 30"
    members = "Hugo LESOBRE et Louise LIZE"
    password = "1234ABCD" 
    croco = CrocomineClient(server, group, members,password)

    #on passe les deux premières grilles
  

    NbGridDone=0

    while(NbGridDone<10000000):
        starttime=time.time()
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
        f = open("const.cnf","w")
        f.write("")
        f.close()

        #creation du tableau de contraintes restantes
        for i in range(nbLine):
            for j in range(nbColumn):
                remainingCase += [[i,j]]

        visited = []
        fieldKnown = []
        chordTest = []
        toTest=[]
        allInfo = []
        newInfo =[]
        mapInfo=[[{} for x in range(nbColumn)] for y in range(nbLine)]
       
        nb1=0
        nb2=0
        nb3=0
        croco_test=0
        tiger_test=0
        shark_test=0


        nbtour=-5
        notvisited=-1
        
        #creation des contraintes du jeu avec les regles de departs
        constraintsList = []
        constraintsDone=[]
        constraintsList += create_all_constraints(boardSize,nbVariable)
        
        #discover de la case de départ
        status, msg, newInfo = croco.discover(start[0],start[1])
        nbcoup=1
        allInfo += newInfo

        #on rempli notre tableau de fieldknown pour pouvoir commencer
        for cpt in range(len(allInfo)):
                    inf=allInfo[cpt]
                    pos=inf["pos"]
                    field=inf["field"]
                    
                    #1 : contrainte sur les fields que l'on connait (cases visites et '?')
                    if(pos not in fieldKnown):
                        constraintsList += create_board_field_constraints(pos[0],pos[1],nbVariable,nbColumn,field)
                        fieldKnown += [pos]
                        toTest+=[pos]
                        mapInfo[pos[0]][pos[1]]["field"]=field
                    
                    #2: contraintes sur les cases deja visites (ajouter les contraintes, faire en sorte de ne pas les visiter à nouveau)
                    if('prox_count' in inf and pos not in constraintsDone): #si la case a été visitée...
                        prox_count=inf["prox_count"]   
                        mapInfo[pos[0]][pos[1]]["prox_count"]=prox_count
                        constraintsList += create_neighbour_constraints(pos[0],pos[1],nbLine,nbColumn,boardSize,nbVariable,prox_count,field) #contraintes sur le nb d'animaux
                        constraintsList += create_visited_cells_constraints(pos[0],pos[1],nbVariable,nbColumn) #elles sont safe
                        visited += [pos]
                        if (prox_count!=[0,0,0]):
                                if(prox_count[0]+prox_count[1]+prox_count[2]==1):
                                    if(isBorderCell(pos[0],pos[1],nbLine,nbColumn)):
                                        chordTest.insert(nb1,pos)
                                    else:
                                        chordTest.insert(0,pos)
                                    nb1=nb1+1
                                elif(prox_count[0]+prox_count[1]+prox_count[2]==2):
                                    if(isBorderCell(pos[0],pos[1],nbLine,nbColumn)):
                                        chordTest.insert(nb2,pos)
                                    else:
                                        chordTest.insert(nb1,pos)
                                    nb2=nb2+1
                                elif(prox_count[0]+prox_count[1]+prox_count[2]==3):
                                    if(isBorderCell(pos[0],pos[1],nbLine,nbColumn)):
                                        chordTest.insert(nb3,pos)
                                    else:
                                        chordTest.insert(nb2,pos)
                                    nb3=nb3+1
                                    
                                else:
                                    chordTest += [pos]
                        del remainingCase[remainingCase.index(pos)] 
                        del toTest[toTest.index(pos)] 
                        constraintsDone +=[pos]                              


        #partie principale de la résolution
        while(status=="OK"):
            notvisited=0
         
            #nombre de cases que voisinantes dont on connait la land et que l'on n'a pas visité (permet de voir si on boucle à l'infini)
            for fk in fieldKnown:
                if fk not in visited: 
                    notvisited=notvisited+1

            #I) si on boucle une première fois : ajouter les contraintes de nb d'animaux dans la grille
            """
            if(nbtour==notvisited and aleatoireMoment==0 and (combin(len(remainingCase),nbTiger+nbCroco+nbShark))<10000):
                                #nbremainingCase = boardSize-(len(constraintsDone)+(nbAnimals-nbTiger-nbCroco-nbShark))
                                #print(combin(len(remainingCase),nbTiger+nbCroco+nbShark))
                                constraintsList += create_number_animals_constraints(remainingCase,nbTiger,nbCroco,nbShark,nbLine,nbColumn,boardSize,nbVariable)
                                aleatoireMoment=1
                                print("contraintes nb animaux")
            """
            if(nbtour==notvisited and aleatoireMoment==0 and ((croco_test==0 and (combin(len(remainingCase),nbCroco))<7500)or((shark_test==0 and (combin(len(remainingCase),nbShark))<7500)) or (tiger_test==0 and (combin(len(remainingCase),nbTiger))<7500))):
                                print(combin(len(remainingCase),nbCroco))
                                print(combin(len(remainingCase),nbShark))
                                print(combin(len(remainingCase),nbTiger))
                                if((combin(len(remainingCase),nbCroco))<7500 and croco_test==0):
                                    constraintsList += create_number_crocos_constraints(remainingCase,nbCroco,nbLine,nbColumn,boardSize,nbVariable)
                                    print("combi croco")
                                    croco_test=1
                                if((combin(len(remainingCase),nbShark))<7500)and shark_test==0:
                                    constraintsList += create_number_sharks_constraints(remainingCase,nbShark,nbLine,nbColumn,boardSize,nbVariable)
                                    print("combi shark")
                                    shark_test=1
                                if((combin(len(remainingCase),nbTiger))<7500 and tiger_test==0):
                                    constraintsList += create_number_tigers_constraints(remainingCase,nbTiger,nbLine,nbColumn,boardSize,nbVariable)
                                    print("combi tiger")
                                    tiger_test=1
                                if(tiger_test+shark_test+croco_test==3):
                                    aleatoireMoment=1


            #II) si on boucle une deuxieme fois : on regarde si on peut dire que les cases dont on ne connait rien ne contiennent pas d'animaux
            elif(nbtour==notvisited and aleatoireMoment==1):
                print("contrainte case non connues")
                for cell in remainingCase:
                    isSat,constraintsList,newInfo,visited,status= noAnimal_test(cell,nbVariable,nbColumn,boardSize,constraintsList,visited,croco,status)
                    if(isSat==0):
                        nbcoup=nbcoup+1
                    #1 : contrainte sur les fields que l'on connait (cases visites et '?')
                    allInfo+=newInfo
                    for cmpt in newInfo:
                        pos=cmpt["pos"]
                        field=cmpt["field"]
                        if(pos not in fieldKnown):
                            constraintsList += create_board_field_constraints(pos[0],pos[1],nbVariable,nbColumn,field)
                            fieldKnown += [pos]
                            toTest+=[pos]
                            mapInfo[pos[0]][pos[1]]["field"]=field
                    
                        #2: contraintes sur les cases déjà visites (car on connait mtn les nb d'animaux, et on sait qu'elles sont safe)
                        if('prox_count' in cmpt and pos not in constraintsDone): #si la case a été visitée...
                            prox_count=cmpt["prox_count"]   
                            mapInfo[pos[0]][pos[1]]["prox_count"]=prox_count
                            constraintsList += create_neighbour_constraints(pos[0],pos[1],nbLine,nbColumn,boardSize,nbVariable,prox_count,field) #contraintes sur le nb d'animaux
                            constraintsList += create_visited_cells_constraints(pos[0],pos[1],nbVariable,nbColumn) #elles sont safe
                            visited += [pos]
                            if (prox_count!=[0,0,0]):
                                if(prox_count[0]+prox_count[1]+prox_count[2]==1):
                                    if(isBorderCell(pos[0],pos[1],nbLine,nbColumn)):
                                        chordTest.insert(nb1,pos)
                                    else:
                                        chordTest.insert(0,pos)
                                    nb1=nb1+1
                                elif(prox_count[0]+prox_count[1]+prox_count[2]==2):
                                    if(isBorderCell(pos[0],pos[1],nbLine,nbColumn)):
                                        chordTest.insert(nb2,pos)
                                    else:
                                        chordTest.insert(nb1,pos)
                                    nb2=nb2+1
                                elif(prox_count[0]+prox_count[1]+prox_count[2]==3):
                                    if(isBorderCell(pos[0],pos[1],nbLine,nbColumn)):
                                        chordTest.insert(nb3,pos)
                                    else:
                                        chordTest.insert(nb2,pos)
                                    nb3=nb3+1
                                    
                                else:
                                    chordTest += [pos]
                            del remainingCase[remainingCase.index(pos)] 
                            constraintsDone +=[pos]
                            del toTest[toTest.index(pos)]
                
                aleatoireMoment=2

            #III) Si on boucle encore : Gestion de l'aléatoire
           
            elif(nbtour==notvisited and (aleatoireMoment==2 or (combin(len(remainingCase),nbTiger+nbCroco+nbShark))>=10000)):
                                print("aleatoire")
                                #input()
                                dict_pos=['i','j']
                                proba_case={}
                                #On crée un dictionnaire qui aura pour clé les coordonnées d'une case et pour valeur la ""probabilité"" qu'un animal s'y trouve.
                                #Le dictionnaire est crée avec les cases qui ne sont pas encore visités mais sur lesquelles on a des informations.
                                # Si on sait le field de la case alors il y a forcément au moins une case découverte autour.
                                for i in range(nbLine):
                                    for j in range(nbColumn):
                                        if ("field" in mapInfo[i][j]) and not ("nbCroco" in mapInfo[i][j]) and not ("nbShark" in mapInfo[i][j]) and not ("nbTiger" in mapInfo[i][j]) and not ("prox_count" in mapInfo[i][j]): #case non visitée
                                            proba_case[f"{i},{j}"]=0
                                #Cas ou field découvert mais aucun prox_count sur les voisins (case entouré d'animaux ne doit pas être considéré comme safe).
                                #On enlève donc ces cases du dictionnaire.
                                #Si ce cas n'était pas traité alors certaines cases seraient désigné comme "safe" par l'aléatoire alors qu'on manque juste d'information sur ces dernières.
                                proba_case_copy=proba_case.copy()
                                for key in proba_case_copy.keys():
                                    coord=key.split(',')
                                    #input()
                                    v=neighbour_cells(int(coord[0]),int(coord[1]),nbLine,nbColumn)
                                    if not oneOfGivenCoordIsGivingInfo(v,mapInfo):
                                        proba_case.pop(key)
                               
                                #input()

                                nbSea=0
                                nbLand=0
                                voisinsCasesNotVisited=[]

                                for i in range(nbLine):
                                    for j in range(nbColumn):
                                        #On récupère les voisins des cases non visitées
                                        if not ("nbCroco" in mapInfo[i][j]) and not ("nbShark" in mapInfo[i][j]) and not ("nbTiger" in mapInfo[i][j]) and not ("prox_count" in mapInfo[i][j]): #case non visitée
                                            voisins=[]
                                            voisins+=neighbour_cells(i,j,nbLine,nbColumn)
                                            #On fait attention à ne pas avoir de doublon dans nos "voisins" pour éviter de fausser le calcul de la "probabilité"
                                            for v in voisins:
                                                if v not in voisinsCasesNotVisited:
                                                    voisinsCasesNotVisited.append(v)
                                #Pour toutes les cases voisines qui nous donnent de l'information (if "prox_count" ....)sur les cases qu'on cherche à découvrir
                                for voisins in voisinsCasesNotVisited:
                                        i=voisins[0]
                                        j=voisins[1]
                                        #input()
                                        if "prox_count" in mapInfo[i][j]:
                                            casesVoisines=neighbour_cells(i,j,nbLine,nbColumn)
                                            (nbT,nbS,nbC)=remainingAnimalsInNeighbourood(casesVoisines,mapInfo,i,j)
                                            (nbSea,nbLand)=fieldCptOfNotVisited(casesVoisines,mapInfo)
                                            proba_case=probaMaker(casesVoisines,mapInfo,proba_case,nbT,nbS,nbC,nbSea,nbLand)
                                min=10
                                pos_a_dec=""
                                discovered=False
                                #On cherche la case ayant la plus petite probabilité de contenir un animal parmis toutes les cases dans notre dictionnaire.
                                for posD,probaD in proba_case.items():
                                    coord=posD.split(',')
                                    for case in allInfo:
                                        if case["pos"][0]==int(coord[0]) and case["pos"][1]==int(coord[1]):
                                            if 'prox_count' in case:
                                                discovered=True
                                    if probaD<min and discovered==False:
                                        min=probaD
                                        pos_a_dec=posD
                                #Une fois trouvé, on découvre cette case et on ajoute à notre base de clause les clauses correspondantes.
                                coord_a_dec=pos_a_dec.split(',')
                                status, msg, newInfo = croco.discover(int(coord_a_dec[0]),int(coord_a_dec[1]))
                                constraintsList+=[[(cell_to_variable(int(coord_a_dec[0]),int(coord_a_dec[1]),nbVariable,nbColumn)+1)]]
                                constraintsList+=[[(cell_to_variable(int(coord_a_dec[0]),int(coord_a_dec[1]),nbVariable,nbColumn))+3]]
                                constraintsList+=[[(cell_to_variable(int(coord_a_dec[0]),int(coord_a_dec[1]),nbVariable,nbColumn))+5]]
                                #aleatoireMoment=0
                                allInfo+=newInfo
                                visited+=[coord_a_dec]
                                
            nbtour=0
            for cpt in fieldKnown:
                if(status=="OK"):

                #on recupere toutes les infos que l'on a et l'on en cree des contraintes
                    for cmpt in newInfo:
                        pos=cmpt["pos"]
                        field=cmpt["field"]

                        #1 : contrainte sur les fields que l'on connait (cases visites et '?')
                        if(pos not in fieldKnown):
                            constraintsList += create_board_field_constraints(pos[0],pos[1],nbVariable,nbColumn,field)
                            fieldKnown += [pos]
                            toTest+=[pos]
                            mapInfo[pos[0]][pos[1]]["field"]=field
                                        
                        #2: contraintes sur les cases déjà visites (car on connait mtn les nb d'animaux, et on sait qu'elles sont safe)
                        if('prox_count' in cmpt and pos not in constraintsDone): #si la case a été visitée...
                            prox_count=cmpt["prox_count"]  
                            mapInfo[pos[0]][pos[1]]["prox_count"]=prox_count
                            constraintsList += create_neighbour_constraints(pos[0],pos[1],nbLine,nbColumn,boardSize,nbVariable,prox_count,field) #contraintes sur le nb d'animaux
                            constraintsList += create_visited_cells_constraints(pos[0],pos[1],nbVariable,nbColumn) #elles sont safe
                            visited += [pos]
                            if (prox_count!=[0,0,0]):
                                if(prox_count[0]+prox_count[1]+prox_count[2]==1):
                                    if(isBorderCell(pos[0],pos[1],nbLine,nbColumn)):
                                        chordTest.insert(nb1,pos)
                                    else:
                                        chordTest.insert(0,pos)
                                    nb1=nb1+1
                                elif(prox_count[0]+prox_count[1]+prox_count[2]==2):
                                    if(isBorderCell(pos[0],pos[1],nbLine,nbColumn)):
                                        chordTest.insert(nb2,pos)
                                    else:
                                        chordTest.insert(nb1,pos)
                                    nb2=nb2+1
                                elif(prox_count[0]+prox_count[1]+prox_count[2]==3):
                                    if(isBorderCell(pos[0],pos[1],nbLine,nbColumn)):
                                        chordTest.insert(nb3,pos)
                                    else:
                                        chordTest.insert(nb2,pos)
                                        nb3=nb3+1

                                else:
                                    chordTest += [pos]
                            del remainingCase[remainingCase.index(pos)]
                            constraintsDone +=[pos] 
                            del toTest[toTest.index(pos)]
                    newInfo=[]   
                    #print(mapInfo)

                    #GESTION DU CHORD
                    var=0
                    for cmpt in chordTest:
                        neighbour = neighbour_cells(cmpt[0],cmpt[1],nbLine,nbColumn)
                        sumNbCroco =0
                        sumNbShark =0
                        sumNbTiger =0
                        emptyNeighbour=0
                        if(var!=1):
                            for cell in neighbour:
                                if ("nbCroco" in mapInfo[cell[0]][cell[1]]):
                                    sumNbCroco = sumNbCroco + mapInfo[cell[0]][cell[1]]["nbCroco"]
                                if ("nbTiger" in mapInfo[cell[0]][cell[1]]):
                                    sumNbTiger = sumNbTiger + mapInfo[cell[0]][cell[1]]["nbTiger"]
                                if ("nbShark" in mapInfo[cell[0]][cell[1]]):
                                    sumNbShark = sumNbShark + mapInfo[cell[0]][cell[1]]["nbShark"]
                                if cell in toTest:
                                    emptyNeighbour=1
                            if (emptyNeighbour==0):
                                del chordTest[chordTest.index(cmpt)]

                            elif (mapInfo[cmpt[0]][cmpt[1]]["prox_count"]==[sumNbTiger,sumNbShark,sumNbCroco]):
                                    status, msg, infos = croco.chord(cmpt[0],cmpt[1])
                                    nbcoup=nbcoup+1
                                    if(status=="GG"):
                                        print("gg")
                                    newInfo += infos
                                    nbtour=nbtour+5                      
                                    del chordTest[chordTest.index(cmpt)]     
                                    var=1
                    cell=cpt
                if cell in toTest and status=="OK":
                    #si il n'y a plus d'animaux, tout découvrir
                    if(nbTiger==0 and nbCroco==0 and nbShark==0):
                                index=0
                                while(status!="GG"):
                                    cmpt=remainingCase[index]
                                    status, msg, infos = croco.discover(cmpt[0],cmpt[1])
                                    nbcoup=nbcoup+1
                                    #print(status, msg)
                                    #pprint(infos)
                                    index=index+1
                                    #print("boucle finale ppour gagner")
                            
                            
                        # si le nb d'animaux restants = 0 faire des contraintes de noAnimal
                        #constraintsNoAnimalDone sert à ne passer qu'une fois dans la boucle et ne pas rajouter des contraintes en boucle
                    elif var!=1:
                            if(nbCroco==0 and constraintsNoCrocoDone==0):
                                    constraintsList+= create_no_Croco_constraints(remainingCase,nbLine,nbColumn,boardSize,nbVariable)
                                    constraintsNoCrocoDone=1
                                

                            if(nbShark==0 and constraintsNoSharkDone==0):
                                    constraintsList+= create_no_Shark_constraints(remainingCase,nbLine,nbColumn,boardSize,nbVariable)
                                    constraintsNoSharkDone=1
                                    

                            if(nbTiger==0 and constraintsNoTigerDone==0):
                                    constraintsList+= create_no_Tiger_constraints(remainingCase,nbLine,nbColumn,boardSize,nbVariable)
                                    constraintsNoTigerDone=1            
                        
                
                           

                            # FONCTION POUR TESTER CHAQUE CASE ET S'IL ELLES SONT UNSAT -> DISCOVER / GUESS   
                            #
                            #
                            # A FAIRE : TESTER SI LA CASE EST MERE OU TERRE
                            # COMME CA ON EVITE UN APPEL A GOPHERSAT 
                            #
                            # A FAIRE 2 : SI IL N'Y A PLUS DE CROCO DE TIGRE OU DE SHARK, NE PAS APPELER GOPHERSAT POUR CET/CES ANIMAL/ANIMAUX
                            #
                            #
                            cellField = mapInfo[cell[0]][cell[1]]["field"]
                            if(cellField=="land"):
                                #si on est sur la terre et qu'il n'y a plus de croco ou de tigre, on peut discover
                                if(nbCroco==0 and nbTiger==0):
                                    status, msg, newInfo = croco.discover(cell[0],cell[1])
                                    nbcoup=nbcoup+1
                                    #print(status, msg)
                                    #pprint(infos)
                                    allInfo+=newInfo
                                    visited += [cell]
                                else:
                                    #NO ANIMAL TEST
                                    isSat,constraintsList,newInfo,visited,status= noAnimal_test(cell,nbVariable,nbColumn,boardSize,constraintsList,visited,croco,status)
                                    allInfo+=newInfo
                            
                                   

                                    #si il n'y a pas de croco, il ne peut y avoir potentiellement que des tigres
                                    if(isSat):
                                        if(nbCroco==0):
                                            isSat,constraintsList,newInfo,visited,nbTiger,remainingCase,status=is_there_tiger_test(cell,nbVariable,nbColumn,boardSize,constraintsList,visited,croco,nbTiger,remainingCase,status)
                                            allInfo+=newInfo
                                            if(isSat):
                                                nbtour=nbtour+1  
                                            else :
                                                del toTest[toTest.index(cell)]
                                                mapInfo[cell[0]][cell[1]]['nbTiger']=1
                                                nbcoup=nbcoup+1
                                                nbtour=nbtour-1
               
                                        
                                        #si il n'y a pas de tigre, il ne peut y avoir potentiellement que des crocos
                                        elif(nbTiger==0):
                                            isSat,constraintsList,newInfo,visited,nbCroco,remainingCase,status=is_there_Croco_test(cell,nbVariable,nbColumn,boardSize,constraintsList,visited,croco,nbCroco,remainingCase,status)
                                            allInfo+=newInfo
                                            if(isSat):
                                                nbtour=nbtour+1
                                            else:
                                                del toTest[toTest.index(cell)]
                                                mapInfo[cell[0]][cell[1]]['nbCroco']=1
                                                nbcoup=nbcoup+1
                                                nbtour=nbtour-1



                                                
                                        #On teste d'abord s'il y a des crocos puis des tigres
                                        elif(nbCroco>nbTiger):
                                            isSat,constraintsList,newInfo,visited,nbCroco,remainingCase,status=is_there_Croco_test(cell,nbVariable,nbColumn,boardSize,constraintsList,visited,croco,nbCroco,remainingCase,status)
                                            allInfo+=newInfo
                                                
                                            if(isSat):
                                                    isSat,constraintsList,newInfo,visited,nbTiger,remainingCase,status=is_there_tiger_test(cell,nbVariable,nbColumn,boardSize,constraintsList,visited,croco,nbTiger,remainingCase,status)
                                                    if(isSat):
                                                        nbtour=nbtour+1
                                                    else:
                                                        del toTest[toTest.index(cell)]
                                                        mapInfo[cell[0]][cell[1]]['nbTiger']=1
                                                        nbcoup=nbcoup+1
                                                        nbtour=nbtour-1


                                            else:
                                                del toTest[toTest.index(cell)]
                                                mapInfo[cell[0]][cell[1]]['nbCroco']=1
                                                nbcoup=nbcoup+1
                                                nbtour=nbtour-1


                                        
                                        #On teste d'abord s'il y a des tigres puis des crocos
                                        elif(nbCroco<=nbTiger):
                                            isSat,constraintsList,newInfo,visited,nbTiger,remainingCase,status=is_there_tiger_test(cell,nbVariable,nbColumn,boardSize,constraintsList,visited,croco,nbTiger,remainingCase,status)
                                            allInfo+=newInfo
                                            if(isSat):
                                                    isSat,constraintsList,newInfo,visited,nbCroco,remainingCase,status=is_there_Croco_test(cell,nbVariable,nbColumn,boardSize,constraintsList,visited,croco,nbCroco,remainingCase,status)
                                                    if(isSat):
                                                        nbtour=nbtour+1
                                                    else:
                                                        del toTest[toTest.index(cell)]
                                                        mapInfo[cell[0]][cell[1]]['nbCroco']=1
                                                        nbcoup=nbcoup+1
                                                        nbtour=nbtour-1
                                            else:
                                                del toTest[toTest.index(cell)]
                                                mapInfo[cell[0]][cell[1]]['nbTiger']=1
                                                nbcoup=nbcoup+1
                                                nbtour=nbtour-1
                                    else:
                                        nbcoup=nbcoup+1
                                        nbtour=nbtour-1

                            elif(cellField=="sea"): 
                                if(nbCroco==0 and nbShark==0):
                                    status, msg, newInfo = croco.discover(cell[0],cell[1])
                                    nbcoup=nbcoup+1
                                    #print(status, msg)
                                    #pprint(infos)
                                    allInfo+=newInfo
                                    visited += [cell]
                                    nbtour=nbtour-1
                                else:
                                    #NO ANIMAL TEST
                                    isSat,constraintsList,newInfo,visited,status= noAnimal_test(cell,nbVariable,nbColumn,boardSize,constraintsList,visited,croco,status)
                                    allInfo+=newInfo

                                    #si il n'y a pas de croco, il ne peut y avoir potentiellement que des requins
                                    if(isSat):
                                        if(nbCroco==0):
                                            isSat,constraintsList,newInfo,visited,nbShark,remainingCase,status=is_there_Shark_test(cell,nbVariable,nbColumn,boardSize,constraintsList,visited,croco,nbShark,remainingCase,status)
                                            allInfo+=newInfo
                                            if(isSat):
                                                nbtour=nbtour+1   
                                            else:
                                                del toTest[toTest.index(cell)]
                                                mapInfo[cell[0]][cell[1]]['nbShark']=1
                                                nbcoup=nbcoup+1
                                                nbtour=nbtour-1
                  
                                        
                                        #si il n'y a pas de requin, il ne peut y avoir potentiellement que des crocos
                                        elif(nbShark==0):
                                            isSat,constraintsList,newInfo,visited,nbCroco,remainingCase,status=is_there_Croco_test(cell,nbVariable,nbColumn,boardSize,constraintsList,visited,croco,nbCroco,remainingCase,status)
                                            allInfo+=newInfo
                                            if(isSat):
                                                nbtour=nbtour+1
                                            else:
                                                del toTest[toTest.index(cell)]
                                                mapInfo[cell[0]][cell[1]]['nbCroco']=1
                                                nbcoup=nbcoup+1
                                                nbtour=nbtour-1

                                                
                                        #On teste d'abord s'il y a des crocos puis des requins
                                        elif(nbCroco>nbShark):
                                            isSat,constraintsList,newInfo,visited,nbCroco,remainingCase,status=is_there_Croco_test(cell,nbVariable,nbColumn,boardSize,constraintsList,visited,croco,nbCroco,remainingCase,status)
                                            allInfo+=newInfo
                                            if(isSat):
                                                    isSat,constraintsList,newInfo,visited,nbShark,remainingCase,status=is_there_Shark_test(cell,nbVariable,nbColumn,boardSize,constraintsList,visited,croco,nbShark,remainingCase,status)
                                                    allInfo+=newInfo
                                                    if(isSat):
                                                        nbtour=nbtour+1
                                                    else:
                                                        del toTest[toTest.index(cell)]
                                                        mapInfo[cell[0]][cell[1]]['nbShark']=1
                                                        nbcoup=nbcoup+1
                                                        nbtour=nbtour-1
                                            else:
                                                del toTest[toTest.index(cell)]
                                                mapInfo[cell[0]][cell[1]]['nbCroco']=1
                                                nbcoup=nbcoup+1
                                                nbtour=nbtour-1


                                        
                                        #On teste d'abord s'il y a des requins puis des crocos
                                        elif(nbCroco<=nbShark):
                                            isSat,constraintsList,newInfo,visited,nbShark,remainingCase,status=is_there_Shark_test(cell,nbVariable,nbColumn,boardSize,constraintsList,visited,croco,nbShark,remainingCase,status)
                                            allInfo+=newInfo
                                            if(isSat):
                                                    isSat,constraintsList,newInfo,visited,nbCroco,remainingCase,status=is_there_Croco_test(cell,nbVariable,nbColumn,boardSize,constraintsList,visited,croco,nbCroco,remainingCase,status)
                                                    allInfo+=newInfo
                                                    if(isSat):
                                                        nbtour=nbtour+1      
                                                    else:
                                                        del toTest[toTest.index(cell)]
                                                        mapInfo[cell[0]][cell[1]]['nbCroco']=1
                                                        nbcoup=nbcoup+1
                                                        nbtour=nbtour-1
                                            else:
                                                del toTest[toTest.index(cell)]
                                                mapInfo[cell[0]][cell[1]]['nbShark']=1
                                                nbcoup=nbcoup+1
                                                nbtour=nbtour-1

                                    else:
                                        nbcoup=nbcoup+1  
                                        nbtour=nbtour-1
      


        ntime = time.time()
        letemps= ntime-starttime
        if(status=="GG"):
            print("GG")
        print("TEMPS DEX",letemps)
        print("nb coup",nbcoup)
                                                     


                                            
                                                
#-----MAIN------
        
nbVariable=7
test(nbVariable)
print("FINI")
#print((cell_to_variable(0,7,nbVariable,9)))
#print((cell_to_variable(0,9,nbVariable,9)))
#print((cell_to_variable(1,7,nbVariable,9)))
#print((cell_to_variable(1,8,nbVariable,9)))
#print((cell_to_variable(1,9,nbVariable,9)))

