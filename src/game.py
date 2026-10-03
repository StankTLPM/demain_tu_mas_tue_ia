class GameState:
    def __init__(self):
        #Représentation du plateau, 3 plateaux 4x4 (passé, présent, futur)
        #Les grilles sont initialisées à vide
        #Par convention, 0 est le passé, 1 est le présent et 2 est le futur
        self.boards = [
            [[None for _ in range(4)] for _ in range(4)], #passé
            [[None for _ in range(4)] for _ in range(4)], #présent
            [[None for _ in range(4)] for _ in range(4)]  #futur
        ]

        #Joueur actuel ('B' pour joueur 1, 'N' pour joueur 2)
        self.current_player = 'B'

    def print_boards(self):
        #Afficher le plateau de manière lisible dans la console
        board_names = ["Passé", "Présent", "Futur"]
        for idx, board in enumerate(self.boards):
            print(f"--- {board_names[idx]} ---")
            for row in board:
                #Remplace les None par des . pour un affichage plus propre
                print(" ".join([cell if cell is not None else '.' for cell in row]))
            print()

if __name__ == "__main__":
    game = GameState()
    print("Etat du système initial")
    game.print_boards()