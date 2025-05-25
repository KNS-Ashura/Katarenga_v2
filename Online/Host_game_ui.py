import pygame
from UI_tools.BaseUi import BaseUI
from Online.Server import ServerManager
from Editor.Square_selector.SquareSelectorUi import SquareSelectorUi

class HostGameUI(BaseUI):
    def __init__(self, title="Host Game - Select Mode"):
        super().__init__(title)
       
        self.server_manager = ServerManager()
        
        # Lauch the server autiomatically
        self.server_started = self.server_manager.start_server_ui()
        
        self.title_font = pygame.font.SysFont(None, 48)
        self.button_font = pygame.font.SysFont(None, 36)
        self.info_font = pygame.font.SysFont(None, 24)
        
        
        self.title_surface = self.title_font.render("Host Game - Select Mode", True, (255, 255, 255))
        self.title_rect = self.title_surface.get_rect(center=(self.get_width() // 2, 100))
        
        button_width = 300
        button_height = 80
        spacing = 40
        num_buttons = 3
        
        total_height = num_buttons * button_height + (num_buttons - 1) * spacing
        start_y = (self.get_height() - total_height) // 2
        x_center = (self.get_width() - button_width) // 2
        
        # Game modes buttons
        game_modes = [
            ("Katarenga", (70, 130, 180), 1),
            ("Congress", (60, 179, 113), 2), 
            ("Isolation", (220, 20, 60), 3)
        ]
        
        self.game_buttons = []
        for i, (label, color, gamemode) in enumerate(game_modes):
            rect = pygame.Rect(
                x_center, 
                start_y + i * (button_height + spacing), 
                button_width, 
                button_height
            )
            self.game_buttons.append({
                "label": label, 
                "rect": rect, 
                "color": color,
                "gamemode": gamemode
            })
        self.game_buttons = []
        for i, mode in enumerate(game_modes):
            label, color, gamemode = mode
            rect = pygame.Rect(
            x_center,
            start_y + i * (button_height + spacing),
            button_width,
            button_height
            )
            self.game_buttons.append(dict(label=label, rect=rect, color=color, gamemode=gamemode))
        # Bouton retour
        self.back_button_rect = pygame.Rect(20, 20, 120, 40)
        
        # Zone d'information serveur
        self.server_info_y = self.get_height() - 150
        
    def run(self):
        if not self.server_started:
            print("Erreur: Impossible to start the server.")
            return
            
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
            
        # Close the server when exiting
        if self.server_manager.is_server_running():
            self.server_manager.stop_server_ui()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_click(event.pos)
    
    def handle_click(self, position):
        # Click on the back button
        if self.back_button_rect.collidepoint(position):
            self.running = False
            return
        
        # Check if at least one client is connected
        server_status = self.server_manager.get_server_status()
        if server_status['clients_count'] == 0:
            return
        
        # Clivk on game mode buttons
        for button in self.game_buttons:
            if button["rect"].collidepoint(position):
                self.start_game_mode(button["gamemode"], button["label"])
                return
    
    def start_game_mode(self, gamemode, mode_name):
        
        print(f"Launching game {mode_name} you are the host...")
        
        # Create the board selection interface for the host
        # The server remains active in the background
        
        try:
            square_selector = SquareSelectorUi(gamemode)
            square_selector.run()
        except Exception as e:
            print(f"Error when launching game: {e}")
    
    def update(self):
        pass
    
    def draw(self):
        screen = self.get_screen()
        screen.fill((30, 30, 30))
        
        
        screen.blit(self.title_surface, self.title_rect)
        
        
        instruction_text = "Select a game mode to host:"
        instruction_surface = self.button_font.render(instruction_text, True, (200, 200, 200))
        instruction_rect = instruction_surface.get_rect(center=(self.get_width() // 2, 150))
        screen.blit(instruction_surface, instruction_rect)
        
        # Check if clients are connected for button state
        server_status = self.server_manager.get_server_status()
        clients_connected = server_status['clients_count'] > 0
        
        # Buttons for game modes
        for button in self.game_buttons:
            if clients_connected:
                button_color = button["color"]
                text_color = (255, 255, 255)
            else:
                button_color = (80, 80, 80)
                text_color = (150, 150, 150)
            
            pygame.draw.rect(screen, button_color, button["rect"], border_radius=12)
            pygame.draw.rect(screen, (255, 255, 255), button["rect"], 2, border_radius=12)
            
           
            text_surface = self.button_font.render(button["label"], True, text_color)
            text_rect = text_surface.get_rect(center=button["rect"].center)
            screen.blit(text_surface, text_rect)
        
        # Back button
        pygame.draw.rect(screen, (70, 70, 70), self.back_button_rect)
        pygame.draw.rect(screen, (255, 255, 255), self.back_button_rect, 2)
        back_text = self.button_font.render("Retour", True, (255, 255, 255))
        back_text_rect = back_text.get_rect(center=self.back_button_rect.center)
        screen.blit(back_text, back_text_rect)
        
        
        self.draw_server_info(screen)
    
    def draw_server_info(self, screen):
        
        server_status = self.server_manager.get_server_status()
        
        if server_status['running']:
            status_text = "Server running"
            status_surface = self.info_font.render(status_text, True, (100, 255, 100))
            status_rect = status_surface.get_rect()
            status_rect.centerx = self.get_width() // 2
            status_rect.y = self.server_info_y
            screen.blit(status_surface, status_rect)
            
            # IP of server
            ip_text = f"IP: {server_status['ip']}:{server_status['port']}"
            ip_surface = self.info_font.render(ip_text, True, (255, 255, 255))
            ip_rect = ip_surface.get_rect()
            ip_rect.centerx = self.get_width() // 2
            ip_rect.y = status_rect.bottom + 5
            screen.blit(ip_surface, ip_rect)
            
            if server_status['clients_count'] == 1:
                clients_text = "1 client connected"
            else:
                pass
            
            
            # Message for waiting players
            if server_status['clients_count'] == 0:
                waiting_text = "Waiting for players to join..."
                waiting_surface = self.info_font.render(waiting_text, True, (255, 255, 100))
            else:
                waiting_text = "A player is waiting to join..."
                waiting_surface = self.info_font.render(waiting_text, True, (100, 255, 100))
            
            waiting_rect = waiting_surface.get_rect()
            waiting_rect.centerx = self.get_width() // 2
            screen.blit(waiting_surface, waiting_rect)
            
        else:
            # Erreur serveur
            error_text = "Erreur: Server down"
            error_surface = self.info_font.render(error_text, True, (255, 100, 100))
            error_rect = error_surface.get_rect()
            error_rect.centerx = self.get_width() // 2
            error_rect.y = self.server_info_y
            screen.blit(error_surface, error_rect)

if __name__ == "__main__":
    app = HostGameUI()
    app.run()