#Objectif :
# gérer la connexion au serveur, 
# envoyer les actions du joueur, 
# recevoir les mises à jour du serveur, 
# gérer les messages d'erreur et de succès

import socket
import time
import threading


def connect_to_server(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setblocking(False)  #socket non bloquant
    try:
        client_socket.connect((host, port))
    except BlockingIOError:
        pass  
    return client_socket



def start_client(ip, port):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, port))
        print(f"[CLIENT] Connecté au serveur {ip}:{port}")

        # Démarre un thread pour recevoir les messages en arrière-plan
        threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

        # Envoie un message de test
        message = input("Entrez un message à envoyer : ")
        while message.lower() != "quit":
            client_socket.sendall(message.encode())
            message = input("Entrez un message à envoyer : ")

        client_socket.close()
        print("[CLIENT] Déconnexion")

    except ConnectionRefusedError:
        print("[ERREUR] Connexion refusée. Vérifie l'IP et que le serveur tourne.")
    except Exception as e:
        print(f"[ERREUR] Une erreur est survenue : {e}")
        
        
def receive_messages(client_socket):
    while True:
        try:
            data = client_socket.recv(1024)
            if data:
                print("[SERVEUR] :", data.decode())
            else:
                print("[CLIENT] Serveur déconnecté.")
                break
        except:
            break
        
        
        
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
        


def main(ip_adress):
    
    port = 5000
    client_socket = connect_to_server(ip_adress, port)
    game_state = {}

    while True:
        # Lecture serveur
        message = receive_updates(client_socket)
        if message:
            handle_server_message(message, game_state)


        time.sleep(0.05)  # Petite pause pour éviter de surcharger

if __name__ == "__main__":
    main()
