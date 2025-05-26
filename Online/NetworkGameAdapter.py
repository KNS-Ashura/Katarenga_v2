import pygame
from UI_tools.BaseUi import BaseUI
from Board.Board_draw_tools import Board_draw_tools
from Game_ui.move_rules import Moves_rules


from Game_ui.Katarenga import Katarenga
from Game_ui.Congress import Congress
from Game_ui.Isolation import Isolation

class NetworkGameAdapter(BaseUI):
    
    def __init__(self, game_session, title="Jeu en réseau"):
        super().__init__(title)
        
        # Session network games
        self.session = game_session
        self.board = game_session.board
        self.game_type = game_session.game_type
        self.local_player = 1 if game_session.is_host else 2
        
        # Create an instance of the game to reuse its methods
        self.game_instance = self._create_game_instance()
        
        # network game state
        self.selected_pawn = None
        self.current_player = 1
        self.game_finished = False
        self.status_message = ""
        self.status_color = (255, 255, 255)
        
        
        self.session.set_game_callbacks(
            board_update=self.on_board_update,
            player_change=self.on_player_change,
            game_end=self.on_game_end
        )
        
        print(f"[NETWORK] Network game intialize - Type: {self.game_type}, Joueur local: {self.local_player}")
    
    def _create_game_instance(self):
        ai_disabled = False
        
        if self.game_type == 1:
            return Katarenga(ai_disabled, self.board)
        elif self.game_type == 2:
            return Congress(ai_disabled, self.board)
        elif self.game_type == 3:
            return Isolation(ai_disabled, self.board)
        else:
            raise ValueError(f"Error: {self.game_type}")
    
    def run(self):
        self.session.start_game()
        
        while self.running and not self.game_finished:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
        
        print("[NETWORK] Game end")
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_click(event.pos)
    
    def handle_click(self, pos):
        # Check who is the current player
        if self.current_player != self.local_player:
            self.set_status("It's not your turn", (255, 255, 100))
            return
        
       
        if self.game_type in [1, 2]:  # Katarenga and Congress
            self._handle_board_click_katarenga_congress(pos)
        elif self.game_type == 3:  # Isolation
            self._handle_click_isolation(pos)
    
    def _handle_board_click_katarenga_congress(self, pos):
        row, col = self._get_board_position(pos)
        if row is None or col is None:
            return
        
        
        cell_value = self.board[row][col]
        player_on_cell = cell_value % 10
        
        if self.selected_pawn is None:
            # Selec pawn
            if player_on_cell == self.local_player:
                self.selected_pawn = (row, col)
                self.set_status(f"Pawn select in ({row}, {col})", (100, 255, 100))
            else:
                self.set_status("elect one of your pawns", (255, 255, 100))
        else:
            #moovement or deselection
            if (row, col) == self.selected_pawn:
                self.selected_pawn = None
                self.set_status("Pawn unselect", (200, 200, 200))
            elif player_on_cell == self.local_player:
                self.selected_pawn = (row, col)
                self.set_status(f"New pawn selected", (100, 255, 100))
            else:
                from_row, from_col = self.selected_pawn
                
                if self._is_valid_move(from_row, from_col, row, col):
                    if self.session.make_move((from_row, from_col), (row, col)):
                        self.selected_pawn = None
                        self.set_status("Move right", (100, 255, 100))
                    else:
                        self.set_status("Error network", (255, 100, 100))
                else:
                    self.set_status("Move invalid", (255, 100, 100))
    
    def _handle_click_isolation(self, pos):
        row, col = self._get_board_position(pos)
        if row is None or col is None:
            return
        
        case = self.board[row][col]
        if case % 10 == 0 and not self.game_instance.in_prise(row, col):
            
            if self.session.make_move(None, (row, col)):  
                self.set_status("Case put", (100, 255, 100))
            else:
                self.set_status("Error network", (255, 100, 100))
        else:
            self.set_status("Case invalid", (255, 100, 100))
    
    def _get_board_position(self, pos):
        x, y = pos
        
        if hasattr(self.game_instance, 'left_offset'):
            left_offset = self.game_instance.left_offset
            top_offset = self.game_instance.top_offset
            cell_size = self.game_instance.cell_size
            grid_dim = self.game_instance.grid_dim
        else:
            left_offset = (self.get_width() - 600) // 2
            top_offset = 80
            cell_size = 60
            grid_dim = len(self.board)
        
        if not (left_offset <= x < left_offset + grid_dim * cell_size and
                top_offset <= y < top_offset + grid_dim * cell_size):
            return None, None
        
        col = (x - left_offset) // cell_size
        row = (y - top_offset) // cell_size
        
        if 0 <= row < grid_dim and 0 <= col < grid_dim:
            return row, col
        return None, None
    
    def _is_valid_move(self, from_row, from_col, to_row, to_col):
        
        if hasattr(self.game_instance, 'is_valid_move'):
            return self.game_instance.is_valid_move(from_row, from_col, to_row, to_col)
        else:
            case_color = self.board[from_row][from_col]
            return self.game_instance.moves_rules.verify_move(case_color, from_row, from_col, to_row, to_col)
    
    def on_board_update(self, new_board):
        self.board = new_board
        self.game_instance.board = new_board  # Synchro the board with the game instance
        print("[NETWORK] Board updated")
    
    def on_player_change(self, new_player):
        self.current_player = new_player
        if new_player == self.local_player:
            self.set_status("Your turn", (100, 255, 100))
        else:
            self.set_status("Opponent turn", (255, 255, 100))
    
    def on_game_end(self, winner):
        self.game_finished = True
        if winner == "Déconnexion":
            self.set_status("Opponent disconnected", (255, 100, 100))
        elif winner == self.local_player:
            self.set_status("You win!", (100, 255, 100))
        else:
            self.set_status("You lose", (255, 100, 100))
    
    def set_status(self, message, color):
        self.status_message = message
        self.status_color = color
    
    def update(self):
        if hasattr(self.game_instance, 'update'):
            self.game_instance.update()
    
    def draw(self):
        screen = self.get_screen()
        
        if hasattr(self.game_instance, 'draw'):
            original_screen = self.game_instance.get_screen()
            original_selected = getattr(self.game_instance, 'selected_pawn', None)
            original_current = getattr(self.game_instance, 'current_player', None)
            
            self.game_instance._BaseUI__screen = screen  
            if hasattr(self.game_instance, 'selected_pawn'):
                self.game_instance.selected_pawn = self.selected_pawn
            if hasattr(self.game_instance, 'current_player'):
                self.game_instance.current_player = self.current_player
            
            self.game_instance.draw()
            
            self.game_instance._BaseUI__screen = original_screen
            if hasattr(self.game_instance, 'selected_pawn'):
                self.game_instance.selected_pawn = original_selected
            if hasattr(self.game_instance, 'current_player'):
                self.game_instance.current_player = original_current
        else:
            self._draw_basic()
        
        self._draw_network_info(screen)
    
    def _draw_basic(self):
        screen = self.get_screen()
        screen.fill((30, 30, 30))
        
        board_ui = Board_draw_tools()
        
        # Draw the board
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                rect = pygame.Rect(
                    col * 60 + 100,
                    row * 60 + 100,
                    60, 60
                )
                
                value = self.board[row][col]
                color = board_ui.get_color_from_board(value // 10)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (255, 255, 255), rect, 1)
                
                # Pawns
                if value % 10 > 0:
                    center = rect.center
                    pawn_color = (0, 0, 255) if value % 10 == 1 else (255, 0, 0)
                    pygame.draw.circle(screen, pawn_color, center, 20)
    
    def _draw_network_info(self, screen):
        if self.status_message:
            status_surface = pygame.font.SysFont(None, 28).render(
                f"[RÉSEAU] {self.status_message}", True, self.status_color
            )
            screen.blit(status_surface, (20, self.get_height() - 60))
        
        player_info = f"You: Player {self.local_player}"
        player_color = (0, 0, 255) if self.local_player == 1 else (255, 0, 0)
        player_surface = pygame.font.SysFont(None, 24).render(player_info, True, player_color)
        screen.blit(player_surface, (20, self.get_height() - 30))