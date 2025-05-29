import pygame
import copy
import time
import random
from UI_tools.BaseUi import BaseUI
from Board.Board_draw_tools import Board_draw_tools
from Game_ui.move_rules import Moves_rules


class Katarenga(BaseUI):
    def __init__(self, ai, board, title="Katarenga"):
        super().__init__(title)

        if board is None:
            raise ValueError("Board can't be None")  # check input

        self.board = self.place_pawn_katarenga(board)  # setup pawns
        self.board_ui = Board_draw_tools()  # drawing helper
        self.moves_rules = Moves_rules(self.board)  # move rules

        self.cell_size = 60  # size of one cell
        self.grid_dim = 10  # 10x10 grid
        self.grid_size = self.cell_size * self.grid_dim  # total size

        self.top_offset = 80  # vertical offset
        self.left_offset = (self.get_width() - self.grid_size) // 2  # center horizontally

        self.title_font = pygame.font.SysFont(None, 48)  # font for title
        self.title_surface = self.title_font.render("Katarenga", True, (255, 255, 255))
        self.title_rect = self.title_surface.get_rect(center=(self.get_width() // 2, 40))

        self.back_button_rect = pygame.Rect(20, 20, 120, 40)  # back button

        self.current_player = 1  # player 1 starts
        self.selected_pawn = None  # no pawn selected

        self.__ai = ai  # AI mode on/off

        self.info_font = pygame.font.SysFont(None, 36)  # font for info text

        # Movement directions by pawn color
        self.directions = {
            1: [(dx, dy) for dx in [-1,0,1] for dy in [-1,0,1] if dx != 0 or dy != 0],  # blue = all around
            2: [(2,1),(1,2),(-1,2),(-2,1),(-2,-1),(-1,-2),(1,-2),(2,-1)],  # green = knight moves
            3: [(-1,-1),(-1,1),(1,-1),(1,1)],  # yellow = diagonals
            4: [(-1,0),(1,0),(0,-1),(0,1)]  # red = straight lines
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
                self.running = False  # quit game
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.back_button_rect.collidepoint(event.pos):
                    self.running = False  # back clicked
                else:
                    self.handle_board_click(event.pos)  # board clicked

    def handle_board_click(self, pos):
        x, y = pos
        if (self.left_offset <= x < self.left_offset + self.grid_size and
            self.top_offset <= y < self.top_offset + self.grid_size):

            col = (x - self.left_offset) // self.cell_size
            row = (y - self.top_offset) // self.cell_size

            if 0 <= row < self.grid_dim and 0 <= col < self.grid_dim:
                self.process_move(row, col)

    def place_pawn_katarenga(self, board):
        new_board = copy.deepcopy(board)  # copy board to avoid mutation

        # Player 2 pawns top row
        for col in range(1, 9):
            color = new_board[1][col] // 10
            new_board[1][col] = color * 10 + 2

        # Player 1 pawns bottom row
        for col in range(1, 9):
            color = new_board[8][col] // 10
            new_board[8][col] = color * 10 + 1

        return new_board

    def process_move(self, row, col):
        cell_value = self.board[row][col]
        player_on_cell = cell_value % 10

        if self.selected_pawn is None:
            if player_on_cell == self.current_player:
                self.selected_pawn = (row, col)  # select pawn
        else:
            sr, sc = self.selected_pawn
            if (row, col) == self.selected_pawn:
                self.selected_pawn = None  # deselect pawn
            elif player_on_cell == self.current_player:
                self.selected_pawn = (row, col)  # switch selection
            else:
                # Check special moves for corners or normal move
                if self.is_valid_move(sr, sc, row, col):
                    self.make_move(sr, sc, row, col)
                    self.selected_pawn = None
                    if self.check_victory() == 0:
                        self.switch_player()
                else:
                    print("Invalid move")  # no cheating baka

    def is_valid_move(self, fr, fc, tr, tc):
        case_color = self.board[fr][fc]
        return self.moves_rules.verify_move(case_color, fr, fc, tr, tc)

    def make_move(self, fr, fc, tr, tc):
        dest_color = self.board[tr][tc] // 10
        origin_color = self.board[fr][fc] // 10
        self.board[fr][fc] = origin_color * 10  # empty old spot
        self.board[tr][tc] = dest_color * 10 + self.current_player  # place pawn
        print(f"Moved from ({fr},{fc}) to ({tr},{tc})")

    def switch_player(self):
        self.current_player = 2 if self.current_player == 1 else 1
        print(f"Player {self.current_player}'s turn")

    def check_victory(self):
        player1_count = 0
        player2_count = 0
        
        for row in range(self.grid_dim):
            for col in range(self.grid_dim):
                player = self.board[row][col] % 10
                if player == 1:
                    player1_count += 1
                elif player == 2:
                    player2_count += 1
        
        # Victory by elimination
        if player1_count == 0:
            print("Player 2 wins by elimination!")
            self.running = False
            return 2
        if player2_count == 0:
            print("Player 1 wins by elimination!")
            self.running = False
            return 1
        
        # Victory by corners
        if self.grid_dim >= 10:
            if self.board[9][0] % 10 == 1 and self.board[9][9] % 10 == 1:
                print("Player 1 wins by corner occupation!")
                self.running = False
                return 1
            
            if self.board[0][0] % 10 == 2 and self.board[0][9] % 10 == 2:
                print("Player 2 wins by corner occupation!")
                self.running = False
                return 2
        
        return 0  # No victory

    def play_ai_turn(self):
        # Simple AI for local mode
        player_pawns = []
        for row in range(self.grid_dim):
            for col in range(self.grid_dim):
                if self.board[row][col] % 10 == 2:
                    player_pawns.append((row, col))
        
        if not player_pawns:
            return
        
        random.shuffle(player_pawns)
        for from_row, from_col in player_pawns:
            possible_moves = []
            for to_row in range(self.grid_dim):
                for to_col in range(self.grid_dim):
                    if self.is_valid_move(from_row, from_col, to_row, to_col):
                        possible_moves.append((to_row, to_col))
            
            if possible_moves:
                to_row, to_col = random.choice(possible_moves)
                self.make_move(from_row, from_col, to_row, to_col)
                
                if self.check_victory() == 0:
                    self.switch_player()
                return

    def draw_pawn(self, screen, rect, player_code):
        center = rect.center
        radius = self.cell_size // 3
        
        if player_code == 1:
            pygame.draw.circle(screen, (255, 255, 255), center, radius)
            pygame.draw.circle(screen, (0, 0, 0), center, radius, 2)
        elif player_code == 2:
            pygame.draw.circle(screen, (0, 0, 0), center, radius)
            pygame.draw.circle(screen, (255, 255, 255), center, radius, 2)

    def draw(self):
        screen = self.get_screen()
        screen.fill((30, 30, 30))  # dark background
        screen.blit(self.title_surface, self.title_rect)  # draw title

        for row in range(self.grid_dim):
            for col in range(self.grid_dim):
                rect = pygame.Rect(
                    col * self.cell_size + self.left_offset,
                    row * self.cell_size + self.top_offset,
                    self.cell_size,
                    self.cell_size
                )
                value = self.board[row][col]
                color_code = value // 10
                player_code = value % 10

                color = self.board_ui.get_color_from_board(color_code)
                pygame.draw.rect(screen, color, rect)

                if self.selected_pawn == (row, col):
                    pygame.draw.rect(screen, (255, 255, 0), rect, 4)  # highlight selected

                pygame.draw.rect(screen, (255, 255, 255), rect, 1)  # grid lines

                if player_code > 0:
                    self.draw_pawn(screen, rect, player_code)  # draw pawn

        # Draw back button
        pygame.draw.rect(screen, (180, 180, 180), self.back_button_rect)
        back_text = self.info_font.render("Back", True, (0, 0, 0))
        back_rect = back_text.get_rect(center=self.back_button_rect.center)
        screen.blit(back_text, back_rect)

        # Draw current player info
        player_text = self.info_font.render(f"Player {self.current_player}'s turn", True, (255, 255, 255))
        screen.blit(player_text, (20, self.get_height() - 50))