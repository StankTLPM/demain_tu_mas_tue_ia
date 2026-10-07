import pygame 
import sys
from game import GameState

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

FONT = pygame.font.SysFont(None, 24)
FONT_BOLD = pygame.font.SysFont(None, 28, bold=True)

def draw_board_grid(surface, x, y, size, board_data, board_name, is_epoch_b, is_epoch_n):
    """
    Dessine une grille 4x4 repésentant une époque
    """
    cell_size = size / 4

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

def main_gui():
    game = GameState()
    clock = pygame.time.Clock()

    grid_size = 280
    #Position des trois grilles (passé, présent, futur)
    board_positions = [(50, 100), (350, 100), (650, 100)]
    board_names = ["PASSE (0)", "PRESENT (1)", "FUTUR (2)"]

    running = True
    while running:
        SCREEN.fill(BG_COLOR)

        #Gestion des évènements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        #Affichage des informations générales
        info_text = f"Tour de joueur : {game.current_player} | Réserves -> B : {game.player_reserves['B']} | N : {game.player_reserves['N']}"
        txt_surf = FONT_BOLD.render(info_text, True, TEXT_COLOR)
        SCREEN.blit(txt_surf, (50, 30))

        #Affichage des trois plateaux
        for idx in range(3):
            bx, by = board_positions[idx]
            is_b_where = (game.player_epochs['B'] == idx)
            is_n_where = (game.player_epochs['N'] == idx)

            draw_board_grid(SCREEN, bx, by, grid_size, game.boards[idx], board_names[idx], is_b_where, is_n_where)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_gui()







