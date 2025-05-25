import socket
import threading


def connect_to_server(host, port):
    print(f"[CLIENT] Attempting to connect to {host}:{port}")
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(10)
        client_socket.connect((host, port))
        client_socket.settimeout(None)
        print(f"[CLIENT] Successfully connected to {host}:{port}")
        return client_socket
    except Exception as e:
        print(f"[ERROR] Could not connect to server: {e}")
        return None

def receive_messages(client_socket):
    print("[CLIENT] Started receiving messages...")
    while True:
        try:
            data = client_socket.recv(1024)
            if data:
                print(f"[SERVER]: {data.decode()}")
            else:
                print("[CLIENT] Server closed the connection.")
                break
        except Exception as e:
            print(f"[CLIENT] Error receiving message: {e}")
            break

def start_client(host, port):
    client_socket = connect_to_server(host, port)
    if not client_socket:
        print("[CLIENT] Failed to connect. Exiting.")
        return

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,), daemon=True)
    receive_thread.start()

    try:
        while True:
            msg = input("Enter message to send (type 'quit' to exit): ").strip()
            if msg.lower() == "quit":
                break
            if msg:
                try:
                    client_socket.sendall(msg.encode())
                except Exception as e:
                    print(f"[CLIENT] Error sending message: {e}")
                    break
    except KeyboardInterrupt:
        print("\n[CLIENT] Interrupted by user")
    finally:
        print("[CLIENT] Closing connection...")
        client_socket.close()

if __name__ == "__main__":
    ip = input("Enter server IP (default 127.0.0.1): ").strip()
    if not ip:
        ip = "127.0.0.1"
    start_client(ip, 5000)
