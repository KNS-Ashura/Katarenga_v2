import socket
import time

clients = []
server = None

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
        # Se connecter à une IP publique pour obtenir l'IP locale utilisée
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'  # par default
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
    try:
        addr = client.getpeername()
        print(f"[DISC] {addr} disconnected")
    except:
        print(f"[DISC] A client disconnected")
    if client in clients_list:
        clients_list.remove(client)
    try:
        client.close()
    except:
        pass

def process_message(client, message):
    try:
        addr = client.getpeername()
        print(f"[MSG] From {addr}: {message}")

        # Ici tu peux traiter le message, mettre à jour l'état de jeu, etc.
        broadcast_message = f"Client {addr}: {message}"
        broadcast_to_clients(clients, broadcast_message, sender=client)
    except Exception as e:
        print(f"[ERROR] Error processing message: {e}")

def cleanup_server():
    global server, clients
    print("[HOST] Cleaning up...")
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
    global server, clients
    clients = []

    print(f"[HOST] Starting server on {host}:{port}")

    if not start_server(host, port):
        return

    print("[HOST] Server started successfully!")
    print("[HOST] Waiting for clients...")

    try:
        while True:
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

if __name__ == "__main__":
    launch_server_session()
