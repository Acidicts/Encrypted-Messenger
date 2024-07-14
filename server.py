import socket
import threading
from cryptography.fernet import Fernet
import json

client_keys = {}

def generate_key():
    return Fernet.generate_key()

def broadcast_keys(new_client_key, addr, clients):
    """
    Broadcasts the new client's key to all other connected clients except the new client itself.
    """
    for client_addr, client_socket in clients.items():
        if client_addr != addr:  # Exclude the new client
            try:
                # Serialize the new client's key and address
                key_info = json.dumps({str(addr): new_client_key.decode('utf-8')})
                client_socket.send(key_info.encode('utf-8'))
            except Exception as e:
                print(f"Error broadcasting new client key to {client_addr}: {e}")

def handle_client(client_socket, addr, clients):
    clients[addr] = client_socket
    client_key = generate_key()
    client_keys[addr] = client_key
    broadcast_keys(client_key, addr, clients)
    try:
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if message:  # Check if message is not empty
                    broadcast_message(message, addr, clients)  # Broadcast received message
            except ConnectionAbortedError:
                print(f"Connection with {addr} aborted.")
                break
            except Exception as e:
                print(f"Unexpected error with {addr}: {e}")
                break
    finally:
        client_socket.close()
        del clients[addr]
        del client_keys[addr]
        print(f"Connection with {addr} closed.")
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 5500))
    server.listen(5)
    clients = {}
    print("Server listening on 127.0.0.1:5500")
    while True:
        client, addr = server.accept()
        print(f"Accepted connection from: {addr}")
        threading.Thread(target=handle_client, args=(client, addr, clients)).start()

if __name__ == "__main__":
    main()