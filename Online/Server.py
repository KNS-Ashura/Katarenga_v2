import socket
import time
import threading

# Variables globales pour la gestion du serveur
clients = []
server = None
server_thread = None
server_running = False
server_ip = None

def start_server(host, port):
    global server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setblocking(False)

    try:
        server.bind((host, port))
        server.listen(5)
        print(f"[HOST] Server listening on {host}:{port}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to start server: {e}")
        return False



def accept_new_clients(server_socket, clients_list):
    if len(clients_list) >= 1:
        return  # Refuse new connections if a client is already connected
    try:
        conn, addr = server_socket.accept()
        conn.setblocking(False)
        clients_list.append(conn)
        print(f"{addr} connected - Total clients: {len(clients_list)}")
        welcome_msg = f"Welcome! You are client #{len(clients_list)}"
        conn.sendall(welcome_msg.encode())
    except BlockingIOError:
        pass
    except Exception as e:
        print(f"[ERROR] Error accepting client: {e}")


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to an external address to determine the local IP
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'  # by default
    finally:
        s.close()
    return ip

def receive_from_clients(clients_list):
    messages = []
    disconnected = []

    for client in clients_list:
        try:
            data = client.recv(1024)
            if data:
                message = data.decode()
                messages.append((client, message))
                print(f"[MSG] Received: {message}")
            else:
                disconnected.append(client)
        except BlockingIOError:
            continue
        except ConnectionResetError:
            print(f"[DISC] Client {client.getpeername()} disconnected (connection reset)")
            disconnected.append(client)
        except Exception as e:
            print(f"[ERROR] Error receiving from client: {e}")
            disconnected.append(client)

    for client in disconnected:
        remove_disconnected_clients(client, clients_list)

    return messages

def broadcast_to_clients(clients_list, message, sender=None):
    disconnected = []
    for client in clients_list:
        if client != sender:
            try:
                client.sendall(message.encode())
            except Exception as e:
                print(f"[ERROR] Error broadcasting to client: {e}")
                disconnected.append(client)
    for client in disconnected:
        remove_disconnected_clients(client, clients_list)


def remove_disconnected_clients(client, clients_list):
    #try:
    #    addr = client.getpeername()
    #    print(f"[DISC] {addr} disconnected")
    #except:
    #    print(f"[DISC] A client disconnected")
    #if client in clients_list:
    #    clients_list.remove(client)
    #try:
    #    client.close()
    #except:
    pass

def process_message(client, message):
    #try:
    #    addr = client.getpeername()
    #    print(f"[MSG] From {addr}: {message}")
#
    #    # Ici tu peux traiter le message, mettre à jour l'état de jeu, etc.
    #    broadcast_message = f"Client {addr}: {message}"
    #    broadcast_to_clients(clients, broadcast_message, sender=client)
    #except Exception as e:
    #    print(f"[ERROR] Error processing message: {e}")
    pass

def cleanup_server():
    global server, clients, server_running
    print("[HOST] Cleaning up...")
    server_running = False
    
    for client in clients:
        try:
            client.close()
        except:
            pass
    clients.clear()
    
    if server:
        try:
            server.close()
        except:
            pass
        server = None
    print("[HOST] Cleanup complete")

def launch_server_session(host='0.0.0.0', port=5000):
    global server, clients, server_running

    print(f"[HOST] Starting server on {host}:{port}")

    if not start_server(host, port):
        return False

    server_running = True
    print("[HOST] Server started successfully!")
    print("[HOST] Waiting for clients...")

    try:
        while server_running:
            accept_new_clients(server, clients)
            messages = receive_from_clients(clients)

            for client, message in messages:
                process_message(client, message)

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n[HOST] Server shutdown requested")
    except Exception as e:
        print(f"[ERROR] Server error: {e}")
    finally:
        cleanup_server()

    return True

#Explication pr vous les beau gosses :


#La méthode start_server_ui vérifie si le serveur est déjà en marche, 
# récupère l’IP locale, crée un thread pour lancer le serveur (avec launch_server_session), 
# puis met à jour les états internes et globaux (server_running, server_ip).
class ServerManager:
    def __init__(self):
        self.is_running = False
        self.thread = None
        self.ip = None

    def start_server_ui(self):
        global server_running, server_thread, server_ip
        
        if self.is_running:
            print("[SERVER] Server is already running")
            return False

        try:
            self.ip = get_local_ip()
            print(f"[SERVER] Starting server on {self.ip}:5000")
            
            self.thread = threading.Thread(
                target=launch_server_session,
                args=('0.0.0.0', 5000),
                daemon=True
            )
            self.thread.start()
            
            self.is_running = True
            server_running = True
            server_ip = self.ip
            
            print(f"[SERVER] Server started successfully on {self.ip}:5000")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to start server: {e}")
            self.is_running = False
            return False

    def stop_server_ui(self):
        global server_running
        
        if not self.is_running:
            print("[SERVER] Server is not running")
            return True

        try:
            print("[SERVER] Stopping server...")
            cleanup_server()
            
            self.is_running = False
            self.thread = None
            self.ip = None
            server_running = False
            
            print("[SERVER] Server stopped successfully")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to stop server: {e}")
            return False

    def get_server_status(self):
        
        return {
            'running': self.is_running,
            'ip': self.ip,
            'port': 5000 if self.is_running else None,
            'clients_count': len(clients) if self.is_running else 0
        }

    def is_server_running(self):
        
        return self.is_running

    def get_server_ip(self):
        
        return self.ip if self.is_running else None

if __name__ == "__main__":
    launch_server_session()