# Online/JoinUI.py
import pygame
import threading
from UI_tools.BaseUi import BaseUI
from Online.NetworkManager import NetworkManager
from Online.GameSession import GameSession

class JoinUI(BaseUI):
    """Interface pour rejoindre une partie en réseau"""
    
    def __init__(self, title="Rejoindre une partie"):
        super().__init__(title)
        
        # Gestionnaire réseau
        self.network = NetworkManager()
        self.session = None
        
        # État de l'interface
        self.connected = False
        self.connecting = False
        self.board_received = False
        self.game_started = False
        
        # Saisie IP
        self.ip_text = "127.0.0.1"
        self.ip_active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        
        # Messages d'état
        self.status_message = ""
        self.status_color = (255, 255, 255)
        
        # Polices
        self.title_font = pygame.font.SysFont(None, 48)
        self.button_font = pygame.font.SysFont(None, 36)
        self.input_font = pygame.font.SysFont(None, 32)
        self.info_font = pygame.font.SysFont(None, 24)
        
        # Interface
        self.setup_ui()
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Titre
        self.title_surface = self.title_font.render("Rejoindre une partie", True, (255, 255, 255))
        self.title_rect = self.title_surface.get_rect(center=(self.get_width() // 2, 80))
        
        # Bouton retour
        self.back_button = pygame.Rect(20, 20, 120, 40)
        
        # Zone de saisie IP
        center_x = self.get_width() // 2
        center_y = self.get_height() // 2
        
        self.ip_input_rect = pygame.Rect(center_x - 200, center_y - 100, 400, 50)
        self.connect_button = pygame.Rect(center_x - 100, center_y - 30, 200, 50)
        
        # Zone d'informations
        self.info_y = center_y + 50
    
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
            
            elif event.type == pygame.KEYDOWN and self.ip_active:
                self.handle_text_input(event)
    
    def handle_click(self, pos):
        """Gère les clics de souris"""
        # Bouton retour
        if self.back_button.collidepoint(pos):
            self.running = False
            return
        
        # Zone de saisie IP
        self.ip_active = self.ip_input_rect.collidepoint(pos)
        
        # Bouton de connexion
        if self.connect_button.collidepoint(pos) and not self.connecting and not self.connected:
            self.attempt_connection()
    
    def handle_text_input(self, event):
        """Gère la saisie de texte pour l'IP"""
        if event.key == pygame.K_BACKSPACE:
            self.ip_text = self.ip_text[:-1]
        elif event.key == pygame.K_RETURN:
            if not self.connecting and not self.connected:
                self.attempt_connection()
        elif event.unicode.isprintable() and len(self.ip_text) < 15:
            # Autorise seulement les chiffres et les points
            if event.unicode.isdigit() or event.unicode == ".":
                self.ip_text += event.unicode
    
    def attempt_connection(self):
        """Tente de se connecter au serveur"""
        if not self.ip_text.strip():
            self.set_status("Veuillez entrer une adresse IP", (255, 100, 100))
            return
        
        self.connecting = True
        self.set_status("Connexion en cours...", (255, 255, 100))
        
        # Lance la connexion dans un thread séparé
        threading.Thread(target=self.connect_to_server, daemon=True).start()
    
    def connect_to_server(self):
        """Se connecte au serveur (appelé dans un thread)"""
        if self.network.connect_to_server(self.ip_text.strip()):
            # Connexion réussie
            self.connected = True
            self.connecting = False
            self.set_status("Connecté! En attente du plateau...", (100, 255, 100))
            
            # Configure les callbacks pour recevoir les données de jeu
            self.network.set_callbacks(
                message_callback=self.handle_network_message,
                disconnect_callback=self.handle_server_disconnect
            )
            
            # Envoie un message de confirmation
            self.network.send_message("CLIENT_READY")
            
        else:
            # Connexion échouée
            self.connecting = False
            self.set_status("Impossible de se connecter", (255, 100, 100))
    
    def handle_network_message(self, message):
        """Traite les messages reçus du serveur"""
        print(f"[CLIENT] Message reçu: {message}")
        
        try:
            import json
            data = json.loads(message)
            
            if data.get('type') == 'BOARD_DATA':
                # Réception du plateau de jeu
                self.board_received = True
                self.session = GameSession(data['game_type'], self.network)
                self.session.set_board(data['board'])
                self.set_status("Plateau reçu! En attente du début de partie...", (100, 255, 100))
            
            elif data.get('type') == 'GAME_START':
                # La partie commence
                self.game_started = True
                self.set_status("Partie démarrée!", (100, 255, 100))
                # TODO: Lancer l'interface de jeu
        
        except:
            # Message simple (pas JSON)
            if "READY" in message.upper():
                self.set_status("Serveur prêt", (100, 255, 100))
    
    def handle_server_disconnect(self):
        """Traite la déconnexion du serveur"""
        self.connected = False
        self.connecting = False
        self.board_received = False
        self.game_started = False
        self.set_status("Serveur déconnecté", (255, 100, 100))
    
    def set_status(self, message, color):
        """Met à jour le message de statut"""
        self.status_message = message
        self.status_color = color
        print(f"[STATUS] {message}")
    
    def update(self):
        """Met à jour l'état de l'interface"""
        # Animation du curseur de saisie
        self.cursor_timer += self.clock.get_time()
        if self.cursor_timer >= 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
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
        
        if not self.connected and not self.game_started:
            # Interface de connexion
            self.draw_connection_interface(screen)
        else:
            # Interface d'attente/jeu
            self.draw_game_interface(screen)
    
    def draw_connection_interface(self, screen):
        """Dessine l'interface de connexion"""
        # Label pour la saisie IP
        label = self.button_font.render("Adresse IP du serveur:", True, (255, 255, 255))
        label_rect = label.get_rect(centerx=self.get_width() // 2, y=self.ip_input_rect.y - 40)
        screen.blit(label, label_rect)
        
        # Zone de saisie IP
        input_color = (100, 100, 100) if self.ip_active else (70, 70, 70)
        pygame.draw.rect(screen, input_color, self.ip_input_rect)
        pygame.draw.rect(screen, (255, 255, 255), self.ip_input_rect, 2)
        
        # Texte saisi
        text_surface = self.input_font.render(self.ip_text, True, (255, 255, 255))
        text_x = self.ip_input_rect.x + 10
        text_y = self.ip_input_rect.y + (self.ip_input_rect.height - text_surface.get_height()) // 2
        screen.blit(text_surface, (text_x, text_y))
        
        # Curseur clignotant
        if self.ip_active and self.cursor_visible:
            cursor_x = text_x + text_surface.get_width() + 2
            cursor_y1 = text_y + 2
            cursor_y2 = text_y + text_surface.get_height() - 2
            pygame.draw.line(screen, (255, 255, 255), (cursor_x, cursor_y1), (cursor_x, cursor_y2), 2)
        
        # Bouton de connexion
        button_color = (70, 130, 180)
        if self.connecting:
            button_color = (100, 100, 100)
        elif not self.ip_text.strip():
            button_color = (50, 50, 50)
        
        pygame.draw.rect(screen, button_color, self.connect_button)
        pygame.draw.rect(screen, (255, 255, 255), self.connect_button, 2)
        
        button_text = "Connexion..." if self.connecting else "Se connecter"
        connect_surface = self.button_font.render(button_text, True, (255, 255, 255))
        screen.blit(connect_surface, connect_surface.get_rect(center=self.connect_button.center))
        
        # Message de statut
        if self.status_message:
            status_surface = self.info_font.render(self.status_message, True, self.status_color)
            status_rect = status_surface.get_rect(centerx=self.get_width() // 2, y=self.info_y)
            screen.blit(status_surface, status_rect)
        
        # Instructions
        instructions = [
            "Entrez l'adresse IP du serveur hébergé par l'autre joueur",
            "L'adresse IP est affichée sur l'écran de l'hôte"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_surface = self.info_font.render(instruction, True, (200, 200, 200))
            inst_rect = inst_surface.get_rect(centerx=self.get_width() // 2, y=self.info_y + 50 + i * 25)
            screen.blit(inst_surface, inst_rect)
    
    def draw_game_interface(self, screen):
        """Dessine l'interface de jeu/attente"""
        # Informations de connexion
        info_texts = [
            f"Connecté à: {self.ip_text}",
            f"Statut: {self.status_message}"
        ]
        
        if self.session:
            status = self.session.get_status()
            info_texts.extend([
                f"Type de jeu: {['', 'Katarenga', 'Congress', 'Isolation'][status.get('game_type', 0)]}",
                f"Vous êtes le joueur: {status.get('local_player', 2)}"
            ])
        
        # Affichage des informations
        start_y = self.get_height() // 2 - len(info_texts) * 15
        for i, text in enumerate(info_texts):
            color = self.status_color if i == 1 else (255, 255, 255)
            surface = self.info_font.render(text, True, color)
            screen.blit(surface, (50, start_y + i * 30))
        
        # Instructions selon l'état
        if self.board_received and not self.game_started:
            instruction = "En attente que l'hôte démarre la partie..."
        elif self.game_started:
            instruction = "Partie en cours!"
        else:
            instruction = "En attente des données de jeu..."
        
        inst_surface = self.button_font.render(instruction, True, (255, 255, 100))
        inst_rect = inst_surface.get_rect(centerx=self.get_width() // 2, y=start_y + len(info_texts) * 30 + 50)
        screen.blit(inst_surface, inst_rect)

if __name__ == "__main__":
    app = JoinUI()
    app.run()