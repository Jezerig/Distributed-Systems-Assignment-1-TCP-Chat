# server.py
# Distributed Systems Assignment 1
# Jesse Pasanen 0545937

import socket
import threading
import json

BUFFER = 2048
IP_ADDRESS = "127.0.0.1"
PORT = 1234
SERVER_NAME = "Server"
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((IP_ADDRESS, PORT))
server.listen(20)
print("Server started...")
clients = []

def client_thread(client_socket, client_address):
    welcome_message = "Welcome to the server!"
    welcome_message_data = json.dumps({'username' : SERVER_NAME, 'ip_address' : IP_ADDRESS, 'port' : PORT, 'msg' : welcome_message})
    client_socket.send(welcome_message_data.encode())
    while(True):
        try:
            message_data = client_socket.recv(BUFFER)
            if message_data:
                message_data_decoded = json.loads(message_data.decode())
                print("[{0}]: {1}".format(message_data_decoded['username'], message_data_decoded['msg']))
                for client in clients:
                    if(client != client_socket):
                        try:
                            client.send(message_data)
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
        print("[{0}]: New user connected from {1}:{2}.".format(SERVER_NAME, client_address[0], client_address[1]))
        threading.Thread(target = client_thread, args=(client_socket, client_address)).start()

if __name__ == "__main__":
    main()
