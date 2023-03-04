POUR LANCER:
-être dans le dossier client
-python mainN.py

FONCTIONNALITES:
-GOPHERSAT
-chord (tri des chords selon le nombre de prox_count)
-GESTION ALEATOIRE (optimise le % de réussite)
-Choix du test à faire (tester si présence de croco,tigre,requin selon le nombre d’animal restant)
-Contraintes nb animaux restants sur la map si possible dans un temps raisonnable
-Les chords sur les cases en bordure ne se font pas en priorité

Nous avons fait le choix de privilégier la qualité de résolution (% de grille résolue) à la quantité.

#################################################################################################################################################################
###                                                                  EXPLICATION DES VARIABLES DIMACS                                                         ###
#################################################################################################################################################################

Variable 1x : tiger
Variable 2x : notiger
Variable 3x : croco
Variable 4x : nocroco
Variable 5x : shark
Variable 6x : noshark
Variable 7x : sea

Particularité de notre programme, nous utilisons 2 variables différentes pour une variable et son contraire.
Ainsi, toute une variable "négative" -tiger, -croco, -notiger etc. Indique que l'on a pas d'information sur cette variable.
Dès lors que l'on est sûr de notre information on passe cette variable en "positif".

Exemple: 
    Pas d'information sur tiger:
        -tiger, -notiger
    Pas de tigre:
        -tiger, notiger
    Tigre:
        tiger, -notiger

#################################################################################################################################################################
###                                                                      DEROULEMENT DU PROGRAMME                                                             ###
#################################################################################################################################################################

1. Demande de grille, récupération des informations de cette dernière, initialisation des variables.

2. Création des contraintes sur les "fields connu" (cases visités et '?')

3. Contraintes sur les cases déjà visités (ajouter les contraintes, faire en sorte qu'on ne puisse pas les visiter à nouveau etc.). On regarde aussi si on peut faire un chord. Les "chord" sont triés en fonction du "prox_count" afin de découvrir le maximum de cases d'un coup.

4. Tant que l'on ne boucle pas:
    1. On récupère les infos que l'on a et on crée les contraintes correspondantes
    2. Test chaque case (dont on connait le terrain mais que l'on a pas encore découverte) avec gophersat et certaines contraintes, si le résultat est unsat alors on peut en tirer des conclusions et donc guess/discover
        - Si on est sur la terre
            - S'il n'y a plus de croco ou tigre alors on peut discover
            - S'il n'y a plus de croco alors il n'y a potentiellement que des tigres et inversement
            - Tests si il y a des crocos et des tigres (avec les fonctions expliqués par la suite)
        - Si on est sur la mer
            - Même logique mais avec les requins et crocodiles
            
        (Dans les 2 cas, on test en premier les animaux qui sont le plus présent)

5. Si on boucle sur le 2. alors on ajoute les contraintes du nombre d'animaux dans la grille (en utilisant combinations()) et à conditions que le nombre de clauses produites ne soit pas trop grand. On retourne dans le corps principal du 2.

6. Si on boucle encore on regarde si on ne peut pas déduire que les cases à découvrir ne contiennent finalement pas d'animaux. On retourne dans le corps principal du 2.

7. Enfin, si l'on boucle encore, on passe à l'aléatoire (l'aléatoire choisira la case à discover pour laquelle il est le moins probable de se tromper). On retourne dans le corps principal du 2.

8. Quand la grille est finie, on en charge une autre et on recommence



#################################################################################################################################################################
###                                                                      EXPLICATION DES FONCTIONS                                                            ###
#################################################################################################################################################################

    functions.py
        neighbour_cells(): 
            Renvoie les coordonnées des voisins de la cellule passée en argument

        remainingAnimalsIsNeighbourood(): 
            Pour une cellule donnée, renvoie le nombre d'animaux restant à découvrir dans ses voisins (en tenant compte des animaux déjà découvert).

        fieldCptOfNotVisited(): 
            Pour une cellule donnée, renvoie le nombre de case eau et de case terre non visitée (dans les cases voisines).

        probaMaker(): 
            Pour une case donnée et selon les valeurs calculées avec les 2 fonctions précédentes calcul les probabilités qu'une case comporte un animal et l'additionne aux probabilités calculés précédemment (lors du même coup) pour cette case.

        combin():
            Permet de calculer le nombre de combinaisons de n parmis k sans avoir à le calculer. Cette information nous permettra de ne pas faire des combinaisons qui seraient trop lourdes.

        isBorderCell(): 
            Renvoie vrai si une case est en bordure, faux sinon.

        oneOfGivenCoordIsGivingInfo(): 
            Renvoie true si au moins une case dans la liste de case donnée donne des informations (possède prox_count)
    
    testAndSearch.py
        noAnimal_test():
            Test sur une case si il n'y a pas d'animaux.
                Ajout la contrainte Croco ou Requin ou Tigre dans notre base de clause, appel gophersat, si unsat alors pas de Croco, ni de Requin et ni de Tigre => Ajout de ces informations à notre base de clause.

        is_there_tiger_test():
            Test sur une case si il y a un tigre.
                Ajout de noTiger dans notre base de clause, test sur gophersat, si unsat alors il y a un Tigre. Donc on fait un guess sur la case et ajoute les informations à notre base de clause.

        is_there_Croco_test():
            Test sur une case si il y a un Croco.
                Ajout de noCroco dans notre base de clause, test sur gophersat, si unsat alors il y a un Croco. Donc on fait un guess sur la case et ajoute les informations à notre base de clause.

        is_there_Shark_test():
            Test sur une case si il y a un Requin.
                Ajout de noShark dans notre base de clause, test sur gophersat, si unsat alors il y a un Shark. Donc on fait un guess sur la case et ajoute les informations à notre base de clause.

    solveurSat.py
        clauses_to_dimacs():
            Ecrit nos clauses sous format dimacs. Renvoie un string qui contient ce que l'on va écrire dans le dimacs.

        write_dimacs_files():
            Ecrit une chaîne de caractere donnée en argument dans un fichier (nom donné en argument: const.cnf).

        exec_gophersat():
            Execute gophersat avec un fichier donné en argument (const.cnf dans notre cas)
    
    conversion.py
        cell_to_variable():
            Converti les coordoonées donnée en argument en un entier qui représente la première variable utilisée dans notre dimacs pour cette case.

        variable_to_cell():
            Opération inverse de la fonction précendte. A partir d'une variable retourne la coordonnée de la case à laquelle elle se réfère.

    constraints.py
        create_tiger_constraints():
            Crée pour chaque case, les contraintes de bases sur les tigres.
            Exemple: tigre=>noshark
        create_croco_constraints():
            Crée pour chaque case, les contraintes de bases sur les crocos.
            Exemple: croco=>noshark

        create_shark_constraints():
            Crée pour chaque case, les contraintes de bases sur les requins.
            Exemple: shark=>-noshark

        create_field_and_animals_constraints():
            Crée pour chaque case, les contraintes de bases liées au terrain et aux animaux (requin que dans l'eau etc.)

        create_all_constraints():
            Appelle les 4 fonctions précédentes afin de créer chaque contraintes.

        create_board_field_constraints():
            Met la variable sea à vrai si la case aux coordonnées passé en paramètre est sea, land sinon.

        create_neighbour_constraints():
            Crée les contraintes suivant l'exemple suivant: 
                il y a 3 animaux dans le voisinages ↔ il y a 5 cases sans animaux

        create_visited_cells_constraints():
            Met à vrai notiger, nocroco, noshark dans notre base de clauses. Utile lorsqu'on appelle une case et que l'on sait qu'elle est vide.

        create_no_Croco_constraints():
            Pour toutes les cases restantes, met nocroco à vrai.
            Il n'y a pas de croco sur les cases restantes

        create_no_Shark_constraints():
            Pour toutes les cases restantes, met noshark à vrai.
            Il n'y a pas de requin sur les cases restantes

        create_no_Tiger_constraints():
            Pour toutes les cases restantes, met tigre à vrai.
            Il n'y a pas de tigre sur les cases restantes

        create_number_animals_constraints():
            Crée des contraintes sur les cases restantes en utilisant le nombre d'animaux restant et combinations()

        create_number_sharks_constraints():
            Crée des contraintes sur les cases restantes en utilisant le nombre de requins restant et combinations()

        create_number_tigers_constraints():
            Crée des contraintes sur les cases restantes en utilisant le nombre de tigres restant et combinations()

        create_number_croco_consteaints():
            Crée des contraintes sur les cases restantes en utilisant le nombre de crocodiles restant et combinations()


#################################################################################################################################################################
###                                                                  PISTES D'AMELIORATIONS                                                                   ###
#################################################################################################################################################################

- Optimiser encore et encore le code ainsi que notre méthode de résolution pour accroître la rapidité de résolutions des grilles.
- Eclairir le code, regrouper les variables qui pourraient l'être pour éviter les redondances dans un but, encore une fois, d'optimisation.