import pygame
import copy
from UI_tools.BaseUi import BaseUI
from Board.Board_draw_tools import Board_draw_tools

class Katarenga(BaseUI):
    def __init__(self, board, title="Katarenga"):
        super().__init__(title)

        # Simple error checking
        if board is None:
            raise ValueError("Le plateau ne peut pas être None")
        
        
        self.board = self.place_pawn_katarenga(board)
        self.board_ui = Board_draw_tools()
        
        self.cell_size = 60
        self.grid_dim = 8
        self.grid_size = self.cell_size * self.grid_dim
        
        self.top_offset = 80
        self.left_offset = (self.get_width() - self.grid_size) // 2
        
        self.title_font = pygame.font.SysFont(None, 48)
        self.title_surface = self.title_font.render("Katarenga", True, (255, 255, 255))
        self.title_rect = self.title_surface.get_rect(center=(self.get_width() // 2, 40))
        
        self.back_button_rect = pygame.Rect(20, 20, 120, 40)
        
       
        self.current_player = 1  
        self.selected_pawn = None  
        
        
        self.info_font = pygame.font.SysFont(None, 36)

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

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
            if 0 <= row < 8 and 0 <= col < 8:
                self.process_move(row, col)

    def place_pawn_katarenga(self, board):
        
        modified_board = copy.deepcopy(board)
        
        # Pawn from player 2 
        for col in range(8):
            color_code = modified_board[0][col] // 10
            modified_board[0][col] = color_code * 10 + 2

        # Pawn from player 1 
        for col in range(8):
            color_code = modified_board[7][col] // 10
            modified_board[7][col] = color_code * 10 + 1
        
        return modified_board
    
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
                    self.switch_player()
                else:
                    print("Mouvement invalide")
