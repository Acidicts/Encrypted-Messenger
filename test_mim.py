import socket
import threading
import time

def get_messages(client):
    while True:
        try:
            response = client.recv(4096)
            if response:
                print("\nServer response received:", response)
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            client.connect(("127.0.0.1", 5500))
            print("Connected to server.")
            break  # Exit loop if connection is successful
        except ConnectionRefusedError:
            print("Connection refused, trying again in 5 seconds...")
            time.sleep(5)

    thread = threading.Thread(target=get_messages, args=(client,))
    thread.start()

    try:
        while True:
            message = input("Enter message: ")
            if message == "exit":
                client.send(message.encode())
                break
            client.send(message.encode())
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client.close()
        print("Connection closed.")
        thread.join()

if __name__ == "__main__":
    main()