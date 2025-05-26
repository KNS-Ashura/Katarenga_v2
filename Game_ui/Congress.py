import pygame
import copy
import random
from collections import deque

from UI_tools.BaseUi import BaseUI
from Board.Board_draw_tools import Board_draw_tools
from Game_ui.move_rules import Moves_rules

class Congress(BaseUI):
    def __init__(self,ai, board, title="Congress"):
        super().__init__(title)

        if board is None:
            raise ValueError("Board cannot be None")

        self.base_board = copy.deepcopy(board)

        # grid setup
        self.cell_size = 60
        self.grid_dim  = 10
        self.grid_size = self.cell_size * self.grid_dim
        self.top_offset  = 80
        self.left_offset = (self.get_width() - self.grid_size) // 2

        # title
        self.title_font    = pygame.font.SysFont(None, 48)
        self.title_surface = self.title_font.render("Congress", True, (255, 255, 255))
        self.title_rect    = self.title_surface.get_rect(center=(self.get_width() // 2, 40))
        self.back_button_rect = pygame.Rect(20, 20, 120, 40)

        # place pawns with quadrant shift
        self.board = self.place_pawn_congress(self.base_board)

        self.board_ui    = Board_draw_tools()
        self.moves_rules = Moves_rules(self.board)

        self.current_player = 1
        self.selected_pawn  = None
        self.info_font = pygame.font.SysFont(None, 36)
        
        self.__ai = ai

    def place_pawn_congress(self, base_board):
        new_board = copy.deepcopy(base_board)
        for i in range(self.grid_dim):
            for j in range(self.grid_dim):
                color_code = new_board[i][j] // 10
                new_board[i][j] = color_code * 10

        blacks = [(0,1),(0,5),(1,9),(4,0),(5,9),(8,0),(9,4),(9,8)]
        whites = [(0,4),(0,8),(1,0),(4,9),(5,0),(8,9),(9,1),(9,5)]

        def shift(r, c):
            if r < 5 and c < 5:
                r2, c2 = r + 1, c + 1
            elif r < 5 and c >= 5:
                r2, c2 = r + 1, c - 1
            elif r >= 5 and c < 5:
                r2, c2 = r - 1, c + 1
            else:
                r2, c2 = r - 1, c - 1
            return max(0, min(9, r2)), max(0, min(9, c2))

        for r, c in blacks:
            r2, c2 = shift(r, c)
            code = new_board[r2][c2] // 10
            new_board[r2][c2] = code * 10 + 2

        for r, c in whites:
            r2, c2 = shift(r, c)
            code = new_board[r2][c2] // 10
            new_board[r2][c2] = code * 10 + 1

        return new_board

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
            
            if self.__ai and self.current_player == 2:
                self.congress_ai()

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
        if (self.left_offset <= x < self.left_offset + self.grid_size and
            self.top_offset  <= y < self.top_offset  + self.grid_size):
            col = (x - self.left_offset) // self.cell_size
            row = (y - self.top_offset)  // self.cell_size
            if 0 <= row < self.grid_dim and 0 <= col < self.grid_dim:
                self.process_move(row, col)

    def process_move(self, row, col):
        val = self.board[row][col]
        owner = val % 10

        if self.selected_pawn is None:
            if owner == self.current_player:
                self.selected_pawn = (row, col)
                print(f"Pion selected at ({row}, {col})")
        else:
            sel_r, sel_c = self.selected_pawn
            if (row, col) == (sel_r, sel_c):
                self.selected_pawn = None
                print("Pawn deselected")
            elif owner == self.current_player:
                self.selected_pawn = (row, col)
                print(f"New pawn selected at ({row}, {col})")
            else:
                if self.board[row][col] % 10 == 0 and \
                   self.is_valid_move(sel_r, sel_c, row, col):
                    self.make_move(sel_r, sel_c, row, col)
                    self.selected_pawn = None
                    if self.check_victory(self.current_player):
                        print(f"Player {self.current_player} wins!")
                        self.running = False
                    else:
                        self.switch_player()
                else:
                    print("Invalid move or square occupied")

    def is_valid_move(self, fr, fc, tr, tc):
        case_color = self.board[fr][fc]
        return self.moves_rules.verify_move(case_color, fr, fc, tr, tc)

    def make_move(self, fr, fc, tr, tc):
        dest_color = self.base_board[tr][tc] // 10
        orig_color = self.base_board[fr][fc] // 10
        self.board[fr][fc] = orig_color * 10
        self.board[tr][tc] = dest_color * 10 + self.current_player
        print(f"Moved from ({fr}, {fc}) to ({tr}, {tc})")

    def switch_player(self):
        self.current_player = 2 if self.current_player == 1 else 1
        print(f"Player {self.current_player}'s turn")

    def check_victory(self, player):
        positions = [(i, j) for i in range(self.grid_dim) for j in range(self.grid_dim)
                     if self.board[i][j] % 10 == player]
        if not positions:
            return False
        visited = set([positions[0]])
        queue   = deque([positions[0]])
        while queue:
            x, y = queue.popleft()
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.grid_dim and 0 <= ny < self.grid_dim and
                    (nx, ny) not in visited and self.board[nx][ny] % 10 == player):
                    visited.add((nx, ny))
                    queue.append((nx, ny))
        return len(visited) == len(positions)

    def draw(self):
        screen = self.get_screen()

        # 💡 Affiche le fond généré par BaseUI
        screen.blit(self.get_background(), (0, 0))

        screen.blit(self.title_surface, self.title_rect)

        for row in range(self.grid_dim):
            for col in range(self.grid_dim):
                rect = pygame.Rect(
                    col * self.cell_size + self.left_offset,
                    row * self.cell_size + self.top_offset,
                    self.cell_size,
                    self.cell_size
                )
                base_val   = self.base_board[row][col]
                color_code = base_val // 10
                color      = self.board_ui.get_color_from_board(color_code)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (255, 255, 255), rect, 1)
                if self.selected_pawn == (row, col):
                    pygame.draw.rect(screen, (255, 255, 0), rect, 4)
                player = self.board[row][col] % 10
                if player > 0:
                    self.draw_pawn(screen, rect, player)

        pygame.draw.rect(screen, (70, 70, 70), self.back_button_rect)
        pygame.draw.rect(screen, (255, 255, 255), self.back_button_rect, 2)
        back_text = pygame.font.SysFont(None, 36).render("Back", True, (255, 255, 255))
        screen.blit(back_text, back_text.get_rect(center=self.back_button_rect.center))
        self.draw_game_info(screen)

    def draw_pawn(self, screen, rect, player):
        cx, cy = rect.center
        r = self.cell_size // 4
        color = (0, 0, 255) if player == 1 else (255, 0, 0)
        pygame.draw.circle(screen, color, (cx, cy), r)
        pygame.draw.circle(screen, (255, 255, 255), (cx, cy), r, 2)

    def draw_game_info(self, screen):
        text = f"Player {self.current_player}'s turn"
        color = (0, 0, 255) if self.current_player == 1 else (255, 0, 0)
        surf = self.info_font.render(text, True, color)
        rect = surf.get_rect()
        rect.topleft = (self.left_offset, self.top_offset + self.grid_size + 40)
        screen.blit(surf, rect)
        instr = "Click empty square to move pawn" if self.selected_pawn else "Click your pawn to select"
        instr_surf = pygame.font.SysFont(None, 24).render(instr, True, (200, 200, 200))
        instr_rect = instr_surf.get_rect()
        instr_rect.topleft = (self.left_offset, rect.bottom + 10)
        screen.blit(instr_surf, instr_rect)
<<<<<<< HEAD
=======
        
    def congress_ai(self):
        positions = [(i, j) for i in range(self.grid_dim) for j in range(self.grid_dim)
                     if self.board[i][j] % 10 == self.current_player]

        random.shuffle(positions)

        directions = [(-1,0), (1,0), (0,-1), (0,1)]

        for fr, fc in positions:
            random.shuffle(directions)
            for dx, dy in directions:
                tr, tc = fr + dx, fc + dy
                if 0 <= tr < self.grid_dim and 0 <= tc < self.grid_dim:
                    if self.board[tr][tc] % 10 == 0:
                        if self.is_valid_move(fr, fc, tr, tc):
                            self.make_move(fr, fc, tr, tc)
                            print(f"AI moved from ({fr},{fc}) to ({tr},{tc})")
                            if self.check_victory(self.current_player):
                                print(f"AI (Player {self.current_player}) wins!")
                                self.running = False
                            else:
                                self.switch_player()
                            return
        print("AI has no valid moves.")
>>>>>>> 7c031064f1965119bda02b7d11665d481d2607e3
