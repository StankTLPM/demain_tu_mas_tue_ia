import copy
import numpy as np

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

        #Les jetons en réserve permettent aux joueurs de se déplacer vers une époque antérieure
        self.player_reserves = {'B': 4, 'N': 4}

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
                #Il faut donc vérifier si le joueur possède au moins un jeton en réserve
                if self.player_reserves[self.current_player] <= 0:
                    return None, False, "Réserve vide : impossible de voyager vers une époque antérieure"

                #Enlever un jeton de la réserve du joueur
                self.player_reserves[self.current_player] -= 1

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
                _, success2, msg2 = self.execute_single_move(next_epoch, next_r, next_c, move2type, move2_param)
                if not success2:
                    return False, f"Echec du deuxième mouvement : {msg2}"

        else:
            print(f"Aucun pion n'est disponible pour le joueur {player} à l'époque {current_epoch}")

        #Changement d'époque obligatoire à la fin
        success_epoch, msg_epoch = self.change_player_epoch(new_epoch)
        if not success_epoch:
            return False, f"Echec du changement d'époque : {msg_epoch}"

        #Vérification qu'aucun joueur n'a gagné
        winner = self.check_win_condition()
        if winner:
            return True, f"Victoire de {winner}, l'adversaire a été effacé de l'histoire !"

        #Changement de joueur
        self.current_player = 'N' if player == 'B' else 'B'
        return True, 'Tour complété avec succès'

    def count_epoch_with_pieces(self, player):
        """
        Compte le nombre d'époques dans lesquelles le joueur est disponible
        """
        count = 0
        for epoch_idx in range(3):
            if self.has_pieces_on_epoch(player, epoch_idx):
                count += 1
        return count

    def check_win_condition(self):
        """
        Vérifie si la partie est terminée et annonce le gagnant.
        Un joueur gagne si son adversaire, au début ou à la fin de son tour n'est disponible que sur au plus une époque
        Retourne 'B', 'N' ou None si la partie continue
        """
        for player in ['B', 'N']:
            opponent = 'N' if player == 'B' else 'B'
            if self.count_epoch_with_pieces(opponent) <= 1:
                return player #Le joueur actuel gagne
        return None

    def clone(self):
        """
        Créer une copie de l'état du jeu actuel
        """
        new_game = GameState()
        new_game.boards = copy.deepcopy(self.boards)
        new_game.current_player = self.current_player
        new_game.player_epochs = self.player_epochs.copy()
        new_game.player_reserves = self.player_reserves.copy()
        return new_game

    def get_legal_actions(self):
        """
        Retourne la liste de tous les coups légaux possibles pour le joueur actuel.
        Chaque coup est un tuple : (start_pos, mov1, mov2, new_epoch)
        """
        player = self.current_player
        current_epoch = self.player_epochs[player]
        legal_actions = []

        #Les époques possibles pour le choix à la fin du tour
        other_epochs = [e for e in range(3) if e != current_epoch]

        # Vérifier si le joueur a des pions sur son époque actuelle
        has_pieces = self.has_pieces_on_epoch(player, current_epoch)

        if not has_pieces:
            #Si aucun pion sur l'époque, la seule chose à faire c'est changé d'époque
            for new_epoch in other_epochs:
                legal_actions.append((None, None, None, new_epoch))
            return legal_actions

        #Faire l'inventaire des pions disponibles sur l'époque actuelle du joueur
        piece_positions = []
        for r in range(4):
            for c in range(4):
                if self.boards[current_epoch][r][c] == player:
                    piece_positions.append((r, c))

        #Faire l'inventaire des movements spatiaux possibles
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        #Faire l'inventaire des mouvements temporels disponibles
        time_epochs = [current_epoch - 1, current_epoch + 1]

        #Pour chaque pion, on regarde les mouvements disponibles
        for pos in piece_positions:
            r, c = pos

            #Regarder le premier mouvements
            possible_move_1 = []

            #Mouvements spatiaux
            for dr, dc in directions:
                tr, tc = r + dr, c + dc
                if 0 <= tr < 4 and 0 <= tc < 4:
                    possible_move_1.append(('space', (tr, tc)))

            #Mouvements temporels
            for te in time_epochs:
                if 0 <= te < 3:
                    possible_move_1.append(('time', te))

            #Tester chaque premier mouvement
            for m1_type, m1_param in possible_move_1:
                #On clone l'état du système après le premier mouvement
                sim_game = self.clone()
                res1 = sim_game.execute_single_move(current_epoch, r, c, m1_type, m1_param)

                #Si le premier mouvement est invalide, on passe
                if not res1[1]:
                    continue

                new_pos = res1[0] # (new_epoch, new_r, new_c) ou None si le pion a disparu

                #Si le pion a disparu lors du premier mouvement (collision)
                if new_pos is None:
                    #Le pion a disparu donc pas de deuxième mouvement disponible
                    #Le tour se termine par le changement d'époque
                    for new_epoch in other_epochs:
                        legal_actions.append((pos, (m1_type, m1_param), None, new_epoch))
                    continue

                #Sinon, le pion a bougé et il faut regarder les mouvements à partir de la nouvelle position
                next_epoch, next_r, next_c = new_pos
                possible_move_2 = []

                #Mouvements spatiaux depuis la nouvelle position
                for dr, dc in directions:
                    tr, tc = next_r + dr, next_c + dc
                    if 0 <= tr < 4 and 0 <= tc < 4:
                        possible_move_2.append(('space', (tr, tc)))

                #Mouvements temporels depuis la nouvelle position
                for te in time_epochs:
                    if 0 <= te < 3:
                        possible_move_2.append(('time', te))

                #Tester les deuxièmes mouvements
                for m2_type, m2_param in possible_move_2:
                    sim_game2 = sim_game.clone()
                    res2 = sim_game2.execute_single_move(next_epoch, next_r, next_c, m2_type, m2_param)

                    if not res2[1]:
                        continue # Deuxième mouvement invalide

                    #Enfin, pour chaque configuration possible de deux mouvements, le joueur choisi la prochaine époque
                    for new_epoch in other_epochs:
                        legal_actions.append((pos, (m1_type, m1_param), (m2_type, m2_param), new_epoch))

        return legal_actions

    def vectorize(self):
        """
        Afin de faire lire le modèle à un réseau de neurones,
        On code toutes les informations de l'état du jeu à un instant t sous forme de tensuer
        Return NumPy tensor (10, 4, 4)
        """
        #Initialisation du tenseur 10 canaux de taille 4x4 à 0
        tensor = np.zeros((10, 4, 4), dtype=np.float32)

        current_p = self.current_player
        opponent_p = 'N' if current_p == 'B' else 'B'

        #Remplissage de 6 premiers canaux représentant les plateaux de jeux des jeux joueurs
        for epoch_idx in range(3):
            for r in range(4):
                for c in range(4):
                    piece = self.boards[epoch_idx][r][c]
                    if piece == current_p:
                        tensor[epoch_idx][r][c] = 1.0
                    elif piece == opponent_p:
                        tensor[3 + epoch_idx][r][c] = 1.0

        #Remplissage du canal 6 pour le jeton époque du joueur actuel
        current_epoch_val = self.player_epochs[current_p] / 2.0
        tensor[6, :, :] = current_epoch_val

        #Remplissage du canal 7 pour le jeton époque de l'adversaire
        opponent_epoch_val = self.player_epochs[opponent_p] / 2.0
        tensor[7, :, :] = opponent_epoch_val

        #Replissage du canal 8 pour la réserve du joeur actuel
        current_reserve = self.player_reserves[current_p] / 4
        tensor[8, :, :] = current_reserve

        #Remplissage du canal 9 pour la réserve de l'adversaire
        opponent_reserve = self.player_reserves[opponent_p] / 4
        tensor[9, :, :] = opponent_reserve

        return tensor


if __name__ == "__main__":
    game = GameState()
    state_tensor = game.vectorize()
    print("Forme du tenseur d'état", state_tensor.shape)
    print("Somme des valeurs dans le tenseur", np.sum(state_tensor))
    print("Forme du tenseur", state_tensor)
    print("Reserve de l'aversaire", state_tensor[8, 0, 0])
