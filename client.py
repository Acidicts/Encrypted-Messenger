import socket
import threading
from cryptography.fernet import Fernet
import base64

def listen_for_messages(client_socket, client_key):
    fernet = Fernet(client_key)
    while True:
        try:
            message = client_socket.recv(4096)
            if message:
                decrypted_message = fernet.decrypt(message).decode('utf-8')
                print(f"\nNew message: {decrypted_message}")
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

def send_messages(client_socket, client_key):
    fernet = Fernet(client_key)
    while True:
        message = input("Enter your message: ")
        if message == "/exit":
            break
        encrypted_message = fernet.encrypt(message.encode('utf-8'))
        try:
            client_socket.send(encrypted_message)
        except OSError as e:
            print(f"Socket error: {e}")
            break

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(("127.0.0.1", 5500))
        client_key = Fernet.generate_key()
        # Encode the key before sending
        encoded_key = base64.urlsafe_b64encode(client_key)
        client_socket.send(encoded_key)
        threading.Thread(target=listen_for_messages, args=(client_socket, client_key)).start()
        send_messages(client_socket, client_key)
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()