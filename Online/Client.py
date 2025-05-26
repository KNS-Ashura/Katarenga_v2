import socket
import threading


class Client:
    
    def connect_to_server(host, port):
        print(f"[CLIENT] Connecting to {host}:{port}")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((host, port))
            sock.settimeout(None)
            print("[CLIENT] Connected successfully!")
            return sock
        except Exception as e:
            print(f"[CLIENT ERROR] {e}")
            return None

    
    def receive_messages(sock):
        print("[CLIENT] Listening for messages...")
        while True:
            try:
                data = sock.recv(1024)
                if data:
                    print("[SERVER]", data.decode())
                else:
                    break
            except Exception as e:
                print(f"[CLIENT] Error receiving: {e}")
                break

    
    def interactive_console_loop(sock):
        try:
            while True:
                msg = input("> ")
                if msg.lower() == 'quit':
                    break
                sock.sendall(msg.encode())
        except KeyboardInterrupt:
            print("\n[CLIENT] Interrupted")
        finally:
            print("[CLIENT] Closing socket...")
            sock.close()

    
    def start_client(host, port):
        sock = Client.connect_to_server(host, port)
        if not sock:
            return
        threading.Thread(target=Client.receive_messages, args=(sock,), daemon=True).start()
        Client.interactive_console_loop(sock)


if __name__ == "__main__":
    ip = input("Enter server IP (default 127.0.0.1): ").strip() or "127.0.0.1"
    Client.start_client(ip, 5000)