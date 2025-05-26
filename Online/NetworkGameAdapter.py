# Online/NetworkGameAdapter.py
import pygame
from UI_tools.BaseUi import BaseUI
from Board.Board_draw_tools import Board_draw_tools
from Game_ui.move_rules import Moves_rules

class NetworkGameAdapter(BaseUI):
    """Adaptateur pour jouer aux jeux en réseau"""
    
    def __init__(self, game_session, title="Jeu en réseau"):
        super().__init__(title)
        
        # Session de jeu réseau
        self.session = game_session
        self.board = game_session.board
        self.game_type = game_session.game_type
        
        # Outils de jeu
        self.board_ui = Board_draw_tools()
        self.moves_rules = Moves_rules(self.board)
        
        # État du jeu
        self.selected_pawn = None
        self.current_player = 1
        self.local_player = 1 if game_session.is_host else 2
        self.game_finished = False
        
        # Interface
        self.cell_size = 60
        self.grid_dim = len(self.board)
        self.grid_size = self.cell_size * self.grid_dim
        self.top_offset = 80
        self.left_offset = (self.get_width() - self.grid_size) // 2
        
        # Polices
        self.title_font = pygame.font.SysFont(None, 48)
        self.info_font = pygame.font.SysFont(None, 36)
        self.button_font = pygame.font.SysFont(None, 36)
        
        # Titre selon le jeu
        game_names = {1: "Katarenga", 2: "Congress", 3: "Isolation"}
        self.title_surface = self.title_font.render(
            f"{game_names.get(self.game_type, 'Jeu')} - Réseau", 
            True, (255, 255, 255)
        )
        self.title_rect = self.title_surface.get_rect(center=(self.get_width() // 2, 40))
        
        # Boutons
        self.back_button = pygame.Rect(20, 20, 120, 40)
        
        # Configuration des callbacks de session
        self.session.set_game_callbacks(
            board_update=self.on_board_update,
            player_change=self.on_player_change,
            game_end=self.on_game_end
        )
        
        # Messages d'état
        self.status_message = ""
        self.status_color = (255, 255, 255)
        
        print(f"[GAME] Jeu réseau initialisé - Type: {self.game_type}, Joueur local: {self.local_player}")
    
    def run(self):
        
        self.session.start_game()
        
        while self.running and not self.game_finished:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
        
        print("[GAME] Jeu terminé")
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.back_button.collidepoint(event.pos):
                    self.running = False
                else:
                    self.handle_board_click(event.pos)
    
    def handle_board_click(self, pos):
        x, y = pos
        
        # Vérifie si le clic est sur le plateau
        if not (self.left_offset <= x < self.left_offset + self.grid_size and
                self.top_offset <= y < self.top_offset + self.grid_size):
            return
        
        # Calcule la position sur le plateau
        col = (x - self.left_offset) // self.cell_size
        row = (y - self.top_offset) // self.cell_size
        
        if not (0 <= row < self.grid_dim and 0 <= col < self.grid_dim):
            return
        
        # Vérifie si c'est le tour du joueur local
        if self.current_player != self.local_player:
            self.set_status("Ce n'est pas votre tour", (255, 255, 100))
            return
        
        self.process_click(row, col)
    
    def process_click(self, row, col):
        cell_value = self.board[row][col]
        player_on_cell = cell_value % 10
        
        if self.selected_pawn is None:
            # Sélection d'un pion
            if player_on_cell == self.local_player:
                self.selected_pawn = (row, col)
                self.set_status(f"Pion sélectionné en ({row}, {col})", (100, 255, 100))
            else:
                self.set_status("Sélectionnez un de vos pions", (255, 255, 100))
        
        else:
            # Déplacement ou nouvelle sélection
            if (row, col) == self.selected_pawn:
                # Désélection
                self.selected_pawn = None
                self.set_status("Pion désélectionné", (200, 200, 200))
            
            elif player_on_cell == self.local_player:
                self.selected_pawn = (row, col)
                self.set_status(f"Nouveau pion sélectionné en ({row}, {col})", (100, 255, 100))
            
            else:
                
                from_row, from_col = self.selected_pawn
                
                if self.is_valid_move(from_row, from_col, row, col):
                    # Movement valid send to session
                    if self.session.make_move((from_row, from_col), (row, col)):
                        self.selected_pawn = None
                        self.set_status("Mouvement effectué", (100, 255, 100))
                    else:
                        self.set_status("Erreur lors du mouvement", (255, 100, 100))
                else:
                    self.set_status("Mouvement invalide", (255, 100, 100))
    
    def is_valid_move(self, from_row, from_col, to_row, to_col):
        dest_player = self.board[to_row][to_col] % 10
        if dest_player == self.local_player:
            return False
        
        # Utilise les règles de mouvement du jeu
        case_color = self.board[from_row][from_col]
        return self.moves_rules.verify_move(case_color, from_row, from_col, to_row, to_col)
    
    def on_board_update(self, new_board):
        self.board = new_board
        print("[GAME] Plateau mis à jour")
    
    def on_player_change(self, new_player):
        self.current_player = new_player
        if new_player == self.local_player:
            self.set_status("C'est votre tour!", (100, 255, 100))
        else:
            self.set_status("Tour de l'adversaire", (255, 255, 100))
        print(f"[GAME] Tour du joueur {new_player}")
    
    def on_game_end(self, winner):
        self.game_finished = True
        
        if winner == "Déconnexion":
            self.set_status("Adversaire déconnecté", (255, 100, 100))
        elif winner == self.local_player:
            self.set_status("Vous avez gagné!", (100, 255, 100))
        else:
            self.set_status("Vous avez perdu", (255, 100, 100))
        
        print(f"[GAME] Partie terminée - Gagnant: {winner}")
    
    def set_status(self, message, color):
        """Met à jour le message de statut"""
        self.status_message = message
        self.status_color = color
    
    def update(self):
        """Met à jour l'état du jeu"""
        pass
    
    def draw(self):
        """Dessine le jeu"""
        screen = self.get_screen()
        screen.fill((30, 30, 30))
        
        # Titre
        screen.blit(self.title_surface, self.title_rect)
        
        # Plateau de jeu
        self.draw_board(screen)
        
        # Bouton retour
        pygame.draw.rect(screen, (70, 70, 70), self.back_button)
        pygame.draw.rect(screen, (255, 255, 255), self.back_button, 2)
        back_text = self.button_font.render("Retour", True, (255, 255, 255))
        screen.blit(back_text, back_text.get_rect(center=self.back_button.center))
        
        # Informations de jeu
        self.draw_game_info(screen)
    
    def draw_board(self, screen):
        for row in range(self.grid_dim):
            for col in range(self.grid_dim):
                rect = pygame.Rect(
                    col * self.cell_size + self.left_offset,
                    row * self.cell_size + self.top_offset,
                    self.cell_size,
                    self.cell_size
                )
                
                # Couleur de la case
                value = self.board[row][col]
                color_code = value // 10
                player_code = value % 10
                
                color = self.board_ui.get_color_from_board(color_code)
                pygame.draw.rect(screen, color, rect)
                
                # Surbrillance pour le pion sélectionné
                if self.selected_pawn == (row, col):
                    pygame.draw.rect(screen, (255, 255, 0), rect, 4)
                
                # Bordure de case
                pygame.draw.rect(screen, (255, 255, 255), rect, 1)
                
                # Pion s'il y en a un
                if player_code > 0:
                    self.draw_pawn(screen, rect, player_code)
    
    def draw_pawn(self, screen, rect, player):
        center = rect.center
        radius = self.cell_size // 4
        
        # Couleur selon le joueur
        if player == 1:
            color = (0, 0, 255)  # Bleu
        else:
            color = (255, 0, 0)  # Rouge
        
        pygame.draw.circle(screen, color, center, radius)
        pygame.draw.circle(screen, (255, 255, 255), center, radius, 2)
    
    def draw_game_info(self, screen):
        
        info_y = self.top_offset + self.grid_size + 20
        
        # Informations du joueur
        player_info = f"Vous êtes le joueur {self.local_player}"
        player_color = (0, 0, 255) if self.local_player == 1 else (255, 0, 0)
        
        player_surface = self.info_font.render(player_info, True, player_color)
        screen.blit(player_surface, (self.left_offset, info_y))
        
        # Tour actuel
        turn_info = f"Tour du joueur {self.current_player}"
        turn_color = (100, 255, 100) if self.current_player == self.local_player else (255, 255, 100)
        
        turn_surface = self.info_font.render(turn_info, True, turn_color)
        screen.blit(turn_surface, (self.left_offset, info_y + 35))
        
        # Message de statut
        if self.status_message:
            status_surface = pygame.font.SysFont(None, 28).render(self.status_message, True, self.status_color)
            screen.blit(status_surface, (self.left_offset, info_y + 70))
        
        # Instructions
        if not self.game_finished:
            if self.selected_pawn:
                instruction = "Cliquez sur une case pour déplacer le pion"
            else:
                instruction = "Cliquez sur un de vos pions pour le sélectionner"
            
            inst_surface = pygame.font.SysFont(None, 24).render(instruction, True, (200, 200, 200))
            screen.blit(inst_surface, (self.left_offset, info_y + 100))

if __name__ == "__main__":
    # Test basique (nécessite une session de jeu valide)
    print("NetworkGameAdapter - Utilisez ce module via une session de jeu")