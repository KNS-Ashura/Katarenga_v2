from Game_ui.move_rules import Moves_rules
import pygame
from UI_tools.BaseUi import BaseUI
from Board.Board_draw_tools import Board_draw_tools
import random
import time

class Isolation(BaseUI):
    def __init__(self,ai, board, title="Isolation"):
        super().__init__(title)
        self.board = board
        self.rules = Moves_rules(board)
        self.board_ui = Board_draw_tools()
        
        self.cell_size = 60
        self.grid_dim = 8
        self.grid_size = self.cell_size * self.grid_dim
        
        self.top_offset = 80
        self.left_offset = (self.get_width() - self.grid_size) // 2
        
        self.title_font = pygame.font.SysFont(None, 48)
        self.title_surface = self.title_font.render("Isolation", True, (255, 255, 255))
        self.title_rect = self.title_surface.get_rect(center=(self.get_width() // 2, 40))
        
        self.back_button_rect = pygame.Rect(20, 20, 120, 40)
        
        self.current_player = 1
        self.total_moves = 0
        self.max_moves = self.grid_dim * self.grid_dim

        self.__AI = ai

    def run(self):
        self.running = True
        while self.running:
            self.handle_events()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

            if self.__AI and self.current_player == 2 and self.running:
                time.sleep(2)
                self.play_ai_move()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.back_button_rect.collidepoint(event.pos):
                    self.running = False
                else:
                    self.handle_click(event.pos)

    def handle_click(self, pos):
        if self.__AI and self.current_player == 2:
            return
        
        x, y = pos
        col = (x - self.left_offset) // self.cell_size
        row = (y - self.top_offset) // self.cell_size

        if 0 <= row < self.grid_dim and 0 <= col < self.grid_dim:
            case = self.board[row][col]
            if case % 10 == 0 and not self.in_prise(row, col):
                color = case // 10
                self.board[row][col] = color * 10 + self.current_player
                self.total_moves += 1
                if self.total_moves >= self.max_moves or not self.can_play():
                    print(f"Le joueur {self.current_player} gagne !")
                    self.running = False
                else:
                    self.current_player = 2 if self.current_player == 1 else 1


    def in_prise(self, x, y):
        for i in range(self.grid_dim):
            for j in range(self.grid_dim):
                case = self.board[i][j]
                if case % 10 != 0:
                    if self.rules.verify_move(case, i, j, x, y):
                        return True
        return False

    def can_play(self):
        for i in range(self.grid_dim):
            for j in range(self.grid_dim):
                case = self.board[i][j]
                if case not in (0, 50, 60) and case % 10 == 0 and not self.in_prise(i, j):
                    return True
        return False
    
    def draw(self):
        screen = self.get_screen()
        screen.fill((30, 30, 30))
        screen.blit(self.title_surface, self.title_rect)

        for row in range(self.grid_dim):
            for col in range(self.grid_dim):
                rect = pygame.Rect(
                    col * self.cell_size + self.left_offset,
                    row * self.cell_size + self.top_offset,
                    self.cell_size,
                    self.cell_size
                )
                value = self.board[row][col]
                color = self.board_ui.get_color_from_board(value // 10)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (255, 255, 255), rect, 1)

                if value % 10 != 0:
                    center = rect.center
                    radius = self.cell_size // 3
                    if value % 10 == 1:
                        pygame.draw.circle(screen, (255, 0, 0), center, radius)
                    elif value % 10 == 2:
                        pygame.draw.circle(screen, (0, 0, 255), center, radius)

        pygame.draw.rect(screen, (70, 70, 70), self.back_button_rect)
        pygame.draw.rect(screen, (255, 255, 255), self.back_button_rect, 2)
        back_text = pygame.font.SysFont(None, 36).render("Retour", True, (255, 255, 255))
        screen.blit(back_text, back_text.get_rect(center=self.back_button_rect.center))

    def play_ai_move(self):
        possibles = []
        for i in range(self.grid_dim):
            for j in range(self.grid_dim):
                case = self.board[i][j]
                if case not in (0, 50, 60) and case % 10 == 0 and not self.in_prise(i, j):
                    possibles.append((i, j))

        if not possibles:
            print("L'IA ne peut plus jouer, joueur 1 gagne !")
            self.running = False
            return

        i, j = random.choice(possibles)
        case = self.board[i][j]
        color = case // 10
        self.board[i][j] = color * 10 + 2
        self.total_moves += 1

        if self.total_moves >= self.max_moves or not self.can_play():
            print("L'IA (joueur 2) gagne !")
            self.running = False
        else:
            self.current_player = 1