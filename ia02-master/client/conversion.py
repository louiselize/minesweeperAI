from typing import List, Tuple


#---------------------------------------
#fonction utilitaires de conversion
#---------------------------------------
   
nbVariable = 12
nbLine = 3
nbColumn = 3
boardSize = nbColumn * nbLine
constraintsList= []

def cell_to_variable(i : int, j : int, nbVariable : int, nbColumn : int) -> int:
    return (nbVariable) * (i * nbColumn + j ) +1

def variable_to_cell(i:int, nbVariable:int, nbLine :int, nbColumn : int) -> Tuple[int]:
    if(i<=0):
        print("erreur variable > à 0")
        return 0
    if(i>nbVariable*nbLine*nbColumn):
        print("erreur variable plus grande que notre nb de variables")
        return 0
    
    var=nbVariable+1
    ligne=0
    column=0
    cmpt=0
    while(var<=nbVariable*boardSize+1):
        if (i<var):
            return [ligne,column]
        var=var+12
        cmpt=cmpt+1
        if(cmpt==nbColumn):
            column=0
            ligne=ligne+1
            cmpt=0
        else:
            column=column+1
    return 0        


