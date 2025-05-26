# Online/NetworkManager.py
import socket
import threading
import json
import time

class NetworkManager:
    """Gestionnaire principal pour les connexions réseau"""
    
    def __init__(self):
        self.is_host = False
        self.is_connected = False
        self.socket = None
        self.server_socket = None
        self.clients = []
        self.message_callback = None
        self.disconnect_callback = None
        
    def set_callbacks(self, message_callback=None, disconnect_callback=None):
        """Définit les fonctions à appeler lors d'événements réseau"""
        self.message_callback = message_callback
        self.disconnect_callback = disconnect_callback
    
    # === FONCTIONS SERVEUR (HOST) ===
    def start_server(self, port=5000):
        """Démarre un serveur pour héberger une partie"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', port))
            self.server_socket.listen(1)  # Maximum 1 client pour simplifier
            
            self.is_host = True
            self.is_connected = True
            
            # Démarre un thread pour accepter les connexions
            threading.Thread(target=self._accept_clients, daemon=True).start()
            
            print(f"[SERVER] Serveur démarré sur le port {port}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Impossible de démarrer le serveur: {e}")
            return False
    
    def _accept_clients(self):
        """Accepte les connexions des clients (thread séparé)"""
        while self.is_connected and len(self.clients) < 1:
            try:
                client_socket, client_address = self.server_socket.accept()
                self.clients.append(client_socket)
                print(f"[SERVER] Client connecté: {client_address}")
                
                # Démarre un thread pour écouter ce client
                threading.Thread(target=self._listen_client, args=(client_socket,), daemon=True).start()
                
            except Exception as e:
                if self.is_connected:
                    print(f"[ERROR] Erreur d'acceptation client: {e}")
                break
    
    def _listen_client(self, client_socket):
        """Écoute les messages d'un client (thread séparé)"""
        while self.is_connected:
            try:
                data = client_socket.recv(1024)
                if data:
                    message = data.decode('utf-8')
                    if self.message_callback:
                        self.message_callback(message)
                else:
                    break
                    
            except Exception as e:
                print(f"[ERROR] Erreur de réception: {e}")
                break
        
        # Client déconnecté
        if client_socket in self.clients:
            self.clients.remove(client_socket)
        client_socket.close()
        
        if self.disconnect_callback:
            self.disconnect_callback()
    
    # === FONCTIONS CLIENT ===
    def connect_to_server(self, host_ip, port=5000):
        """Se connecte à un serveur hébergé par un autre joueur"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host_ip, port))
            
            self.is_host = False
            self.is_connected = True
            
            # Démarre un thread pour écouter le serveur
            threading.Thread(target=self._listen_server, daemon=True).start()
            
            print(f"[CLIENT] Connecté au serveur {host_ip}:{port}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Impossible de se connecter: {e}")
            return False
    
    def _listen_server(self):
        """Écoute les messages du serveur (thread séparé)"""
        while self.is_connected:
            try:
                data = self.socket.recv(1024)
                if data:
                    message = data.decode('utf-8')
                    if self.message_callback:
                        self.message_callback(message)
                else:
                    break
                    
            except Exception as e:
                print(f"[ERROR] Erreur de réception: {e}")
                break
        
        # Serveur déconnecté
        self.is_connected = False
        if self.disconnect_callback:
            self.disconnect_callback()
    
    # === FONCTIONS COMMUNES ===
    def send_message(self, message):
        """Envoie un message (fonctionne pour host et client)"""
        if not self.is_connected:
            return False
        
        try:
            if self.is_host:
                # Envoie à tous les clients connectés
                for client in self.clients:
                    client.send(message.encode('utf-8'))
            else:
                # Envoie au serveur
                self.socket.send(message.encode('utf-8'))
            return True
            
        except Exception as e:
            print(f"[ERROR] Erreur d'envoi: {e}")
            return False
    
    def disconnect(self):
        """Ferme toutes les connexions"""
        self.is_connected = False
        
        if self.socket:
            self.socket.close()
            self.socket = None
        
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
        
        for client in self.clients:
            client.close()
        self.clients.clear()
        
        print("[NETWORK] Déconnecté")
    
    def get_local_ip(self):
        """Retourne l'adresse IP locale"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(('8.8.8.8', 80))
                return s.getsockname()[0]
        except:
            return '127.0.0.1'
    
    def get_status(self):
        """Retourne le statut de la connexion"""
        return {
            'connected': self.is_connected,
            'is_host': self.is_host,
            'clients_count': len(self.clients) if self.is_host else 0,
            'local_ip': self.get_local_ip()
        }