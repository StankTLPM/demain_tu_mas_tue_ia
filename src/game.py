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

if __name__ == "__main__":
    game = GameState()
    print("Etat du système initial")
    game.print_boards()