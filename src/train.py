import torch
import torch.nn as nn
import torch.optim as optim
import random
from game import GameState
from model import TsuNet
import numpy as np

def generate_self_play_data(num_games=50):
    """
    Simule des parties aléatoires et collecte les états sous forme de tenseurs associés au résultat de chaque partie
    """
    X_data = [] #Les tenseurs de jeu
    Y_data = [] #Les tenseurs de scores

    print(f"Génération de {num_games} pour l'entrainement du modèle")

    for game_idx in range(num_games):
        game = GameState()
        game_history = [] #Liste des tuple retraçant la partie

        #Jouer une partie complète avec un maximum de 100 tours pour éviter les boucles infinies
        for _ in range(100):
            winner = game.check_win_condition()
            if winner:
                break

            # Vectoriser l'état actuel (forme 10, 4, 4)
            state_tensor = game.vectorize()
            game_history.append((state_tensor, game.current_player))

            #Coup aléatoire
            legal_actions = game.get_legal_actions()
            if not legal_actions:
                break
            action = random.choice(legal_actions)
            start_pos, m1, m2, new_epoch = action
            m1_t, m1_p = m1 if m1 else None, None
            m2_t, m2_p = m2 if m2 else None, None

            success, _ = game.play_full_turn(start_pos, m1_t, m1_p, m2_t, m2_p, new_epoch)
            if not success:
                break
        else:
            winner = "Draw" #Limite de tour atteinte

        #Assigner un score final à la partie
        #1 pour victoire, -1 pour défaite et 0 pour match nul
        for state_tensor, player in game_history:
            if winner == "Draw":
                reward = 0.0
            elif winner == player:
                reward = 1.0
            else:
                reward = -1.0

            X_data.append(state_tensor)
            Y_data.append([reward])

    X_array = np.array(X_data, dtype= np.float32)
    Y_array = np.array(Y_data, dtype= np.float32)
    print(f"Collecte terminée : {len(X_data)} positions extraites")
    return torch.tensor(X_array), torch.tensor(Y_array)

def train_model():
    #Générer un dataset de train
    X, Y = generate_self_play_data(num_games=100)

    if len(X) == 0:
        print("Erreur : Aucune donnée générée")
        return

    #Initialiser le modèle, la fonction de coût MSE et l'optimiseur Adam
    model = TsuNet()
    model.train() #Mode entraînement

    criterion = nn.MSELoss() #Erreur quadratique moyenne pour prédire un score entre -1 et 1
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    epoques = 10
    batch_size = 32

    print("\nDébut de l'entraînement du réseau de neurones ...")
    for epoque in range(epoques):
        total_loss = 0
        #Mélanger et parcourir par batchs
        permutation = torch.randperm(X.size(0))

        for i in range(0, X.size(0), batch_size):
            indices = permutation[i:i + batch_size]
            batch_x, batch_y = X[indices], Y[indices]

            #Remise à 0 des gradients
            optimizer.zero_grad()

            #Prédiction du modèle
            predictions = model(batch_x)

            #Calcul de l'erreur
            loss = criterion(predictions, batch_y)

            #Rétropropagtion
            loss.backward()
            optimizer.step()

            total_loss += loss.item() * batch_x.size(0)

        epoch_loss = total_loss / X.size(0)
        print(f"Epoque {epoque + 1}/{epoques} - Loss (erreur): {epoch_loss:.4f}")

    #Sauvegarder les poids entrainés du modèle
    torch.save(model.state_dict(), "tsunet_weights.pth")
    print("\nEntraînement terminé ! Modèle sauvegardé dans 'tsunet_weights.pth'.")

if __name__ == "__main__":
    train_model()



