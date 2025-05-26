import pygame
import copy
import time
from UI_tools.BaseUi import BaseUI
from Board.Board_draw_tools import Board_draw_tools
from Game_ui.move_rules import Moves_rules


class Katarenga(BaseUI):
    def __init__(self,ai, board, title="Katarenga"):
        super().__init__(title)
        
        if board is None:
            raise ValueError("Le plateau ne peut pas être None")
        
        self.board = self.place_pawn_katarenga(board)
        self.board_ui = Board_draw_tools()
        self.moves_rules = Moves_rules(self.board)
        
        self.cell_size = 60
        self.grid_dim = 10
        self.grid_size = self.cell_size * self.grid_dim
        
        self.top_offset = 80
        self.left_offset = (self.get_width() - self.grid_size) // 2
        
        self.title_font = pygame.font.SysFont(None, 48)
        self.title_surface = self.title_font.render("Katarenga", True, (255, 255, 255))
        self.title_rect = self.title_surface.get_rect(center=(self.get_width() // 2, 40))
        
        self.back_button_rect = pygame.Rect(20, 20, 120, 40)
        
        self.current_player = 1  
        self.selected_pawn = None  

        self.__ai = ai

        self.info_font = pygame.font.SysFont(None, 36)
        
        self.directions = {
            1: [ # blue
                (dx, dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1] if not (dx == 0 and dy == 0)
            ],
            2: [  # green
                (2, 1), (1, 2), (-1, 2), (-2, 1),
                (-2, -1), (-1, -2), (1, -2), (2, -1)
            ],
            3: [  # yellow
                (-1, -1), (-1, 1), (1, -1), (1, 1)
            ],
            4: [  # red
                (-1, 0), (1, 0), (0, -1), (0, 1)
            ]
        }

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

            if self.__ai and self.current_player == 2:
                time.sleep(1)
                self.play_ai_turn()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.back_button_rect.collidepoint(event.pos):
                    self.running = False
                else:
                    self.handle_board_click(event.pos)

    def handle_board_click(self, pos):
        x, y = pos
        
        # Check if the click is within the grid area
        if (self.left_offset <= x < self.left_offset + self.grid_size and 
            self.top_offset <= y < self.top_offset + self.grid_size):
            
            col = (x - self.left_offset) // self.cell_size
            row = (y - self.top_offset) // self.cell_size
            
            # Valid coord
        if 0 <= row < self.grid_dim and 0 <= col < self.grid_dim:
            self.process_move(row, col)

    def place_pawn_katarenga(self, board):
        new_board = copy.deepcopy(board)

        # First row, columns 1 to 9 (top of the board)
        for col in range(1, 9):
            color = new_board[1][col] // 10
            new_board[1][col] = color * 10 + 2  # Player 2

        # Last row, columns 1 to 9
        for col in range(1, 9):
            color = new_board[8][col] // 10
            new_board[8][col] = color * 10 + 1  # Player 1

        return new_board
        
    def process_move(self, row, col):
        cell_value = self.board[row][col]
        player_on_cell = cell_value % 10
        
        if self.selected_pawn is None:
            # Pawn selection
            if player_on_cell == self.current_player:
                self.selected_pawn = (row, col)
                print(f"Pion sélectionné à ({row}, {col})")
        else:
            # Second click
            selected_row, selected_col = self.selected_pawn
            
            if (row, col) == self.selected_pawn:
                # Click again = deselect
                self.selected_pawn = None
                print("Pion désélectionné")
            elif player_on_cell == self.current_player:
                # Switch selection with same player
                self.selected_pawn = (row, col)
                print(f"Nouveau pion sélectionné à ({row}, {col})")
            else:
                if self.is_valid_move(selected_row, selected_col, row, col):
                    self.make_move(selected_row, selected_col, row, col)
                    self.selected_pawn = None
                    
                    winner = self.check_victory()
                    if winner == 0:
                        self.switch_player()
                        
                else:
                    print("Mouvement invalide")

    def is_valid_move(self, from_row, from_col, to_row, to_col):
        
        case_color = self.board[from_row][from_col]
        
        # Use the Moves_rules class to validate the move based on the case color
        return self.moves_rules.verify_move(case_color, from_row, from_col, to_row, to_col)

    def make_move(self, from_row, from_col, to_row, to_col):
        # Keep color of the destination
        destination_color = self.board[to_row][to_col] // 10
        
        # Update position
        origin_color = self.board[from_row][from_col] // 10
        self.board[from_row][from_col] = origin_color * 10
        
        # Place pawn at new position
        self.board[to_row][to_col] = destination_color * 10 + self.current_player
        
        print(f"Position départ ({from_row}, {from_col}) vers ({to_row}, {to_col})")

    def switch_player(self):
        self.current_player = 2 if self.current_player == 1 else 1
        print(f"Tour du joueur {self.current_player}")

    def draw(self):
        screen = self.get_screen()
        screen.fill((30, 30, 30))
        screen.blit(self.title_surface, self.title_rect)

        # Draw the board
        for row in range(self.grid_dim):
            for col in range(self.grid_dim):
                rect = pygame.Rect(
                    col * self.cell_size + self.left_offset,
                    row * self.cell_size + self.top_offset,
                    self.cell_size,
                    self.cell_size
                )
                
                # Get cell values
                value = self.board[row][col]
                color_code = value // 10
                player_code = value % 10
                
                # Draw cell color
                color = self.board_ui.get_color_from_board(color_code)
                pygame.draw.rect(screen, color, rect)
                
                # Highlight selected pawn
                if self.selected_pawn == (row, col):
                    pygame.draw.rect(screen, (255, 255, 0), rect, 4)  # Yellow border for selected pawn
                
                # Draw cell border
                pygame.draw.rect(screen, (255, 255, 255), rect, 1)
                
                # Draw pawn if present
                if player_code > 0:
                    self.draw_pawn(screen, rect, player_code)
        
        # Draw back button
        pygame.draw.rect(screen, (70, 70, 70), self.back_button_rect)
        pygame.draw.rect(screen, (255, 255, 255), self.back_button_rect, 2)
        back_text = pygame.font.SysFont(None, 36).render("Retour", True, (255, 255, 255))
        screen.blit(back_text, back_text.get_rect(center=self.back_button_rect.center))
        
        # Draw game info
        self.draw_game_info(screen)


    def draw_pawn(self, screen, rect, player):
        center_x = rect.centerx
        center_y = rect.centery
        radius = self.cell_size // 4
        
        
        if player == 1:
            pawn_color = (0, 0, 255)  # Blue for player 1
        elif player == 2:
            pawn_color = (255, 0, 0)  # Red for player 2
        else:
            return
        
        # Draw pawn 
        pygame.draw.circle(screen, pawn_color, (center_x, center_y), radius)
        pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), radius, 2)
        

    def draw_game_info(self, screen):
        # Display current player
        player_text = f"Tour du joueur {self.current_player}"
        player_color = (0, 0, 255) if self.current_player == 1 else (255, 0, 0)
        
        text_surface = self.info_font.render(player_text, True, player_color)
        text_rect = text_surface.get_rect()
        text_rect.topleft = (self.left_offset, self.top_offset + self.grid_size + 40)
        screen.blit(text_surface, text_rect)
        
        # Display instructions
        if self.selected_pawn:
            instruction = "Cliquez sur une case pour déplacer le pion sélectionné"
        else:
            instruction = "Cliquez sur un de vos pions pour le sélectionner"
        
        instruction_surface = pygame.font.SysFont(None, 24).render(instruction, True, (200, 200, 200))
        instruction_rect = instruction_surface.get_rect()
        instruction_rect.topleft = (self.left_offset, text_rect.bottom + 10)
        screen.blit(instruction_surface, instruction_rect)

    def count_pawns(self):
        player1_count = 0
        player2_count = 0
        
        for row in range(10):
            for col in range(10):
                player = self.board[row][col] % 10
                if player == 1:
                    player1_count += 1
                elif player == 2:
                    player2_count += 1
        
        return player1_count, player2_count
    
    def check_victory(self):
        player1_count, player2_count = self.count_pawns()
        
        if player1_count == 0:
            print("Le joueur 2 a gagné (plus de pions pour le joueur 1) !")
            self.running = False
            return 2
        if player2_count == 0:
            print("Le joueur 1 a gagné (plus de pions pour le joueur 2) !")
            self.running = False
            return 1

        if self.board[9][0] % 10 == 2 and self.board[9][9] % 10 == 2:
            print("Le joueur 1 a gagné (occupé les coins en bas à gauche) !")
            self.running = False
            return 1

        if self.board[0][0] % 10 == 1 and self.board[0][9] % 10 == 1:
            print("Le joueur 2 a gagné (occupé les coins en haut gauche et droite) !")
            self.running = False
            return 2

        return 0
    
    def play_ai_turn(self):
        from random import choice, shuffle

        if self.current_player != 2:
            return

        pawns = []
        for x in range(10):
            for y in range(10):
                if self.board[x][y] % 10 == 2:
                    pawns.append((x, y))

        shuffle(pawns)

        for x, y in pawns:
            couleur = self.board[x][y] // 10
            dir_list = self.directions.get(couleur, [])
            shuffle(dir_list)

            for dx, dy in dir_list:
                steps = 1
                while True:
                    new_x = x + dx * steps
                    new_y = y + dy * steps

                    if not (0 <= new_x < 10 and 0 <= new_y < 10):
                        break

                    if self.moves_rules.verify_move(self.board[x][y], x, y, new_x, new_y):
                        self.make_move(x, y, new_x, new_y)
                        print(f"IA a joué de ({x}, {y}) à ({new_x}, {new_y})")

                        winner = self.check_victory()
                        if winner == 0:
                            self.switch_player()
                        return

                    if couleur in [1, 2]:
                        break

                    if self.board[new_x][new_y] != 0:
                        break

                    steps += 1

        print("L'IA n'a pas trouvé de coup valide.")