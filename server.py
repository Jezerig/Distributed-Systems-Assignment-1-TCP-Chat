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
server.listen(50)
print("Server started...\nRunning...")
clients = []
usernames = []
channels = ["channel1", "channel2", "channel3"]

def client_thread(client_socket, client_address):
    welcome_message_data = json.dumps({'username' : SERVER_NAME, 'msg' : "Welcome to the server! Please select a username."})
    client_socket.send(welcome_message_data.encode())

    while(True):
        client_username = client_socket.recv(BUFFER).decode('utf-8')
        if client_username not in usernames:
            client_socket.send("0".encode('utf-8'))
            username_response = json.dumps({'username' : SERVER_NAME, 'msg' : "Username set as " + client_username})
            client_socket.send(username_response.encode())
            usernames.append(client_username)
            break
        else:
            client_socket.send("1".encode('utf-8'))
            username_response = json.dumps({'username' : SERVER_NAME, 'msg' : "Username already exists. Please try another one..."})
            client_socket.send(username_response.encode())

    while(True):
        try:
            message_data = client_socket.recv(BUFFER)
           
            # jos eka merkki on / niin siitä tulee komento
            # /join channelname
            # /msg username viesti
            # /exit
            if message_data:
                message_data_decoded = json.loads(message_data.decode())
                if(message_data_decoded['msg'][0] == '/'):
                    #if((message_data_decoded['msg'].strip(' ')[0:5] == '/join' and (len(message_data_decoded['msg'].strip(' ')) == 2)):
                    
                    if((message_data_decoded['msg'].rstrip('\n').split(' ')[0].strip()[0:6] == '/exit') and (len(message_data_decoded['msg'].split(' ')) == 1)):
                        print("User {0} ({1}:{2}) disconnected.".format(client_username, client_address[0], client_address[1]))
                        clients.remove(client_socket)
                        usernames.remove(client_username)
                        
                    #if((message_data_decoded['msg'].strip(' ')[0:4] == '/msg') and (len(message_data_decoded['msg'].strip(' ')) > 2)):

                    
                    

                    
                    
                else:    
                    print("[{0}]: {1}".format(message_data_decoded['username'], message_data_decoded['msg']))
                    for client in clients:
                        if(client != client_socket):
                            try:
                                client.send(message_data)
                            except:
                                if(client_socket in clients):
                                    clients.remove(client_socket)
                                    usernames.remove(client_username)
            else:
                if(client_socket in clients):
                    clients.remove(client_socket)
                    usernames.remove(client_username)
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
