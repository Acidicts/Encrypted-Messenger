import socket
import threading
from cryptography.fernet import Fernet
import logging
import base64

# Setup basic logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

clients = {}
client_keys = {}
dict_lock = threading.Lock()

def handle_client(client_socket, addr):
    global clients, client_keys
    try:
        # Receive the encoded key from the client
        encoded_client_key = client_socket.recv(4096)
        if encoded_client_key:
            # Decode the key to its original format
            client_key = base64.urlsafe_b64decode(encoded_client_key)
            with dict_lock:
                client_keys[addr] = client_key
                clients[addr] = client_socket
            logging.info(f"Client {addr} connected and key stored.")
        else:
            logging.error(f"No key received from {addr}.")
            return

        while True:
            encrypted_message = client_socket.recv(4096)
            if encrypted_message:
                logging.debug(f"Message received from {addr}.")
                fernet = Fernet(client_keys[addr])
                decrypted_message = fernet.decrypt(encrypted_message)
                broadcast_message(decrypted_message, addr)
            else:
                logging.error(f"No message received from {addr}.")
    except Exception as e:
        logging.error(f"Error with {addr}: {e}")
    finally:
        cleanup_connection(addr)

def broadcast_message(message, sender_addr):
    global clients, client_keys
    with dict_lock:
        for addr, client_socket in clients.items():
            if addr != sender_addr:
                try:
                    recipient_key = client_keys[addr]
                    fernet = Fernet(recipient_key)
                    encrypted_message = fernet.encrypt(message)
                    client_socket.send(encrypted_message)
                    logging.debug(f"Message broadcasted to {addr}.")
                except Exception as e:
                    logging.error(f"Error broadcasting message to {addr}: {e}")
                    cleanup_connection(addr)

def cleanup_connection(addr):
    with dict_lock:
        if addr in clients:
            clients[addr].close()
            del clients[addr]
            logging.info(f"Connection with {addr} cleaned up.")
        if addr in client_keys:
            del client_keys[addr]

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 5500))
    server.listen(5)
    logging.info("Server listening on 127.0.0.1:5500")

    while True:
        client_socket, addr = server.accept()
        logging.info(f"Accepted connection from: {addr}")
        threading.Thread(target=handle_client, args=(client_socket, addr)).start()

if __name__ == "__main__":
    main()