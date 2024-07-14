import socket
import threading
import json

# Step 1: Define other_clients_keys at the global level
other_clients_keys = {}

def listen_for_messages(client_socket):
    global other_clients_keys  # Step 3: Use the global keyword
    while True:
        message = client_socket.recv(4096).decode('utf-8')
        if message:
            try:
                keys = json.loads(message)
                other_clients_keys.update(keys)
                print("Updated keys:", other_clients_keys)
            except json.JSONDecodeError:
                print("Server response received:", message)

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", 5500))
    print("Connected to server.")
    # Step 2: Initialize other_clients_keys as an empty dictionary is already done at the global level
    threading.Thread(target=listen_for_messages, args=(client,)).start()
    client.send("request_keys".encode('utf-8'))
    # Client can now send messages or perform other actions

if __name__ == "__main__":
    main()