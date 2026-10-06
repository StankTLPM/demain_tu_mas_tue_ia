import torch
import torch.nn as nn
import torch.nn.functional as F

#Création du réseau de neurones
class TsuNet(nn.Module):
    def __init__(self):
        super(TsuNet, self).__init__()

        #On utilise des blocs convolutifs pour les dépendances temporelles
        self.conv1 = nn.Conv2d(10, 64, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(64)

        self.conv2 = nn.Conv2d(64, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)

        #Evaluation de la position actuelle
        #En entrée 64 canaux * 4 hauteurs * 4 largeurs = 1024
        self.fc1 = nn.Linear(64 * 4 * 4, 128)
        self.fc2 = nn.Linear(128, 1)

    def forward(self, x):
        """
        Tenseur de forme (batch_size, 10, 4, 4)
        """
        #Passage dans les convoluetions avec activation ReLU et BatchNorm
        x = F.relu(self.bn1(self.conv1(x)))
        x = F.relu(self.bn2(self.conv2(x)))

        #Applatissement avant les couches denses
        x = x.view(x.size(0), -1)

        #Calcul du score de la position
        x = F.relu(self.fc1(x))
        #Tangente hyperbolique assure une sortie entre -1 (défaite assurée) et 1 (victoire assurée)
        value = torch.tanh(self.fc2(x))

        return value

if __name__ == "__main__":
    from game import GameState

    #Initialisation du jeu
    game = GameState()
    tensor_state = game.vectorize()

    #Transformer en tenseur lisible par notre modèle
    input_tensor = torch.tensor(tensor_state, dtype=torch.float32).unsqueeze(0)

    #Initialiser le réseau et tester une inférence
    model = TsuNet()
    model.eval() #Mode évaluation

    with torch.no_grad():
        prediction = model(input_tensor)

    print("Forme de l'entrée du modèle", input_tensor.shape)
    print("Sortie du réseau (Evaluation de la position) :", prediction.item())
