import pygame
from UI_tools.BaseUi import BaseUI
from Online.Client import start_client
import threading

class JoinGameUI(BaseUI):
    def __init__(self, title="Join Game"):
        super().__init__(title)
        
        
        self.title_font = pygame.font.SysFont(None, 48)
        self.button_font = pygame.font.SysFont(None, 36)
        self.input_font = pygame.font.SysFont(None, 32)
        
        
        self.title_surface = self.title_font.render("Join Game", True, (255, 255, 255))
        self.title_rect = self.title_surface.get_rect(center=(self.get_width() // 2, 100))
        
        # Text input for ip adress
        input_width = 400
        input_height = 50
        self.ip_input_rect = pygame.Rect(
            (self.get_width() - input_width) // 2,
            self.get_height() // 2 - 50,
            input_width,
            input_height
        )
        
        # Status of the UI
        self.ip_text = "127.0.0.1"  # IP by default
        self.ip_active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        
        
        button_width = 200
        button_height = 60
        button_spacing = 40
        
        # Button connect
        self.connect_button_rect = pygame.Rect(
            (self.get_width() - button_width) // 2,
            self.ip_input_rect.bottom + 50,
            button_width,
            button_height
        )
        
        # Button Back
        self.back_button_rect = pygame.Rect(
            20, 20, 120, 40
        )
        
        # Connexion status
        self.connection_status = ""
        self.connection_color = (255, 255, 255)
        
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_click(event.pos)
            
            elif event.type == pygame.KEYDOWN:
                if self.ip_active:
                    self.handle_text_input(event)
    
    def handle_click(self, position):
        # Click on the back button
        if self.back_button_rect.collidepoint(position):
            self.running = False
            return
        
        # Click on the connect button
        if self.connect_button_rect.collidepoint(position):
            self.connect_to_server()
            return
        
        # Click on the IP input area
        if self.ip_input_rect.collidepoint(position):
            self.ip_active = True
        else:
            self.ip_active = False
    
    def handle_text_input(self, event):
        if event.key == pygame.K_BACKSPACE:
            self.ip_text = self.ip_text[:-1]
        elif event.key == pygame.K_RETURN:
            self.connect_to_server()
            self.ip_active = False
        elif event.key == pygame.K_TAB:
            self.ip_active = False
        else:
            # Only ip address characters
            if event.unicode.isprintable() and len(self.ip_text) < 15:
                # Only allow digits and dots (chiffre et point)
                if event.unicode.isdigit() or event.unicode == '.':
                    self.ip_text += event.unicode
    
    def connect_to_server(self):
        if not self.ip_text.strip():
            self.connection_status = "Erreur: Adresse IP vide"
            self.connection_color = (255, 100, 100)
            return
        
        # CHeck if the IP format is valid
        if not self.is_valid_ip(self.ip_text):
            self.connection_status = "Erreur: Format d'IP invalide"
            self.connection_color = (255, 100, 100)
            return
        
        self.connection_status = "Connexion en cours..."
        self.connection_color = (255, 255, 100)
        
        # Launch the connection in a separate thread
        connection_thread = threading.Thread(
            target=self.attempt_connection, 
            args=(self.ip_text.strip(),), 
            daemon=True
        )
        connection_thread.start()
    
    def attempt_connection(self, ip_address):#La fonction est nécessaire si tu veux que la connexion réseau ne bloque pas l'UI
        try:
            # Utiliser la fonction start_client du module Client
            print(f"Tentative de connexion à {ip_address}:5000")
            start_client(ip_address, 5000)
            self.connection_status = f"Connecté à {ip_address}"
            self.connection_color = (100, 255, 100)
        except Exception as e:
            print(f"Erreur de connexion: {e}")
            self.connection_status = f"Échec de connexion: {str(e)}"
            self.connection_color = (255, 100, 100)
    
    def is_valid_ip(self, ip):
        
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            for part in parts:
                if not part.isdigit():
                    return False
                num = int(part)
                if num < 0 or num > 255:
                    return False
            return True
        except:
            return False
    
    def update(self):
        # Gestion of cursor
        self.cursor_timer += self.clock.get_time()
        if self.cursor_timer >= 500:  
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def draw(self):
        screen = self.get_screen()
        screen.fill((30, 30, 30))
        
        
        screen.blit(self.title_surface, self.title_rect)
        
        
        ip_label = self.button_font.render("Adresse IP du serveur:", True, (255, 255, 255))
        ip_label_rect = ip_label.get_rect()
        ip_label_rect.centerx = self.get_width() // 2
        ip_label_rect.bottom = self.ip_input_rect.top - 10
        screen.blit(ip_label, ip_label_rect)
        
        
        input_color = (70, 70, 70) if not self.ip_active else (100, 100, 100)
        border_color = (255, 255, 255) if not self.ip_active else (100, 150, 255)
        
        pygame.draw.rect(screen, input_color, self.ip_input_rect)
        pygame.draw.rect(screen, border_color, self.ip_input_rect, 2)
        
        
        text_surface = self.input_font.render(self.ip_text, True, (255, 255, 255))
        text_x = self.ip_input_rect.x + 10
        text_y = self.ip_input_rect.y + (self.ip_input_rect.height - text_surface.get_height()) // 2
        screen.blit(text_surface, (text_x, text_y))
        
        
        if self.ip_active and self.cursor_visible:
            cursor_x = text_x + text_surface.get_width() + 2
            cursor_y = text_y
            cursor_height = text_surface.get_height()
            pygame.draw.line(screen, (255, 255, 255), 
                           (cursor_x, cursor_y), 
                           (cursor_x, cursor_y + cursor_height), 2)
        
        
        connect_color = (70, 130, 180)
        pygame.draw.rect(screen, connect_color, self.connect_button_rect, border_radius=8)
        pygame.draw.rect(screen, (255, 255, 255), self.connect_button_rect, 2, border_radius=8)
        
        
        # Connect button text
        connect_text = self.button_font.render("Connect", True, (255, 255, 255))
        connect_text_rect = connect_text.get_rect(center=self.connect_button_rect.center)
        screen.blit(connect_text, connect_text_rect)
        
        # Back button
        pygame.draw.rect(screen, (70, 70, 70), self.back_button_rect)
        pygame.draw.rect(screen, (255, 255, 255), self.back_button_rect, 2)
        back_text = self.button_font.render("Retour", True, (255, 255, 255))
        back_text_rect = back_text.get_rect(center=self.back_button_rect.center)
        screen.blit(back_text, back_text_rect)
        
        # Connexion status
        if self.connection_status:
            status_surface = self.button_font.render(self.connection_status, True, self.connection_color)
            status_rect = status_surface.get_rect()
            status_rect.centerx = self.get_width() // 2
            status_rect.top = self.connect_button_rect.bottom + 30
            screen.blit(status_surface, status_rect)
        
        # Instructions
        instruction_text = "Entrez l'adresse IP du serveur et appuyez sur Connect"
        instruction_surface = pygame.font.SysFont(None, 24).render(instruction_text, True, (150, 150, 150))
        instruction_rect = instruction_surface.get_rect()
        instruction_rect.centerx = self.get_width() // 2
        instruction_rect.bottom = self.get_height() - 50
        screen.blit(instruction_surface, instruction_rect)

if __name__ == "__main__":
    app = JoinGameUI()
    app.run()