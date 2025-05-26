import pygame
import sys
from Editor.EditorMenu import EditorMenu
from UI_tools.BaseUi import BaseUI
from Editor.Square_selector.SquareSelectorUi import SquareSelectorUi
from Online.Join_game_ui import JoinGameUI
from Online.Host_game_ui import HostGameUI


class MainMenuUI(BaseUI):
    def __init__(self, title="Katarenga"):
        super().__init__(title)

        btn_width = 300
        btn_height = 80
        spacing = 40
        num_buttons = 5

        total_height = num_buttons * btn_height + (num_buttons - 1) * spacing
        start_y = (self.get_height() - total_height) // 2
        x_center = (self.get_width() - btn_width) // 2

        labels_colors = [
            ("Katarenga", (70, 130, 180)),
            ("Congress", (60, 179, 113)),
            ("Isolation", (220, 20, 60)),
            ("Board Editor", (255, 140, 0)),
            ("Leave Game", (186, 85, 211))
        ]

        self.buttons = []
        for i, (label, color) in enumerate(labels_colors):
            rect = pygame.Rect(x_center, start_y + i * (btn_height + spacing), btn_width, btn_height)
            self.buttons.append({"label": label, "rect": rect, "color": color})

        side_x = 80
        side_btn_width = 200
        side_spacing = 120
        side_total_height = 2 * btn_height + side_spacing
        side_y = (self.get_height() - side_total_height) // 2

        self.buttons.append({
            "label": "Host a game",
            "rect": pygame.Rect(side_x, side_y, side_btn_width, btn_height),
            "color": (100, 149, 237)
        })

        self.buttons.append({
            "label": "Join a game",
            "rect": pygame.Rect(side_x, side_y + btn_height + side_spacing, side_btn_width, btn_height),
            "color": (72, 209, 204)
        })

        self.info_font = pygame.font.SysFont(None, 24)

        # Crée le fond bleu dégradé une fois
        self.background_surface = self.create_blue_gradient_background()

    def create_blue_gradient_background(self):
        "Fond dégardé bleu"
        width, height = self.get_width(), self.get_height()
        surface = pygame.Surface((width, height))
        center_x, center_y = width // 2, height // 2
        max_dist = (center_x ** 2 + center_y ** 2) ** 0.5

        for y in range(height):
            for x in range(width):
                dx, dy = x - center_x, y - center_y
                dist = (dx ** 2 + dy ** 2) ** 0.5
                ratio = dist / max_dist

                r = int((1 - ratio) * 100 + ratio * 10)
                g = int((1 - ratio) * 149 + ratio * 20)
                b = int((1 - ratio) * 237 + ratio * 60)

                surface.set_at((x, y), (r, g, b))

        return surface

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_click(event.pos)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

    def handle_click(self, position):
        for button in self.buttons:
            if button["rect"].collidepoint(position):
                label = button["label"]
                print(f"Launching {label}...")
                if label == "Katarenga":
                    SquareSelectorUi(1).run()
                elif label == "Congress":
                    SquareSelectorUi(2).run()
                elif label == "Isolation":
                    SquareSelectorUi(3).run()
                elif label == "Board Editor":
                    EditorMenu().run()
                elif label == "Leave Game":
                    self.running = False
                elif label == "Host a game":
                    HostGameUI().run()
                elif label == "Join a game":
                    JoinGameUI().run()

    def update(self):
        pass

    def draw(self):
        self.get_screen().blit(self.background_surface, (0, 0))
        for button in self.buttons:
            pygame.draw.rect(self.get_screen(), button["color"], button["rect"], border_radius=12)
            self.draw_text(button["label"], button["rect"])

    def draw_text(self, text, rect):
        txt_surface = self.font.render(text, True, (255, 255, 255))
        txt_rect = txt_surface.get_rect(center=rect.center)
        self.get_screen().blit(txt_surface, txt_rect)


if __name__ == "__main__":
    app = MainMenuUI()
    app.run()
