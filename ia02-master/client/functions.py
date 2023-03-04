from typing import List, Tuple
from conversion import *
from pprint import pprint
#------------------------------------------------------------------
#Fonction de voisinage : pour chaque case on calcule ses 8 voisins, 
#                        conditions sur les cases en bordure
#------------------------------------------------------------------

def neighbour_cells(i : int, j : int, nbLine : int, nbColumn) ->List[List[int]]:
    neighbour_list = []
    cpt=0

    case1_i=i-1
    case1_j=j-1
    if(case1_i>=0 and case1_i<nbLine and case1_j>=0 and case1_j<nbColumn):
        neighbour_list += [[case1_i,case1_j]]
    
    case2_i=i-1
    case2_j=j
    if(case2_i>=0 and case2_i<nbLine and case2_j>=0 and case2_j<nbColumn):
        neighbour_list += [[case2_i,case2_j]]
    
    case3_i=i-1
    case3_j=j+1
    if(case3_i>=0 and case3_i<nbLine and case3_j>=0 and case3_j<nbColumn):
        neighbour_list += [[case3_i,case3_j]]
    
    case4_i=i
    case4_j=j-1
    if(case4_i>=0 and case4_i<nbLine and case4_j>=0 and case4_j<nbColumn):
        neighbour_list +=[[case4_i,case4_j]]
    
    case6_i=i
    case6_j=j+1
    if(case6_i>=0 and case6_i<nbLine and case6_j>=0 and case6_j<nbColumn):
        neighbour_list += [[case6_i,case6_j]]
    
    case7_i=i+1
    case7_j=j-1
    if(case7_i>=0 and case7_i<nbLine and case7_j>=0 and case7_j<nbColumn):
        neighbour_list += [[case7_i,case7_j]]
    
    case8_i=i+1
    case8_j=j
    if(case8_i>=0 and case8_i<nbLine and case8_j>=0 and case8_j<nbColumn):
        neighbour_list += [[case8_i,case8_j]]

    case9_i=i+1
    case9_j=j+1
    if(case9_i>=0 and case9_i<nbLine and case9_j>=0 and case9_j<nbColumn):
        neighbour_list += [[case9_i,case9_j]]

    return neighbour_list



def remainingAnimalsInNeighbourood(cellsVoisines,mapInfo,x,y) -> tuple[int,int]:
    (nbT,nbS,nbC)=mapInfo[x][y]["prox_count"]
    for cell in cellsVoisines:
        i=cell[0]
        j=cell[1]
        if ("nbCroco" in mapInfo[i][j]) or ("nbShark" in mapInfo[i][j]) or ("nbTiger" in mapInfo[i][j]) or ("prox_count" in mapInfo[i][j]): #case non visitée                 
            if ("nbCroco" in mapInfo[i][j]):
                if mapInfo[i][j]['nbCroco']==1:
                    #input()
                    nbC-=1
            elif ("nbTiger" in mapInfo[i][j]):
                if mapInfo[i][j]['nbTiger']==1:
                    #input()
                    nbT-=1
            elif ("nbShark" in mapInfo[i][j]):
                if mapInfo[i][j]['nbShark']==1:
                    #input()
                    nbS-=1

    return (nbT,nbS,nbC)

def fieldCptOfNotVisited(cellsVoisines, mapInfo) -> tuple[int,int]:
    nbT_cpt=0
    nbS_cpt=0
    nbC_cpt=0
    nbSea=0
    nbField=0        
    for cell in cellsVoisines:      #         #
        i=cell[0]
        j=cell[1]
        if not ("nbCroco" in mapInfo[i][j]) and not ("nbShark" in mapInfo[i][j]) and not ("nbTiger" in mapInfo[i][j]) and not ("prox_count" in mapInfo[i][j]): #case non visitée
            if mapInfo[i][j]["field"]=='sea':
                nbSea+=1
            else:
                nbField+=1
    return (nbSea,nbField)

def probaMaker(cellsVoisines, mapInfo, proba_case,nbT,nbS,nbC,nbSea,nbLand):
    print(f"tigre:{nbT}  Requin:{nbS}   Croco:{nbC}")
    for cell in cellsVoisines:      #
        i=cell[0]
        j=cell[1]
        if not ("nbCroco" in mapInfo[i][j]) and not ("nbShark" in mapInfo[i][j]) and not ("nbTiger" in mapInfo[i][j]) and not ("prox_count" in mapInfo[i][j]): #case non visitée                
            if mapInfo[i][j]["field"]=='sea':
                proba_case[f"{i},{j}"]+=(nbS/nbSea)+(nbC/(nbSea+nbLand))
            else:
                proba_case[f"{i},{j}"]+=(nbT/nbLand)+(nbC/(nbSea+nbLand))
    return proba_case
    
#pris sur : https://python.jpvweb.com/python/mesrecettespython/doku.php?id=combinaisons
def combin(n, k):
    """Nombre de combinaisons de n objets pris k a k"""
    if k > n//2:
        k = n-k
    x = 1
    y = 1
    i = n-k+1
    while i <= n:
        x = (x*i)//y
        y += 1
        i += 1
    return x

def isBorderCell(i : int, j : int, nbLine : int, nbColumn):
    if(i==0 or j==0 or i==nbLine-1 or j==nbColumn-1):
        return 1
    else:
        return 0

def oneOfGivenCoordIsGivingInfo(coords,mapInfo) -> bool:
    for coord in coords:
        i=coord[0]
        j=coord[1]
        if "prox_count" in mapInfo[i][j]:
            return True
    return False

