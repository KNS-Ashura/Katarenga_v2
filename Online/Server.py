
import socket
import threading
import time

clients = []
server = None
server_running = False
server_ip = None

class ServerManager:
    def __init__(self):
        self.is_running = False
        self.thread = None
        self.ip = None

    def start_server_ui(self):
        global server_running, server_ip

        if self.is_running:
            print("[SERVER] Server is already running")
            return False

        try:
            self.ip = self.get_local_ip()
            print(f"[SERVER] Starting server on {self.ip}:5000")

            self.thread = threading.Thread(target=self.launch_server_session, daemon=True)
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
            self.cleanup_server()

            self.is_running = False
            self.thread = None
            self.ip = None
            server_running = False

            print("[SERVER] Server stopped successfully")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to stop server: {e}")
            return False

    def send_to_client(self, client_socket, message):
        try:
            client_socket.sendall(message.encode())
        except Exception as e:
            print(f"[SERVER] Error sending to client: {e}")

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

    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

    def launch_server_session(self, host='0.0.0.0', port=5000):
        global server, clients, server_running

        print(f"[HOST] Launching server session on {host}:{port}")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.setblocking(False)

        try:
            server.bind((host, port))
            server.listen(5)
            server_running = True
            print("[HOST] Server is running and listening...")
        except Exception as e:
            print(f"[ERROR] Could not start server: {e}")
            return

        try:
            while server_running:
                self.accept_new_clients(server, clients)
                messages = self.receive_from_clients(clients)
                for client, message in messages:
                    self.process_message(client, message)
                time.sleep(0.01)
        except Exception as e:
            print(f"[ERROR] Server crashed: {e}")
        finally:
            self.cleanup_server()

    def accept_new_clients(self, server_socket, clients_list):
        if len(clients_list) >= 1:
            return
        try:
            conn, addr = server_socket.accept()
            conn.setblocking(False)
            clients_list.append(conn)
            print(f"{addr} connected - Total clients: {len(clients_list)}")
            conn.sendall(b"Welcome! You are client #1")
        except BlockingIOError:
            pass
        except Exception as e:
            print(f"[ERROR] Accepting client failed: {e}")

    def receive_from_clients(self, clients_list):
        messages = []
        disconnected = []
        for client in clients_list:
            try:
                data = client.recv(1024)
                if data:
                    messages.append((client, data.decode()))
                else:
                    disconnected.append(client)
            except (BlockingIOError, ConnectionResetError):
                continue
            except Exception as e:
                print(f"[ERROR] Receiving failed: {e}")
                disconnected.append(client)
        for client in disconnected:
            self.remove_disconnected_client(client, clients_list)
        return messages

    def remove_disconnected_client(self, client, clients_list):
        try:
            clients_list.remove(client)
            client.close()
        except:
            pass

    def process_message(self, client, message):
        print(f"[MSG] From client: {message}")
        self.broadcast_to_clients(clients, f"Echo: {message}", sender=client)

    def broadcast_to_clients(self, clients_list, message, sender=None):
        for client in clients_list:
            if client != sender:
                try:
                    client.sendall(message.encode())
                except:
                    self.remove_disconnected_client(client, clients_list)

    def cleanup_server(self):
        global server, clients, server_running
        print("[HOST] Cleaning up server...")
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