import pygame
from Editor.Square_editor.SquareEditor_ui import SquareEditorUi
from Editor.Square_selector.SquareSelectorUi import SquareSelectorUi
from Editor.Square_Manager.SquareManagerUi import SquareManagerUi
from UI_tools.BaseUi import BaseUI

class EditorMenu(BaseUI):
    def __init__(self, title="Katarenga"):
        super().__init__(title)

        btn_width = 300
        btn_height = 80
        spacing = 40
        num_buttons = 3

        total_height = num_buttons * btn_height + (num_buttons - 1) * spacing
        start_y = (self.get_height() - total_height) // 2 - 100
        x_center = (self.get_width() - btn_width) // 2

        labels_colors = [
            ("Edit Square", (70, 130, 180)),
            ("Manage squares", (60, 179, 113)),
            ("Create Board", (186, 85, 211)),
            ("Go to menu", (234, 182, 118))
        ]

        self.buttons = []
        for i, (label, color) in enumerate(labels_colors):
            rect = pygame.Rect(x_center, start_y + i * (btn_height + spacing), btn_width, btn_height)
            self.buttons.append({"label": label, "rect": rect, "color": color})

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_click(event.pos)

    def handle_click(self, position):
        for button in self.buttons:
            if button["rect"].collidepoint(position):
                label = button["label"]
                if label == "Edit Square":
                    print("Launching Editor...")
                    Editor = SquareEditorUi()
                    Editor.run()

                elif label == "Manage squares":
                    print("Launching Square Manager...")
                    Manager = SquareManagerUi()
                    Manager.run()

                elif label == "Create Board":
                    print("Launching Board Creator...")
                    Creator = SquareSelectorUi()
                    Creator.run()

                elif label == "Go to menu":
                    print("Returning to Menu...")
                    self.running = False

    def update(self):
        pass

    def draw(self):
        self.get_screen().fill((30, 30, 30))
        for button in self.buttons:
            pygame.draw.rect(self.get_screen(), button["color"], button["rect"], border_radius=12)
            self.draw_text(button["label"], button["rect"])

    def draw_text(self, text, rect):
        txt_surface = self.font.render(text, True, (255, 255, 255))
        txt_rect = txt_surface.get_rect(center=rect.center)
        self.get_screen().blit(txt_surface, txt_rect)

if __name__ == "__main__":
    while True:
        app = EditorMenu()
        app.run()