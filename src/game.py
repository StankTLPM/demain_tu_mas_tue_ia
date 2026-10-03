class GameState:
    def __init__(self):
        #Représentation du plateau, 3 plateaux 4x4 (passé, présent, futur)
        #Les grilles sont initialisées à vide
        #Par convention, 0 est le passé, 1 est le présent et 2 est le futur
        self.boards = [
            [['B'] + [None for _ in range(3)], [None for _ in range(4)], [None for _ in range(4)], [None for _ in range(3)] + ['N']], #passé
            [['B'] + [None for _ in range(3)], [None for _ in range(4)], [None for _ in range(4)], [None for _ in range(3)] + ['N']], #présent
            [['B'] + [None for _ in range(3)], [None for _ in range(4)], [None for _ in range(4)], [None for _ in range(3)] + ['N']]  #futur
        ]

        #Joueur actuel ('B' pour joueur 1, 'N' pour joueur 2)
        self.current_player = 'B'

        #Ajout de la notion d'époque, le joueur ne peut jouer que dans son époque et doit changer obligatoirement à la fin de son tour
        #Joueur 1 commence dans le passé
        #Joueur 2 commence dans le futur
        self.player_epochs = {'B': 0, 'N': 2}

    def print_boards(self):
        #Afficher le plateau de manière lisible dans la console et montre la position époque des joueurs
        board_names = ["Passé", "Présent", "Futur"]

        print(f"=== Tour du joueur : {self.current_player} ===")
        print(f"Positions des époques -> B: {board_names[self.player_epochs['B']]}, N: {board_names[self.player_epochs['N']]} ")
        print(f"Le joueur {self.current_player} doit joueur sur l'époque {board_names[self.player_epochs[self.current_player]]}\n")

        for idx, board in enumerate(self.boards):
            marker = ""
            if self.player_epochs['B'] == idx: marker += " [Jeton Blanc] "
            if self.player_epochs['N'] == idx: marker += " [Jeton Noir] "

            print(f"--- {board_names[idx]} {marker} ---")
            for row in board:
                #Remplace les None par des . pour un affichage plus propre
                print(" ".join([cell if cell is not None else '.' for cell in row]))
            print()

    def change_player_epoch(self, new_epoch):
        """
        Déplace le jeton époque d'un joueur à la fin de son tour
        Règle : le jeton ne peut rester sur l'époque actuelle
        """
        current_epoch = self.player_epochs[self.current_player]

        if not (0 <= new_epoch <= 2):
            return False, "L'époque doit être passé, présent ou futur"

        if new_epoch == current_epoch:
            return False, "L'époque doit obligatoirement changer"

        #Mise à jour
        self.player_epochs[self.current_player] = new_epoch
        return True, "Epoque changée avec succès"

    def execute_single_move(self, epoch, r, c, move_type, target_param):
        """
        Exécuter un mouvement unitaire parmi ceux possibles dans le jeu pour un pion situé à une époque epoch, sur la ligne r et la colonne c
        - move_type 'space', mouvement latéral sur la même époque, target_param = (targetr, targetc)
        - move_type 'time', mouvement dans une autre époque, target_param = int (nouvelle époque)
        """
        piece = self.boards[epoch][r][c]
        if piece is None:
            return None, False, "Aucun pion à cette position"

        #Mouvement spatial
        if move_type == 'space':
            target_r, target_c = target_param

            #Vérification mouvement adjacent non diagonal
            if abs(r - target_r) + abs(c - target_c) != 1:
                return None, False, "Distance trop grande ou non mouvement"
            if not (0 <= target_r < 4 and 0 <= target_c < 4):
                return None, False, "Mouvement en dehors du plateau"

            target_piece = self.boards[epoch][target_r][target_c]

            #Déplacement si ca case visée est vide
            if target_piece is None:
                self.boards[epoch][target_r][target_c] = piece
                self.boards[epoch][r][c] = None
                return (epoch, target_r, target_c), True, "Déplacement spatial réussi"

            #La case visée est occupé par un pion de la même couleur
            elif target_piece == piece:
                self.boards[epoch][target_r][target_c] = None
                self.boards[epoch][r][c] = None
                return None, True, "Collision entre deux pièces alliées"

            #La case visée est occupée par un pion ennemi
            else:
                #direction du déplacement 
                dr = target_r - r
                dc = target_c - c

                next_r = target_r + dr
                next_c = target_c + dc

                #Le pion attaquant prend la place du pion déplacé
                self.boards[epoch][target_r][target_c] = piece
                self.boards[epoch][r][c] = None

                #Si on sort du plateau, le pion attaqué est détruit
                if not (0 <= next_r < 4 and 0 <= next_c < 4):

                    return (epoch, target_r, target_c), True, "Pion ejecté par le déplacement"

                return self.execute_single_move(epoch, target_r, target_c, 'space', (next_r, next_c))

        #Mouvement temporel
        if move_type == 'time':
            target_epoch = target_param

            #Vérification que le voyage se fait vers une époque adjacente
            if abs(target_epoch - epoch) != 1:
                return None, False, "Voyage vers une époque trop lointaine ou la même"

            #La case d'arrivée doit être vide
            if self.boards[target_epoch][r][c] is not None:
                return None, False, "La case d'arrivée n'est pas libre"

            #Règle de dépôt
            if target_epoch < epoch:
                #Vers une époque antérieure, on doit placer un nouveau jeton sur la case libérée (on n'enlève pas le jeton actuel en mettant à jour le plateau)
                self.boards[target_epoch][r][c] = piece
                return (target_epoch, r, c), True, f"Voyage temporel vers {target_epoch} réussi"

            if target_epoch > epoch:
                #Vers une époque postérieure, on ne place pas de jeton, le jeton est donc retiré lorsque l'on met à jour le board
                self.boards[target_epoch][r][c] = piece
                self.boards[epoch][r][c] = None
                return (target_epoch, r, c), True, f"Voyage temporel vers {target_epoch} réussi"

        return None, False, "Mouvement inconnu"

    def has_pieces_on_epoch(self, player, epoch):
        """
        Vérifie si le joueur a au moins un pion sur l'époque sur laquelle il joue
        """
        for r in range(4):
            for c in range(4):
                if self.boards[epoch][r][c] == player:
                    return True
        return False

    def play_full_turn(self, start_pos, move1type, move1_param, move2type, move2_param, new_epoch):
        """
        Joue un tour complet pour le joueur actuel
        - start_pos : couple (r,c) pour le pion qu'il choisi de jouer
        - move1type / move1_param : le type (space/time) et les paramètres associés pour faire le premier mouvement
        - move2type / move2_param : le type (space/time) et les paramètres associés pour faire le deuxième mouvement
        - new_epoch : l'époque sur laquelle le joueur déplace son jeton à la fin du tour
        """
        player = self.current_player
        current_epoch = self.player_epochs[player]

        #Vérifier si le joueur a au moins une pièce dans cette époque
        has_pieces = self.has_pieces_on_epoch(player, current_epoch)

        if has_pieces:
            if start_pos is None:
                return False, "Vous devez choisir une case occupée par un de vos pions"

            r, c = start_pos
            #Vérifier que la case choisi est bien occupée par un pion du joueur 
            if self.boards[current_epoch][r][c] != player:
                return False, "Ce pion ne vous appartient pas ou il n'y a pas de pion"

            #Premier Mouvement
            new_pos, success1, msg1 = self.execute_single_move(current_epoch, r, c, move1type, move1_param)
            if not success1:
                return False, f"Echec du premier mouvement : {msg1}"

            #Si le pion a disparu pendant le premier mouvement, on annule le deuxième
            if new_pos is None:
                print('Le pion a disparu pendant le premier mouvement, le second mouvement est annulé')
            else:
                #Deuxième Mouvement
                next_epoch, next_r, next_c = new_pos
                _, success2, msg2 = self.execute_single_move(new_epoch, next_r, next_c, move2type, move2_param)
                if not success2:
                    return False, f"Echec du deuxième mouvement : {msg2}"

        else:
            print(f"Aucun pion n'est disponible pour le joueur {player} à l'époque {current_epoch}")

        #Changement d'époque obligatoire à la fin
        success_epoch, msg_epoch = self.change_player_epoch(new_epoch)
        if not success_epoch:
            return False, f"Echec du changement d'époque : {msg_epoch}"

        #Changement de joueur
        self.current_player = 'N' if player == 'B' else 'B'
        return True, 'Tour complété avec succès'

            


if __name__ == "__main__":
    game = GameState()
    print("Etat du système initial")
    game.print_boards()