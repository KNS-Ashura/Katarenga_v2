import pygame
from UI_tools.BaseUi import BaseUI

class JoinGameUI(BaseUI):
    def __init__(self, title="Join a Game"):
        super().__init__(title)
        
        # Configuration des polices
        self.title_font = pygame.font.SysFont(None, 48)
        self.button_font = pygame.font.SysFont(None, 36)
        self.input_font = pygame.font.SysFont(None, 32)
        
        # Titre
        self.title_surface = self.title_font.render("Join a Game", True, (255, 255, 255))
        self.title_rect = self.title_surface.get_rect(center=(self.get_width() // 2, 100))
        
        # Bouton retour
        self.back_button_rect = pygame.Rect(20, 20, 120, 40)
        
        # Zone de texte pour l'IP
        input_width = 400
        input_height = 50
        self.text_input_rect = pygame.Rect(
            (self.get_width() - input_width) // 2,
            self.get_height() // 2 - 50,
            input_width,
            input_height
        )
        
        # Variables pour la zone de texte
        self.text_input = ""
        self.text_active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        
        # Bouton de connexion
        connect_width = 200
        connect_height = 50
        self.connect_button_rect = pygame.Rect(
            (self.get_width() - connect_width) // 2,
            self.text_input_rect.bottom + 30,
            connect_width,
            connect_height
        )
        
        # Label pour la zone de texte
        self.label_surface = self.input_font.render("Server IP Address:", True, (255, 255, 255))
        self.label_rect = self.label_surface.get_rect()
        self.label_rect.centerx = self.text_input_rect.centerx
        self.label_rect.bottom = self.text_input_rect.top - 10

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
                if self.text_active:
                    if event.key == pygame.K_BACKSPACE:
                        self.text_input = self.text_input[:-1]
                    elif event.key == pygame.K_RETURN:
                        self.connect_to_server()
                    elif event.key == pygame.K_TAB:
                        self.text_active = False
                    else:
                        # Filtrer pour n'accepter que les caractères valides pour une IP
                        if event.unicode.isprintable() and len(self.text_input) < 50:
                            self.text_input += event.unicode

    def handle_click(self, position):
        x, y = position
        
        # Bouton retour
        if self.back_button_rect.collidepoint(x, y):
            self.running = False
            return
        
        # Zone de texte
        if self.text_input_rect.collidepoint(x, y):
            self.text_active = True
        else:
            self.text_active = False
        
        # Bouton de connexion
        if self.connect_button_rect.collidepoint(x, y):
            self.connect_to_server()

    def connect_to_server(self):
        if self.text_input.strip():
            print(f"Tentative de connexion au serveur : {self.text_input}")
            # Ici vous pouvez ajouter la logique de connexion au serveur
            # Par exemple, appeler une fonction du module Online/Server.py
            self.running = False
        else:
            print("Veuillez entrer une adresse IP valide")

    def update(self):
        # Animation du curseur
        self.cursor_timer += 1
        if self.cursor_timer >= 30:  # Change la visibilité toutes les 30 frames (0.5 seconde à 60 FPS)
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def draw(self):
        screen = self.get_screen()
        screen.fill((30, 30, 30))
        
        # Dessiner le titre
        screen.blit(self.title_surface, self.title_rect)
        
        # Dessiner le bouton retour
        pygame.draw.rect(screen, (70, 70, 70), self.back_button_rect)
        pygame.draw.rect(screen, (255, 255, 255), self.back_button_rect, 2)
        back_text = self.button_font.render("Retour", True, (255, 255, 255))
        screen.blit(back_text, back_text.get_rect(center=self.back_button_rect.center))
        
        # Dessiner le label
        screen.blit(self.label_surface, self.label_rect)
        
        # Dessiner la zone de texte
        border_color = (0, 150, 255) if self.text_active else (255, 255, 255)
        pygame.draw.rect(screen, (50, 50, 50), self.text_input_rect)
        pygame.draw.rect(screen, border_color, self.text_input_rect, 3)
        
        # Dessiner le texte saisi
        text_surface = self.input_font.render(self.text_input, True, (255, 255, 255))
        text_x = self.text_input_rect.x + 10
        text_y = self.text_input_rect.y + (self.text_input_rect.height - text_surface.get_height()) // 2
        screen.blit(text_surface, (text_x, text_y))
        
        # Dessiner le curseur si la zone de texte est active
        if self.text_active and self.cursor_visible:
            cursor_x = text_x + text_surface.get_width() + 2
            cursor_y = text_y
            cursor_height = text_surface.get_height()
            pygame.draw.line(screen, (255, 255, 255), 
                           (cursor_x, cursor_y), 
                           (cursor_x, cursor_y + cursor_height), 2)
        
        # Dessiner le bouton de connexion
        button_color = (0, 150, 0) if self.text_input.strip() else (100, 100, 100)
        pygame.draw.rect(screen, button_color, self.connect_button_rect)
        pygame.draw.rect(screen, (255, 255, 255), self.connect_button_rect, 2)
        connect_text = self.button_font.render("Connect", True, (255, 255, 255))
        screen.blit(connect_text, connect_text.get_rect(center=self.connect_button_rect.center))
        
        # Instructions
        instruction_text = "Entrez l'adresse IP du serveur et cliquez sur Connect"
        instruction_surface = pygame.font.SysFont(None, 24).render(instruction_text, True, (180, 180, 180))
        instruction_rect = instruction_surface.get_rect(center=(self.get_width() // 2, self.connect_button_rect.bottom + 50))
        screen.blit(instruction_surface, instruction_rect)

if __name__ == "__main__":
    app = JoinGameUI()
    app.run()