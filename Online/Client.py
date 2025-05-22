#Objectif :
# gérer la connexion au serveur, 
# envoyer les actions du joueur, 
# recevoir les mises à jour du serveur, 
# gérer les messages d'erreur et de succès

import socket

def connect_to_server(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    print(f"[CONN] Connected to server at {host}:{port}")
    return client_socket

def send_action(client_socket, action):
    try:
        client_socket.sendall(action.encode())
        print(f"[SEND] Action sent: {action}")
    except Exception as e:
        print(f"[ERROR] Failed to send action: {e}")
        
        
def receive_updates(client_socket):
    try:
        data = client_socket.recv(1024)
        if data:
            print(f"[RECV] Update received: {data.decode()}")
        else:
            print("[ERROR] Server closed the connection")
    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")

def handle_server_message(message, game_state):
    # Process the message from the server
    print(f"[MSG] Server: {message}")
    # Update game state based on the message
    # This is a placeholder; actual implementation will depend on the game logic
    if message.startswith("UPDATE"):
        game_state.update(message)
    elif message.startswith("ERROR"):
        print(f"[ERROR] {message}")
    else:
        print(f"[INFO] {message}")
        
def player_input():
    # Get player input for actions
    action = input("Enter your action: ")
    return action


def main_loop():
    pass