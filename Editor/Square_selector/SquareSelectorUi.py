import pygame

from Board.Board import Board
from Board.Board_draw_tools import Board_draw_tools
from UI_tools.BaseUi import BaseUI
from Game_ui.Katarenga import Katarenga
from Game_ui.Congress import Congress
from Game_ui.Isolation import Isolation

class SquareSelectorUi(BaseUI):
    def __init__(self,gamemode, title="Select your square"):
        super().__init__(title)

        self.board_obj = Board()
        self.board_ui = Board_draw_tools()
        self.board = self.board_obj.get_default_board()
        
        self.gamemode = gamemode

        self.cell_size = 50
        self.grid_dim = 8
        self.grid_size = self.cell_size * self.grid_dim

        self.title_font = pygame.font.SysFont(None, 48)
        self.button_font = pygame.font.SysFont(None, 36)

        self.title_surface = self.title_font.render("Square Editor", True, (255, 255, 255))
        self.title_rect = self.title_surface.get_rect(center=(self.get_width() // 2, 40))
        self.top_offset = self.title_rect.bottom + 20
        self.left_offset = (self.get_width() - self.grid_size) // 2

        self.back_button_rect = pygame.Rect(20, 20, 120, 40)
        
        self.start_button_rect = pygame.Rect(self.get_width() // 2 - 100, self.get_height() - 70, 200, 50)

        self.board_obj.load_from_file("game_data.json")
        self.square_list = self.board_obj.get_square_list()
        self.square_buttons = self.create_square_buttons()

        self.selected_square = None
        self.holding_square = False 
        self.held_square_data = None
        
    def is_board_filled(self):
        for row in self.board:
            for cell in row:
                if cell == 0:
                    return False
        return True


    def create_square_buttons(self):
        buttons = []
        button_width = 150
        button_height = 40
        padding = 10

        total_width = len(self.square_list) * (button_width + padding) - padding
        start_x = (self.get_width() - total_width) // 2
        y = self.top_offset + self.grid_size + 30

        for idx, name in enumerate(self.square_list.keys()):
            x = start_x + idx * (button_width + padding)
            rect = pygame.Rect(x, y, button_width, button_height)
            buttons.append((name, rect))

        return buttons

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
                self.handle_click(event.pos)

            elif event.type == pygame.KEYDOWN and self.holding_square:
                if event.key == pygame.K_r:
                    self.rotate_square_right()
                elif event.key == pygame.K_l:
                    self.rotate_square_left()
                elif event.key == pygame.K_f:
                    self.flip_square()

    def handle_click(self, position):
        x, y = position
        square_rect = None

        if self.back_button_rect.collidepoint(x, y):
            self.running = False
            return

        if self.holding_square:
            if self.is_on_board(x, y):
                row = (y - self.top_offset) // self.cell_size
                col = (x - self.left_offset) // self.cell_size
                self.place_square_on_board(row, col)
                self.holding_square = False
                self.held_square_data = None
                return

        for name, rect in self.square_buttons:
            if rect.collidepoint(position):
                self.selected_square = name
                self.held_square_data = None
                self.holding_square = False
                print(f"Bouton sélectionné : {name}")
                return

        if self.selected_square:
            square_cell_size = 40
            square_width = 4 * square_cell_size
            square_offset_x = (self.get_width() - square_width) // 2
            square_offset_y = self.square_buttons[0][1].bottom + 30
            square_rect = pygame.Rect(square_offset_x, square_offset_y, square_width, square_width)

            if square_rect.collidepoint(position):
                self.held_square_data = self.square_list[self.selected_square]
                self.holding_square = True
                print(f"Square accroché : {self.selected_square}")
                return

        if self.is_board_filled():
            print("Lancement de la partie")
            
            pre_final_board = self.board_obj.create_final_board(self.board)
            
            final_board = self.board_obj.add_border_and_corners(pre_final_board)
            
            if self.gamemode == 1:
                katarenga = Katarenga(final_board)
                katarenga.run()
            elif self.gamemode == 2:
                congress = Congress(final_board)
                congress.run()
            elif self.gamemode == 3:
                isolation = Isolation(pre_final_board)
                isolation.run()
        else:
            print("Le plateau n'est pas encore rempli.")

        return


    def is_on_board(self, x, y):
        return (
            self.left_offset <= x < self.left_offset + self.grid_size
            and self.top_offset <= y < self.top_offset + self.grid_size
        )

    def place_square_on_board(self, row, col):
        if self.held_square_data is None:
            return

        # Détermine le coin du plateau
        row = 0 if row < 4 else 4
        col = 0 if col < 4 else 4

        for i in range(4):
            for j in range(4):
                self.board[row + i][col + j] = self.held_square_data[i][j]

        print(f"Square placé dans le quadrant ({row}, {col})")

    def rotate_square_right(self):
            self.held_square_data = self.board_obj.rotate_right(self.held_square_data)
            print("Square tourné à droite")

    def rotate_square_left(self):
        self.held_square_data = self.board_obj.rotate_left(self.held_square_data)
        print("Square tourné à droite")

    def flip_square(self):
        self.held_square_data = self.board_obj.flip_horizontal(self.held_square_data)
        print("Square retourné horizontalement")

    def draw(self):
        screen = self.get_screen()
        screen.fill((30, 30, 30))
        screen.blit(self.title_surface, self.title_rect)

        for row in range(8):
            for col in range(8):
                rect = pygame.Rect(
                    col * self.cell_size + self.left_offset,
                    row * self.cell_size + self.top_offset,
                    self.cell_size,
                    self.cell_size
                )
                color = self.board_ui.get_color_from_board(self.board[row][col] // 10)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (255, 255, 255), rect, 1)

        pygame.draw.rect(screen, (70, 70, 70), self.back_button_rect)
        pygame.draw.rect(screen, (255, 255, 255), self.back_button_rect, 2)
        back_text = self.button_font.render("Retour", True, (255, 255, 255))
        screen.blit(back_text, back_text.get_rect(center=self.back_button_rect.center))
        
        is_ready = self.is_board_filled()
        button_color = (0, 200, 0) if is_ready else (100, 100, 100)

        pygame.draw.rect(screen, button_color, self.start_button_rect)
        pygame.draw.rect(screen, (255, 255, 255), self.start_button_rect, 2)

        start_text = self.button_font.render("Lancer la partie", True, (255, 255, 255))
        screen.blit(start_text, start_text.get_rect(center=self.start_button_rect.center))

        for name, rect in self.square_buttons:
            pygame.draw.rect(screen, (70, 70, 70), rect)
            pygame.draw.rect(screen, (255, 255, 255), rect, 2)
            label = self.button_font.render(name, True, (255, 255, 255))
            screen.blit(label, label.get_rect(center=rect.center))

        if self.holding_square and self.held_square_data:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            square_cell_size = 40
            offset_x = mouse_x - 2 * square_cell_size
            offset_y = mouse_y - 2 * square_cell_size

            for row in range(4):
                for col in range(4):
                    value = self.held_square_data[row][col]
                    color = self.board_ui.get_color_from_board(value // 10)
                    rect = pygame.Rect(
                        offset_x + col * square_cell_size,
                        offset_y + row * square_cell_size,
                        square_cell_size,
                        square_cell_size
                    )
                    pygame.draw.rect(screen, color, rect)
                    pygame.draw.rect(screen, (255, 255, 255), rect, 1)

        elif self.selected_square:
            square = self.square_list[self.selected_square]
            square_cell_size = 40
            square_width = 4 * square_cell_size
            square_offset_x = (self.get_width() - square_width) // 2
            square_offset_y = self.square_buttons[0][1].bottom + 30

            for row in range(4):
                for col in range(4):
                    rect = pygame.Rect(
                        square_offset_x + col * square_cell_size,
                        square_offset_y + row * square_cell_size,
                        square_cell_size,
                        square_cell_size
                    )
                    value = square[row][col]
                    color = self.board_ui.get_color_from_board(value // 10)
                    pygame.draw.rect(screen, color, rect)
                    pygame.draw.rect(screen, (255, 255, 255), rect, 1)
                    
        instructions = [
            "L : rotate left",
            "R : rotate right",
            "F : flip side"
        ]

        for i, text in enumerate(instructions):
            instruction_surface = self.button_font.render(text, True, (255, 255, 255))
            screen.blit(instruction_surface, (20, 100 + i * 30))

if __name__ == "__main__":
    app = SquareSelectorUi()
    app.run()