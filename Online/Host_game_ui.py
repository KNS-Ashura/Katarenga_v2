import pygame
from UI_tools.BaseUi import BaseUI
from Online.Client import Client  
from Online.Server import ServerManager  
from Editor.Square_selector.SquareSelectorUi import SquareSelectorUi


class HostGameUI(BaseUI):
    def __init__(self, title="Host Game"):
        super().__init__(title)
        self.server_manager = ServerManager()
        self.server_started = self.server_manager.start_server_ui()

        self.title_font = pygame.font.SysFont(None, 48)
        self.button_font = pygame.font.SysFont(None, 36)
        self.info_font = pygame.font.SysFont(None, 24)

        self.title_surface = self.title_font.render("Host Game - Select Mode", True, (255, 255, 255))
        self.title_rect = self.title_surface.get_rect(center=(self.get_width() // 2, 100))

        self.back_button_rect = pygame.Rect(20, 20, 120, 40)
        self.server_info_y = self.get_height() - 150

        self.game_buttons = []
        self.build_game_buttons()

    def build_game_buttons(self):
        game_modes = [("Katarenga", (70, 130, 180), 1), ("Congress", (60, 179, 113), 2), ("Isolation", (220, 20, 60), 3)]
        bw, bh, spacing = 300, 80, 40
        start_y = (self.get_height() - (len(game_modes) * (bh + spacing))) // 2
        x_center = (self.get_width() - bw) // 2

        for i, (label, color, mode) in enumerate(game_modes):
            rect = pygame.Rect(x_center, start_y + i * (bh + spacing), bw, bh)
            self.game_buttons.append({"label": label, "rect": rect, "color": color, "gamemode": mode})

    def run(self):
        if not self.server_started:
            print("Erreur: Impossible to start the server.")
            return

        while self.running:
            self.handle_events()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        if self.server_manager.is_server_running():
            self.server_manager.stop_server_ui()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_click(event.pos)

    def handle_click(self, pos):
        if self.back_button_rect.collidepoint(pos):
            self.running = False
            return

        status = self.server_manager.get_server_status()
        if status['clients_count'] == 0:
            return  # No launch if no players connected

        for button in self.game_buttons:
            if button['rect'].collidepoint(pos):
                self.launch_game(button['gamemode'], button['label'])

    def launch_game(self, gamemode, label):
        print(f"[HOST] Launching game mode: {label}")
        selector = SquareSelectorUi(gamemode)
        selector.run()

    def draw(self):
        screen = self.get_screen()
        screen.fill((30, 30, 30))
        screen.blit(self.title_surface, self.title_rect)

        for button in self.game_buttons:
            pygame.draw.rect(screen, button['color'], button['rect'], border_radius=12)
            pygame.draw.rect(screen, (255, 255, 255), button['rect'], 2, border_radius=12)
            label = self.button_font.render(button['label'], True, (255, 255, 255))
            screen.blit(label, label.get_rect(center=button['rect'].center))

        pygame.draw.rect(screen, (70, 70, 70), self.back_button_rect)
        pygame.draw.rect(screen, (255, 255, 255), self.back_button_rect, 2)
        screen.blit(self.button_font.render("Retour", True, (255, 255, 255)), self.back_button_rect.move(20, 5))

        self.draw_server_info(screen)

    def draw_server_info(self, screen):
        status = self.server_manager.get_server_status()
        text = "Server running" if status['running'] else "Erreur: Server down"
        color = (100, 255, 100) if status['running'] else (255, 100, 100)

        s1 = self.info_font.render(text, True, color)
        s2 = self.info_font.render(f"IP: {status['ip']}:{status['port']}", True, (255, 255, 255))
        waiting = "Waiting for player..." if status['clients_count'] == 0 else "Player connected!"
        s3 = self.info_font.render(waiting, True, (255, 255, 0) if status['clients_count'] == 0 else (100, 255, 100))

        for i, surf in enumerate([s1, s2, s3]):
            rect = surf.get_rect(centerx=self.get_width() // 2)
            rect.y = self.server_info_y + i * 25
            screen.blit(surf, rect)


if __name__ == "__main__":
    HostGameUI().run()