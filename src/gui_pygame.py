import pygame 
import sys
from game import GameState
import os
import torch
import numpy as np

def save_game_history(history, winner):
    """
    history : liste de tuples retraçant les coups d'une partie
    winner : 'B', 'N' ou 'Draw'
    """
    if not history:
        return

    X_data = []
    Y_data = []

    for state_tensor, player in history:
        if winner == 'Draw':
            reward = 0.0
        elif winner == player:
            reward = 1.0
        else:
            reward = -1.0

        X_data.append(state_tensor)
        Y_data.append([reward])

    #Créer un dossier 'data' s'il n'existe pas
    os.makedir("data", exist_ok=True)
    filename = f"data/game_vs_human_{winner}_{os.urandom(4).hex()}.pt"

    torch.save({'X': torch.tensor(np.array(X_data, dtype=np.float32)),
                'y': torch.tensor(np.array(Y_data, dtypa=np.float32))
                }, filename)
    print(f"[SUCCES] Partie enregistrée dans {filename}")
    
#Initialisation de pygame
pygame.init()

#Paramètre de la fenêtre et des couleurs
WIDTH, HEIGHT = 1000, 500
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Demain tu m'as tué - Visualisation")

#Couleur (RGB)
BG_COLOR = (240, 240, 245)
GRID_BG = (255, 255, 255)
LINE_COLOR = (200, 200, 200)
TEXT_COLOR = (50, 50, 50)
COLOR_B = (245, 245, 245) #Blanc avec bordure
COLOR_N = (40, 40, 40) #Noir
BORDER_B = (180, 180, 180) 
BORDER_N = (0, 0, 0)
HIGHTLIGHT_EPOCH = (255, 220, 100) # Jaune discret pour l'époque active
HIGHTLIGHT_COLOR = (100, 200, 100) #Vert pour la sélection

FONT = pygame.font.SysFont(None, 24)
FONT_BOLD = pygame.font.SysFont(None, 28, bold=True)

grid_size = 280
#Position des trois grilles (passé, présent, futur)
board_positions = [(50, 100), (350, 100), (650, 100)]
board_names = ["PASSE (0)", "PRESENT (1)", "FUTUR (2)"]

def get_board_and_cell_from_mouse(pos):
    """
    Converti un clic de souris (x, y) en (epoch_idx, row, col) si valide
    """
    mx, my = pos
    cell_size = grid_size // 4

    for idx, (bx, by) in enumerate(board_positions):
        if bx <= mx < bx + grid_size and by <= my < by + grid_size:
            c = (mx - bx) // cell_size
            r = (my - by) // cell_size
            if 0 <= r < 4 and 0 <= c < 4:
                return idx, r, c
    return None

def draw_board_grid(surface, x, y, size, board_data, board_name, is_epoch_b, is_epoch_n, selected_pos):
    """
    Dessine une grille 4x4 repésentant une époque
    """
    cell_size = size // 4

    #Fond de la grille
    rect = pygame.Rect(x, y, size, size)

    #Mettre en surbrillance si un joueur a son jeton époque ici
    if is_epoch_b or is_epoch_n:
        pygame.draw.rect(surface, (255, 245, 200), rect) #Fond légèrement teinté

    pygame.draw.rect(surface, GRID_BG, rect)
    pygame.draw.rect(surface, LINE_COLOR, rect, 2)

    #Lignes intérieures
    for i in range(1, 4):
        #Lignes verticales
        pygame.draw.line(surface, LINE_COLOR, (x + i * cell_size, y), (x + i * cell_size, y + size), 1)
        #Lignes horizontales
        pygame.draw.line(surface, LINE_COLOR, (x, y + i * cell_size), (x + size, y + i * cell_size), 1)

    #Titre du plateau et indicateurs d'époques
    title_surface = FONT_BOLD.render(board_name, True, TEXT_COLOR)
    surface.blit(title_surface, (x, y-30))

    markers = []
    if is_epoch_b: markers.append('B')
    if is_epoch_n: markers.append('N')
    if markers:
        marker_text = FONT.render(f"Jeton: {', '.join(markers)}", True, (200, 100, 0))
        surface.blit(marker_text, (x + size - marker_text.get_width(), y-30))

    #Dessin de pions
    for r in range(4):
        for c in range(4):
            piece  = board_data[r][c]
            if piece is not None:
                cx = x + c * cell_size + cell_size // 2
                cy = y + r * cell_size + cell_size // 2
                radius = cell_size // 3

                #surlignage de la selection actuelle
                if selected_pos and selected_pos == (idx_from_name(board_name), r, c):
                    pygame.draw.circle(surface, HIGHTLIGHT_COLOR, (cx, cy), radius + 4, 3)

                if piece == 'B':
                    pygame.draw.circle(surface, COLOR_B, (cx, cy), radius)
                    pygame.draw.circle(surface, BORDER_B, (cx, cy), radius, 2)
                    #Lettrage de 'B'
                    txt = FONT.render("B", True, (0, 0, 0))
                    surface.blit(txt, (cx - txt.get_width()//2, cy - txt.get_width()//2))
                else:
                    pygame.draw.circle(surface, COLOR_N, (cx, cy), radius)
                    pygame.draw.circle(surface, BORDER_N, (cx, cy), radius, 2)
                    #Lettrage de 'N'
                    txt = FONT.render("N", True, (0, 0, 0))
                    surface.blit(txt, (cx - txt.get_width()//2, cy - txt.get_width()//2))

def idx_from_name(name):
    if "PASSE" in name: return 0
    if "PRESENT" in name: return 1
    return 2



def main_gui():
    game = GameState()
    clock = pygame.time.Clock()

    #Etat du tour : 'SELECT_PIECE', 'SELECT_MOVE_1', 'SELECT_MOVE_2', 'SELECT_NEW_EPOCH'
    state = 'SELECT_PIECE'

    selected_start = None
    m1 = None
    m2 = None
    sim_game = None
    current_pos_sim = None

    message = 'Cliquez sur l un des pions de votre époque actuelle'

    running = True
    while running:
        SCREEN.fill(BG_COLOR)

        player = game.current_player
        current_epoch = game.player_epochs[player]
        has_pieces = game.has_pieces_on_epoch(player, current_epoch)

        #Si le joueur n'a aucun pion disponible
        if not has_pieces and state == 'SELECT_PIECE':
            state = 'SELECT_NEW_EPOCH'
            message = 'Aucun pion disponible sur cette époque, passez au changement d epoque'

        #Gestion des évènements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click_pos = get_board_and_mouse = get_board_and_cell_from_mouse(event.pos)

                if click_pos:
                    epoch_idx, r, c = click_pos

                    #ETAPE 1 : SELECTION DU PION
                    if state == 'SELECT_PIECE':
                        if epoch_idx == current_epoch and game.boards[epoch_idx][r][c] == player:
                            selected_start = (epoch_idx, r, c)
                            state = 'SELECT_MOVE_1'
                            message = "1er mouvement: Cliquez sur une case adjacente (space) ou sur la même case d'une autre époque (time)"
                        else:
                            message = "Sélection invalide, choisissez un pion de votre époque"

                    #ETAPE 2 : SELECTION DU PREMIER MOUVEMENT
                    elif state == 'SELECT_MOVE_1':
                        start_epoch, sr, sc = selected_start

                        if epoch_idx == start_epoch:
                            if abs(r - sr) + abs (c - sc) == 1:
                                m1 = ('space', (r, c))
                        elif abs(epoch_idx - start_epoch) == 1:
                            if r == sr and c == sc:
                                m1 = ('time', epoch_idx)

                        if m1:
                            #Tester le premier mouvement sur une simulation
                            sim_game = game.clone()
                            res1 = sim_game.execute_single_move(start_epoch, sr, sc, m1[0], m1[1])

                            if res1[1]:
                                current_pos_sim = res1[0]
                                if current_pos_sim is None:
                                    #Le pion a disparu suite à une collision
                                    message = "Collision ! Le pion a disparu, choisissez une nouvelle époque."
                                    state = 'SELECT_NEW_EPOCH'
                                else:
                                    state = 'SELECT_MOVE_2'
                                    message = "2ème mouvement : déplacez ce pion à nouveau (ou recommencez avec ECHAP)."
                            else:
                                message = f"Mouvement illégal : {res1[2]}"
                                m1 = None
                        else:
                            message = "Mouvement invalide (doit être orthogonal ou temporel adjacent)."

                    #ETAPE 3 : SELECTION DU DEUXIEME MOUVEMENT
                    elif state == 'SELECT_MOVE_2':
                        curr_e, cr, cc = current_pos_sim

                        if epoch_idx == curr_e:
                            if abs(r - cr) + abs(c - cc) == 1:
                                m2 = ('space', (r, c))
                        elif abs(epoch_idx - curr_e) == 1:
                            if r == cr and c == cc:
                                m2 = ('time', epoch_idx)  

                        if m2:
                            res2 = sim_game.execute_single_move(curr_e, cr, cc, m2[0], m2[1])
                            if res2[1]:
                                state = 'SELECT_NEW_EPOCH'
                                message = "Tour valide ! Choisissez votre nouvelle époque (cliquez sur le titre d'une autre époque)."
                            else:
                                message = f"2ème mouvement illégal : {res2[2]}"
                                m2 = None
                        else:
                            message = "2ème mouvement invalide !"

                    #ETAPE 4 : SELECTION NOUVELLE EPOQUE
                    elif state == 'SELECT_NEW_EPOCH':
                        other_epochs = [e for e in range(3) if e != current_epoch]
                        if epoch_idx in other_epochs:
                            #Tout est prêt, on valide le tour dans le vrai jeu
                            s_pos = (selected_start[1], selected_start[2]) if has_pieces else None
                            m1_t, m1_p = m1 if m1 else (None, None)
                            m2_t, m2_p = m2 if m2 else (None, None)

                            success, msg = game.play_full_turn(s_pos, m1_t, m1_p, m2_t, m2_p, epoch_idx)

                            if success:
                                #Réinitialiser pour le tour suivant
                                state = 'SELECT_PIECE'
                                selected_start = None
                                m1, m2 = None, None
                                message = f"Tour réussi ! C'est au tour de {game.current_player}."
                            else:
                                message = f"Erreur de validation : {msg}"
                                state = 'SELECT_PIECE'
                        else:
                            message = "Vous devez choisir une autre époque que l'époque actuelle."

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    #Réinitialiser la sélection en cours
                    state = 'SELECT_PIECE'
                    selected_start = None
                    m1, m2 = None, None
                    message = "Tour réinitialisé. Sélectionnez un pion."
        
        
        #Affichage des informations générales
        info_surf = FONT_BOLD.render(f"Tour : Joueur {player} | Réserves -> B : {game.player_reserves['B']} | N : {game.player_reserves['N']}", True, TEXT_COLOR)
        SCREEN.blit(info_surf, (50, 20))

        msg_surf = FONT.render(message, True, (180, 50, 50) if "illégal" in message or "invalide" in message else (0, 100, 0))
        SCREEN.blit(msg_surf, (50, 390))

        hint_surf = FONT.render("(Appuyez sur ECHAP pour réinitialiser votre sélection en cours)", True, (120, 120, 120))
        SCREEN.blit(hint_surf, (50, 420))

        winner = game.check_win_condition()
        if winner:
            win_surf = FONT_BOLD.render(f"VICTOIRE DU JOUEUR {winner} !", True, (200, 0, 0))
            SCREEN.blit(win_surf, (WIDTH // 2 - win_surf.get_width()//2, HEIGHT - 40))
        

        #Affichage des trois plateaux
        for idx in range(3):
            bx, by = board_positions[idx]
            is_b_where = (game.player_epochs['B'] == idx)
            is_n_where = (game.player_epochs['N'] == idx)

            sel = selected_start if (state in ['SELECT_MOVE_1', 'SELECT_MOVE_2'] and selected_start and selected_start[0] == idx) else None
            
            draw_board_grid(SCREEN, bx, by, grid_size, game.boards[idx], board_names[idx], is_b_where, is_n_where, sel)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_gui()







