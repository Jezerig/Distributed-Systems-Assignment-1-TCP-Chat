# server.py
# Distributed Systems Assignment 1
# Jesse Pasanen 0545937

import socket
import select
import threading

BUFFER = 2048
IP_ADDRESS = "127.0.0.1"
PORT = 1234

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((IP_ADDRESS, PORT))
server.listen(10)
print("Server started...")
clients = []

def client_thread(client_socket, client_address):
    client_socket.send("[Server]: Welcome to the server!".encode('utf-8'))
    while(True):
        try:
            message = client_socket.recv(BUFFER).decode('utf-8')
            if message:
                print("[{0}]: {1}".format(client_address[0], message))
                for client in clients:
                    if(client != client_socket):
                        try:
                            client.send(message.encode('utf-8'))
                        except:
                            if(client_socket in clients):
                                clients.remove(client_socket)
            else:
                if(client_socket in clients):
                    clients.remove(client_socket)
        except:
            continue

def main():
    while(True):
        client_socket, client_address = server.accept()
        clients.append(client_socket)
        print("[Server]: New user connected from {0}:{1}.".format(client_address[0], client_address[1]))
        threading.Thread(target = client_thread, args=(client_socket, client_address)).start()

if __name__ == "__main__":
    main()
