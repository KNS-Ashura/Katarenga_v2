# Online/GameSession.py
import json
import copy

class GameSession:
    """Gère une session de jeu en réseau"""
    
    def __init__(self, game_type, network_manager):
        self.game_type = game_type  # 1=Katarenga, 2=Congress, 3=Isolation
        self.network = network_manager
        self.board = None
        self.current_player = 1
        self.is_host = network_manager.is_host
        self.game_started = False
        self.game_finished = False
        
        # Callbacks pour les événements de jeu
        self.on_board_update = None
        self.on_player_change = None
        self.on_game_end = None
        
        # Configure les callbacks réseau
        self.network.set_callbacks(
            message_callback=self._handle_network_message,
            disconnect_callback=self._handle_disconnect
        )
    
    def set_game_callbacks(self, board_update=None, player_change=None, game_end=None):
        """Définit les fonctions à appeler lors d'événements de jeu"""
        self.on_board_update = board_update
        self.on_player_change = player_change
        self.on_game_end = game_end
    
    def set_board(self, board_data):
        """Définit le plateau de jeu et le partage si on est host"""
        self.board = copy.deepcopy(board_data)
        
        if self.is_host:
            # Envoie le plateau à l'autre joueur
            message = {
                'type': 'BOARD_DATA',
                'board': self.board,
                'game_type': self.game_type
            }
            self.network.send_message(json.dumps(message))
    
    def start_game(self):
        """Démarre la partie"""
        if not self.board:
            print("[ERROR] Pas de plateau défini")
            return False
        
        self.game_started = True
        self.current_player = 1  # Le host commence toujours
        
        if self.is_host:
            message = {
                'type': 'GAME_START',
                'current_player': self.current_player
            }
            self.network.send_message(json.dumps(message))
        
        if self.on_player_change:
            self.on_player_change(self.current_player)
        
        print(f"[GAME] Partie démarrée - Type: {self.game_type}")
        return True
    
    def make_move(self, from_pos, to_pos):
        """Effectue un mouvement (coordonnées sous forme de tuples)"""
        if not self.game_started or self.game_finished:
            return False
        
        # Vérifie si c'est le tour du joueur local
        local_player = 1 if self.is_host else 2
        if self.current_player != local_player:
            print("[GAME] Ce n'est pas votre tour")
            return False
        
        # Valide et applique le mouvement (à implémenter selon le jeu)
        if self._validate_move(from_pos, to_pos):
            self._apply_move(from_pos, to_pos)
            
            # Envoie le mouvement à l'autre joueur
            message = {
                'type': 'MOVE',
                'from': from_pos,
                'to': to_pos,
                'player': self.current_player
            }
            self.network.send_message(json.dumps(message))
            
            # Change de joueur
            self._switch_player()
            
            # Vérifie la fin de partie
            winner = self._check_victory()
            if winner:
                self._end_game(winner)
            
            return True
        
        return False
    
    def _handle_network_message(self, message):
        """Traite les messages reçus du réseau"""
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            if msg_type == 'BOARD_DATA':
                self.board = data['board']
                self.game_type = data['game_type']
                if self.on_board_update:
                    self.on_board_update(self.board)
                print("[GAME] Plateau reçu")
            
            elif msg_type == 'GAME_START':
                self.game_started = True
                self.current_player = data['current_player']
                if self.on_player_change:
                    self.on_player_change(self.current_player)
                print("[GAME] Partie démarrée par l'hôte")
            
            elif msg_type == 'MOVE':
                from_pos = tuple(data['from'])
                to_pos = tuple(data['to'])
                player = data['player']
                
                # Applique le mouvement de l'adversaire
                self._apply_move(from_pos, to_pos)
                self._switch_player()
                
                # Vérifie la fin de partie
                winner = self._check_victory()
                if winner:
                    self._end_game(winner)
                
                print(f"[GAME] Mouvement reçu: {from_pos} -> {to_pos}")
            
            elif msg_type == 'GAME_END':
                winner = data['winner']
                self._end_game(winner)
                print(f"[GAME] Partie terminée - Gagnant: {winner}")
            
            elif msg_type == 'CHAT':
                message_text = data['message']
                print(f"[CHAT] {message_text}")
        
        except Exception as e:
            print(f"[ERROR] Erreur de traitement message: {e}")
    
    def _handle_disconnect(self):
        """Traite la déconnexion de l'adversaire"""
        print("[GAME] Adversaire déconnecté")
        if not self.game_finished:
            self._end_game("Déconnexion")
    
    def _validate_move(self, from_pos, to_pos):
        """Valide un mouvement selon les règles du jeu"""
        # À implémenter selon le type de jeu
        # Pour l'instant, on retourne toujours True
        return True
    
    def _apply_move(self, from_pos, to_pos):
        """Applique un mouvement sur le plateau"""
        if not self.board:
            return
        
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Déplace le pion
        piece = self.board[from_row][from_col]
        
        # Nettoie la case d'origine (garde la couleur, enlève le joueur)
        self.board[from_row][from_col] = (piece // 10) * 10
        
        # Place le pion à la nouvelle position
        dest_color = self.board[to_row][to_col] // 10
        self.board[to_row][to_col] = dest_color * 10 + self.current_player
        
        if self.on_board_update:
            self.on_board_update(self.board)
    
    def _switch_player(self):
        """Change de joueur actuel"""
        self.current_player = 2 if self.current_player == 1 else 1
        if self.on_player_change:
            self.on_player_change(self.current_player)
    
    def _check_victory(self):
        """Vérifie s'il y a un gagnant"""
        # À implémenter selon le type de jeu
        # Pour l'instant, on retourne None (pas de gagnant)
        return None
    
    def _end_game(self, winner):
        """Termine la partie"""
        self.game_finished = True
        
        if self.is_host and winner != "Déconnexion":
            # Notifie l'autre joueur de la fin
            message = {
                'type': 'GAME_END',
                'winner': winner
            }
            self.network.send_message(json.dumps(message))
        
        if self.on_game_end:
            self.on_game_end(winner)
    
    def send_chat_message(self, text):
        """Envoie un message de chat"""
        message = {
            'type': 'CHAT',
            'message': f"{'Host' if self.is_host else 'Client'}: {text}"
        }
        self.network.send_message(json.dumps(message))
    
    def get_status(self):
        """Retourne le statut de la session"""
        return {
            'game_type': self.game_type,
            'game_started': self.game_started,
            'game_finished': self.game_finished,
            'current_player': self.current_player,
            'is_host': self.is_host,
            'local_player': 1 if self.is_host else 2
        }