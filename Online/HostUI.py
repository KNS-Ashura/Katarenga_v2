import pygame
from UI_tools.BaseUi import BaseUI
from Online.NetworkManager import NetworkManager
from Online.GameSession import GameSession
from Editor.Square_selector.SquareSelectorUi import SquareSelectorUi


class HostUI(BaseUI):

    
    def __init__(self, title="Héberger une partie"):
        super().__init__(title)
        
        # Gestionnaire réseau
        self.network = NetworkManager()
        self.session = None
        self.selected_game = None
        
        # État de l'interface
        self.server_started = False
        self.client_connected = False
        self.waiting_for_client = False
        
        # Polices
        self.title_font = pygame.font.SysFont(None, 48)
        self.button_font = pygame.font.SysFont(None, 36)
        self.info_font = pygame.font.SysFont(None, 24)
        
        # Interface
        self.setup_ui()
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Titre
        self.title_surface = self.title_font.render("Héberger une partie", True, (255, 255, 255))
        self.title_rect = self.title_surface.get_rect(center=(self.get_width() // 2, 80))
        
        # Bouton retour
        self.back_button = pygame.Rect(20, 20, 120, 40)
        
        # Boutons de jeux
        self.game_buttons = []
        games = [
            ("Katarenga", (70, 130, 180), 1),
            ("Congress", (60, 179, 113), 2),
            ("Isolation", (220, 20, 60), 3)
        ]
        
        button_width = 250
        button_height = 60
        spacing = 30
        start_y = 200
        center_x = self.get_width() // 2 - button_width // 2
        
        for i, (name, color, game_id) in enumerate(games):
            rect = pygame.Rect(center_x, start_y + i * (button_height + spacing), button_width, button_height)
            self.game_buttons.append({
                'name': name,
                'color': color,
                'game_id': game_id,
                'rect': rect
            })
        
        # Bouton démarrer serveur
        self.start_server_button = pygame.Rect(center_x, start_y + len(games) * (button_height + spacing) + 50, button_width, button_height)
        
        # Zone d'informations
        self.info_y = self.get_height() - 200
    
    def run(self):
        """Boucle principale de l'interface"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
        
        # Nettoyage à la fermeture
        if self.network:
            self.network.disconnect()
    
    def handle_events(self):
        """Gère les événements pygame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_click(event.pos)
    
    def handle_click(self, pos):
        """Gère les clics de souris"""
        # Bouton retour
        if self.back_button.collidepoint(pos):
            self.running = False
            return
        
        # Sélection du jeu
        if not self.server_started:
            for button in self.game_buttons:
                if button['rect'].collidepoint(pos):
                    self.selected_game = button['game_id']
                    print(f"[HOST] Jeu sélectionné: {button['name']}")
                    return
            
            # Démarrage du serveur
            if self.start_server_button.collidepoint(pos) and self.selected_game:
                self.start_server()
        
        # Si un client est connecté, lancer la sélection du plateau
        elif self.client_connected and not self.waiting_for_client:
            self.launch_board_selection()
    
    def start_server(self):
        """Démarre le serveur de jeu"""
        if self.network.start_server():
            self.server_started = True
            self.waiting_for_client = True
            
            # Configure les callbacks réseau
            self.network.set_callbacks(
                message_callback=self.handle_network_message,
                disconnect_callback=self.handle_client_disconnect
            )
            
            print(f"[HOST] Serveur démarré - IP: {self.network.get_local_ip()}")
        else:
            print("[ERROR] Impossible de démarrer le serveur")
    
    def handle_network_message(self, message):
        """Traite les messages réseau"""
        print(f"[HOST] Message reçu: {message}")
        
        # Premier message = client connecté
        if not self.client_connected:
            self.client_connected = True
            self.waiting_for_client = False
            print("[HOST] Client connecté!")
    
    def handle_client_disconnect(self):
        """Traite la déconnexion du client"""
        self.client_connected = False
        self.waiting_for_client = True
        print("[HOST] Client déconnecté")
    
    def launch_board_selection(self):
        """Lance la sélection du plateau et la partie"""
        print(f"[HOST] Lancement de la sélection du plateau pour le jeu {self.selected_game}")
        
        # Crée la session de jeu
        self.session = GameSession(self.selected_game, self.network)
        
        # Lance l'interface de sélection du plateau
        # Note: il faudra modifier SquareSelectorUi pour intégrer le réseau
        selector = SquareSelectorUi(self.selected_game)
        selector.run()
        
        # Après la sélection, on pourrait démarrer la partie réseau
        # TODO: intégrer la logique de jeu réseau
    
    def update(self):
        """Met à jour l'état de l'interface"""
        pass
    
    def draw(self):
        """Dessine l'interface"""
        screen = self.get_screen()
        screen.fill((30, 30, 30))
        
        # Titre
        screen.blit(self.title_surface, self.title_rect)
        
        # Bouton retour
        pygame.draw.rect(screen, (70, 70, 70), self.back_button)
        pygame.draw.rect(screen, (255, 255, 255), self.back_button, 2)
        back_text = self.button_font.render("Retour", True, (255, 255, 255))
        screen.blit(back_text, back_text.get_rect(center=self.back_button.center))
        
        if not self.server_started:
            # Affichage de la sélection de jeu
            self.draw_game_selection(screen)
        else:
            # Affichage de l'état du serveur
            self.draw_server_status(screen)
    
    def draw_game_selection(self, screen):
        """Dessine la sélection de jeu"""
        # Boutons de jeux
        for button in self.game_buttons:
            color = button['color']
            if self.selected_game == button['game_id']:
                # Surbrillance pour le jeu sélectionné
                pygame.draw.rect(screen, (255, 255, 255), button['rect'], 3)
            
            pygame.draw.rect(screen, color, button['rect'])
            pygame.draw.rect(screen, (255, 255, 255), button['rect'], 2)
            
            text = self.button_font.render(button['name'], True, (255, 255, 255))
            screen.blit(text, text.get_rect(center=button['rect'].center))
        
        # Bouton démarrer serveur
        button_color = (100, 255, 100) if self.selected_game else (100, 100, 100)
        pygame.draw.rect(screen, button_color, self.start_server_button)
        pygame.draw.rect(screen, (255, 255, 255), self.start_server_button, 2)
        
        start_text = self.button_font.render("Démarrer le serveur", True, (255, 255, 255))
        screen.blit(start_text, start_text.get_rect(center=self.start_server_button.center))
        
        # Instructions
        if not self.selected_game:
            instruction = "Sélectionnez un jeu puis démarrez le serveur"
        else:
            instruction = f"Jeu sélectionné: {[b['name'] for b in self.game_buttons if b['game_id'] == self.selected_game][0]}"
        
        inst_surface = self.info_font.render(instruction, True, (200, 200, 200))
        screen.blit(inst_surface, (50, self.info_y))
    
    def draw_server_status(self, screen):
        
        status = self.network.get_status()
        
        # Informations du serveur
        info_texts = [
            f"Serveur actif sur: {status['local_ip']}:5000",
            f"Clients connectés: {status['clients_count']}/1"
        ]
        
        if self.waiting_for_client:
            info_texts.append("En attente d'un joueur...")
            status_color = (255, 255, 100)
        elif self.client_connected:
            info_texts.append("Joueur connecté! Cliquez pour commencer")
            status_color = (100, 255, 100)
        else:
            info_texts.append("Aucun joueur connecté")
            status_color = (255, 100, 100)
        
        # Affichage des informations
        for i, text in enumerate(info_texts):
            color = status_color if i == len(info_texts) - 1 else (255, 255, 255)
            surface = self.info_font.render(text, True, color)
            screen.blit(surface, (50, self.info_y + i * 30))

if __name__ == "__main__":
    app = HostUI()
    app.run()