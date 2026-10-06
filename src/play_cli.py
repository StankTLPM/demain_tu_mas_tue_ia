from game import GameState

def get_user_input(prompt):
    """
    Affiche un message et récupère l'entrée du joueur
    """
    try:
        return input(prompt).strip()
    except (KeyboardInterrupt, EOFError):
        print("\nPartie Interrompue.")
        exit(0)

def parse_coordinate(coord_str):
    """
    Converti une chaine de caractère '1, 2' en tuple (1, 2)
    """
    try:
        parts = coord_str.split(',')
        if len(parts) != 2:
            return None
        r, c = int(parts[0].strip()), int(parts[1].strip())
        if 0 <= r < 4 and 0 <= c < 4:
            return (r, c)
    except ValueError:
        pass
    return None

def ask_move_details(prompt_prefix):
    """
    Aide à saisir une mouvement, spatial ou temporel
    """
    while True:
        choice = get_user_input(f"{prompt_prefix} -> Type [1] pour mouvement spatial et [2] pour mouvement temporel :")
        if choice == '1':
            coord_str = get_user_input(" Entrez la case d'arrivée ligne, colonne (ex 1,0) :")
            target = parse_coordinate(coord_str)
            if target:
                return 'space', target
        elif choice == '2':
            try:
                te = int(get_user_input(" Entrez lépoque visée, 0 pour passé, 1 pour présent, 2 pour futur :"))
                if 0 <= te <= 2:
                    return 'time', te
            except ValueError:
                pass
        print('Saisie invalide. Réessayez.')


def interactive_game():
    game = GameState()
    print("========================================")
    print(" BIENVENUE DANS DEMAIN TU M'AS TUE ")
    print("========================================")
    print("Format des coordonnées : ligne, colonne (ex: 0,0 ou 3,2)")
    print("Epoques : 0 = passé, 1 = présent, 2 = futur\n")

    while True:
        #Afficher l'état du jeu
        game.print_boards()

        #Vérifier si le jeu est fini
        winner = game.check_win_condition()
        if winner:
            print(f"\n FIN DE PARTIE : {winner} a gagné !")
            break

        player = game.current_player
        current_epoch = game.player_epochs[player]
        has_pieces = game.has_pieces_on_epoch(player, current_epoch)

        start_pos = None
        m1type, m1_param = None, None
        m2type, m2_param = None, None

        if not has_pieces:
            print(f"Vous n'avez aucun piont sur cette époque {current_epoch}")
            print(f"Vous ne pouvez faire de mouvement, changez simplement d'époque")
        else:
            #Demander le pion que l'on souhaite déplacer
            while True:
                pos_str = get_user_input(f"Joueur {player}, choisissez la position de votre pion sur l'époque {current_epoch} (ex 0,0) :")
                start_pos = parse_coordinate(pos_str)
                if start_pos and game.boards[current_epoch][start_pos[0]][start_pos[1]] == player:
                    break
                else:
                    print("Position invalide ou il n'y a pas de pion vous appartenant à cette position. Réessayez")

            #Premier mouvement
            print("\n--- Premier Mouvement ---")
            m1type, m1_param = ask_move_details("Choisissez le premier mouvement")

            #Simulation rapide pour voir si le pion a survécu au premier mouvement
            #On clone pour tester
            sim = game.clone()
            res1 = sim.execute_single_move(current_epoch, start_pos[0], start_pos[1], m1type, m1_param)

            if not res1[1]:
                print(f"Erreur dans le mouvement : {res1[2]}")
                continue # Recommencer le tour

            new_pos = res1[0] #Position après le premier mouvement

            if new_pos is None:
                print("Votre pion a disparu suite à une collision ! Pas de deuxième mouvement possible.")
            else:
                print("\n--- Deuxième mouvement ---")
                m2type, m2_param = ask_move_details("Choisissez le deuxième mouvement")

                #On teste le deuxième mouvement
                next_epoch, next_r, next_c = new_pos
                res2 = sim.execute_single_move(next_epoch, next_r, next_c, m2type, m2_param)
                if not res2[1]:
                    print(f"[ERREUR] deuxième mouvement invalide : {res2[2]}")
                    get_user_input("Appuyez sur entrée pour recommencer votre tour ...")
                    continue

        #Choix de la nouvelle époque
        while True:
            try:
                other_epochs = [e for e in range(3) if e != current_epoch]
                epoch_str = get_user_input(f"Choisissez votre nouvelle époque {other_epochs} :")
                new_epoch = int(epoch_str)
                if new_epoch in other_epochs:
                    break
            except ValueError:
                pass
            print("Epoque invalide. Vous devez changer obligatoirement vers une autre époque.")

        # Execution du tour complet avec le moteur du jeu
        s1_pos = start_pos if has_pieces else None
        success, message = game.play_full_turn(s1_pos, m1type, m1_param, m2type, m2_param, new_epoch)

        if not success:
            print(f"\n[ERREUR] Coup refusé : {message}")
            get_user_input("Appuyer sur Entrée pour recommencer ce tour...")
        else:
            print(f"\n[SUCCES] {message}")

if __name__ == "__main__":
    interactive_game()

            






