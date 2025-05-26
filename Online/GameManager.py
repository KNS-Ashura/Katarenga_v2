import json
import uuid
from Online.game_logic import NetworkGameSession

class GameManager:
    def __init__(self, server_manager):
        self.server_manager = server_manager
        self.sessions = {}  # {session_id: NetworkGameSession}
        self.client_to_session = {}  # {client_socket: session_id}
        self.waiting_hosts = {}  # {client_socket: game_type}
        
    def handle_message(self, client_socket, message):
        #Manage all messages from clients
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'CREATE_GAME':
                self.handle_create_game(client_socket, data)
            elif message_type == 'JOIN_GAME':
                self.handle_join_game(client_socket, data)
            elif message_type == 'BOARD_READY':
                self.handle_board_ready(client_socket, data)
            elif message_type == 'MOVE':
                self.handle_move(client_socket, data)
            else:
                print(f"Type of message unknow: {message_type}")
                
        except json.JSONDecodeError:
            print(f"Invalid message: {message}")
        except Exception as e:
            print(f"Error treatement message: {e}")
    
    def handle_create_game(self, host_socket, data):
        #manage the creation of a new game session
        game_type = data.get('game_mode')
        session_id = str(uuid.uuid4())
        
        # Create a new game session
        session = NetworkGameSession(session_id, game_type, self.server_manager)
        session.add_player(host_socket, is_host=True)
        
        self.sessions[session_id] = session
        self.client_to_session[host_socket] = session_id
        self.waiting_hosts[host_socket] = game_type
        
        # Confirm creation to the host
        response = {
            'type': 'GAME_CREATED',
            'session_id': session_id,
            'you_are': 'host'
        }
        self.server_manager.send_to_client(host_socket, json.dumps(response))
        
        print(f"Game create - Session: {session_id}, Type: {game_type}")
    
    def handle_join_game(self, client_socket, data):
        #manage a player joining an existing game session
        available_session = self.find_available_session()

        if available_session:
            session_id, session = available_session

            if len(session.players) >= 2:
                response = {
                    'type': 'SESSION_FULL',
                    'message': 'Thsis session is already full.'
                }
                self.server_manager.send_to_client(client_socket, json.dumps(response))
                return

            session.add_player(client_socket, is_host=False)
            self.client_to_session[client_socket] = session_id

            # Confirm to the client
            response = {
                'type': 'GAME_JOINED',
                'session_id': session_id,
                'game_type': session.game_type,
                'you_are': 'client'
            }
            self.server_manager.send_to_client(client_socket, json.dumps(response))

            # Notify host about the new player
            host_socket = session.get_host_socket()
            if host_socket:
                host_notification = {
                    'type': 'PLAYER_JOINED',
                    'message': 'A new player has joined the session.',
                }
                self.server_manager.send_to_client(host_socket, json.dumps(host_notification))

            print(f"Player join a session: {session_id}")
        else:
            response = {
                'type': 'NO_GAME_AVAILABLE',
                'message': 'No game available to join.'
            }
            self.server_manager.send_to_client(client_socket, json.dumps(response))

    
    def handle_board_ready(self, client_socket, data):
        #manage sending the board data to the session
        session_id = self.client_to_session.get(client_socket)
        if session_id and session_id in self.sessions:
            session = self.sessions[session_id]
            session.set_board(data['board'])
    
    def handle_move(self, client_socket, data):
        #manage the player's move in the game session
        session_id = self.client_to_session.get(client_socket)
        if session_id and session_id in self.sessions:
            session = self.sessions[session_id]
            session.handle_move(client_socket, data)
    
    def find_available_session(self):
        
        #search for a session that needs a player
        for session_id, session in self.sessions.items():
            if session.needs_player():
                return session_id, session
        return None
    
    def remove_player(self, client_socket):
        #deconnect a player from the session
        if client_socket in self.client_to_session:
            session_id = self.client_to_session[client_socket]
            if session_id in self.sessions:
                session = self.sessions[session_id]
                session.remove_player(client_socket)
                
                