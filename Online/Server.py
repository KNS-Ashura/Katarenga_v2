import socket

clients = []  
server = None  


def start_server(host, port):
    global server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(False)
    server.bind((host, port))
    server.listen()
    print(f"[HOST] Server listening on {host}:{port}")


def accept_new_clients(server_socket, clients_list):
    try:
        conn, addr = server_socket.accept()
        conn.setblocking(False)
        clients_list.append(conn)
        print(f"[CONN] {addr} connected")
    except BlockingIOError:
        pass


def receive_from_clients(clients_list):
    messages = []
    disconnected = []

    for client in clients_list:
        try:
            data = client.recv(1024)
            if data:
                messages.append((client, data.decode()))
            else:
                disconnected.append(client)
        except BlockingIOError:
            continue
        except ConnectionResetError:
            disconnected.append(client)

    for client in disconnected:
        remove_disconnected_clients(client, clients_list)

    return messages


def broadcast_to_clients(clients_list, message, sender=None):
    for client in clients_list:
        if client != sender:
            try:
                client.sendall(message.encode())
            except:
                remove_disconnected_clients(client, clients_list)


def process_message(client, message):
    # Manage all of messages
    print(f"[MSG] From {client.getpeername()}: {message}")
    broadcast_to_clients(clients, message, sender=client)


def remove_disconnected_clients(client, clients_list):
    addr = client.getpeername()
    print(f"[DISC] {addr} disconnected")
    clients_list.remove(client)
    client.close()


#boucle principale a appeler dans le main
if __name__ == "__main__":
    HOST = '192.168.146.1'
    PORT = 5000
    start_server(HOST, PORT)

    while True:
        accept_new_clients(server, clients)
        messages = receive_from_clients(clients)

        for client, message in messages:
            process_message(client, message)
