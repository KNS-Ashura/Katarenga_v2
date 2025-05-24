from Online.Server import launch_server_session, get_local_ip
from Online.Client import start_client
from Online.Join_game import JoinGameUI


class MultiplayerHandler:
    def __init__(self):
        pass

    def host_game(self):
        #Start a new game session/server
        print("[INFO] Starting server...")
        
        local_ip = get_local_ip()
        print(f"[INFO] Server will start on: {local_ip}:5000")
        print(f"[INFO] Other players should connect to: {local_ip}")
        
        launch_server_session()

    def join_game(self):
        #Join an existing game session/server
        print("Je cherche une partie")
        
        join_game_ui = JoinGameUI()
        join_game_ui.run()
        
        ip_address = join_game_ui.get_input_ip()
        if ip_address:
            print(f" Connecting to server at {ip_address}:5000")
            start_client(ip_address, 5000)
        else:
            print("No IP entered, returning to main menu.")