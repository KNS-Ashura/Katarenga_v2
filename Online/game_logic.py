import json
from Game_ui.Katarenga import Katarenga
from Game_ui.Congress import Congress
from Game_ui.Isolation import Isolation

class NetworkGameSession:
    def __init__(self, session_id, game_type, server_manager):
        self.session_id = session_id
        self.game_type = game_type  # 1=Katarenga, 2=Congress, 3=Isolation
        self.server_manager = server_manager
        self.players = {}  # {socket: player_number}
        self.host_socket = None
        self.board = None
        self.game_instance = None
        self.current_player = 1
        self.state = "waiting_for_players" 

    def add_player(self, client_socket, is_host=False):
        if is_host:
            self.host_socket = client_socket
            self.players[client_socket] = 1
        else:
            if self.host_socket is None or len(self.players) >= 2:
                return  
            self.players[client_socket] = 2
            if self.state == "waiting_for_players":
                self.state = "waiting_for_board"

    def get_host_socket(self):
        return self.host_socket

    def needs_player(self):
        return len(self.players) < 2

    def set_board(self, board_data):
        self.board = board_data
        self.state = "playing"

        # Create the game instance based on the game type
        if self.game_type == 1:
            self.game_instance = Katarenga(self.board)
        elif self.game_type == 2:
            self.game_instance = Congress(self.board)
        elif self.game_type == 3:
            self.game_instance = Isolation(self.board)

        self.broadcast_state()

    def handle_move(self, client_socket, move_data):
        if self.state != "playing":
            return

        player_number = self.players.get(client_socket)
        if player_number != self.current_player:
            return  # It's not this player's turn

        from_pos = move_data.get("from")
        to_pos = move_data.get("to")

        if self.game_instance.play_turn(from_pos, to_pos):
            # If move is valid, update the game state
            self.current_player = 2 if self.current_player == 1 else 1

            if self.game_instance.is_game_over():
                self.state = "finished"

            self.broadcast_state()
        else:
            # Bad move, notify the player
            try:
                self.server_manager.send_to_client(client_socket, json.dumps({
                    "type": "INVALID_MOVE",
                    "message": "Invalid move."
                }))
            except:
                pass

    def broadcast_state(self):
        state_data = {
            "type": "GAME_STATE",
            "board": self.game_instance.get_board_state() if self.game_instance else self.board,
            "current_player": self.current_player,
            "status": self.state
        }
        message = json.dumps(state_data)
        for client in self.players.keys():
            try:
                self.server_manager.send_to_client(client, message)
            except:
                pass

    def remove_player(self, client_socket):
        if client_socket in self.players:
            del self.players[client_socket]

        if not self.players:
            self.state = "finished"

        
        self.broadcast_state()
