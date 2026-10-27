import torch
import glob
import os
import torch.nn as nn
import torch.optim as optim
from model import TsuNet

def train_on_human_data():
    all_X = []
    all_Y = []

    #Charger les fichiers des parties humaines sauvegardées
    files = glob.glob("data/game_vs_human_*.pt")
    if not files:
        print("Aucune partie enregistrée trouvée dans le dossier 'data/. Jouez sur pygame !")
        return

    for file in files:
        data = torch.load(file)
        all_X.append(data['X'])
        all_Y.append(data['y'])

    X = torch.cat(all_X, dim=0)
    y = torch.cat(all_Y, dim=0)

    print(f"Chargement de {X.size(0)} positions issues de vos parties !")

    model = TsuNet()
    #Charger des poinds précédents si disponibles
    if os.path.exists("tsunet_weights.pts"):
        model.load_state_dict(torch.load("tsunet_weights.pts"))
        print('Anciens poids chargés.')

    model.train()
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    #Entrainement rapide sur les données
    for epoch in range(15):
        optimizer.zero_grad()
        predictions = model(X)
        loss = criterion(predictions, y)
        loss.backward()
        optimizer.step()
        print(f"Epoque {epoch + 1}/15 - Loss : {loss.item():.4f}")

    torch.save(model.state_dict(), "tsunet_weights.pth")
    print("Modèle mis à jour avec les parties sauvegardées !")

if __name__ == "__main__":
    train_on_human_data()


