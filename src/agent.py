import random
from game import GameState # Import du jeu

class RandomAgent:
    def __init__(self, color):
        self.color = color #'B' ou 'N' selon le joueur

    def choose_action(self, game_state):
        """
        Choisi un coup aléatoire parmi les coups légaux
        """
        legal_actions = game_state.get_legal_actions()
        if not legal_actions:
            return None
        return random.choice(legal_actions)

def play_match(agent_b, agent_n, max_turn=200, verbose=False):
    """
    Fait s'affronter deux agents sur une partie complète
    Retourne le gagnant ('B', 'N' ou 'Draw')
    """
    game = GameState()

    for turn_num in range(max_turn):
        #Vérifier si la partie est finie
        winner = game.check_win_condition()
        if winner:
            if verbose:
                print(f"Partie terminée au tour {turn_num}. Victoire de {winner} !")

        #Déterminer quel agent doit jouer
        current_agent = agent_b if game.current_player == 'b' else agent_n

        #Choix du coup
        action = current_agent.choose_action(game)
        if action is None:
            if verbose:
                print(f"Plus de coup légal pour {game.current_player}. Fin de partie")
            return 'N' if game.current_player == 'B' else 'B'

        #Décomposer le coup choisi
        start_pos, m1, m2, new_epoch = action

        m1_type, m1_param = m1 if m1 else (None, None)
        m2_type, m2_param = m2 if m2 else (None, None)

        #Faire un tour complet
        success, message = game.play_full_turn(start_pos, m1_type, m1_param, m2_type, m2_param, new_epoch)

        if not success:
            print(f"ERREUR: coup illégal joué par {game.current_player} -> {message}")
            return "Error"

        if verbose:
            print(f"--- Tour {turn_num} ({game.current_player}) ---")
            print(f"Coup joué : {action}")

    if verbose:
        print("Limite de tour atteinte : Match Nul")
    return 'Draw'

if __name__ == "__main__" :
    agent1 = RandomAgent('B')
    agent2 = RandomAgent('N')

    results = {"B":0, "N":0, "Draw":0, "Error":0}

    print("Lancement d'un tournoi de 10 parties (Random vs Random)...")
    for i in range(10):
        winner = play_match(agent1, agent2, max_turn=2000, verbose=False)
        results[winner] += 1
        print(f"Partie {i+1} : Gagnant -> {winner}")

    print("\n Bilan des 10 parties :", results)


        


