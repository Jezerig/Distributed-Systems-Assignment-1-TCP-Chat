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
channels = [{'name': "channel1", 'clients' : []}, { 'name': "channel2", 'clients' : []}]



def client_thread(client_socket, client_address):
    welcome_message_data = json.dumps({'username' : SERVER_NAME, 'msg' : "Welcome to the server! Please select a username."})
    client_socket.send(welcome_message_data.encode())
    client_channel = ""
    while(True):
        client_username = client_socket.recv(BUFFER).decode('utf-8')
        if client_username not in usernames:
            client_socket.send("0".encode('utf-8'))
            client_socket.send(json.dumps({'username' : SERVER_NAME, 'msg' : "Username set as " + client_username}).encode())
            usernames.append(client_username)
            break
        else:
            client_socket.send("1".encode('utf-8'))
            client_socket.send(json.dumps({'username' : SERVER_NAME, 'msg' : "Username already exists. Please try another one..."}).encode())

    while(True):
        if(len(client_channel) == 0):
            client_socket.send(json.dumps({'username' : SERVER_NAME, 'msg' : "Please select a channel you want to chat in. '/join [Channel name]'"}).encode())
        try:
            message_data = client_socket.recv(BUFFER)
           
            # jos eka merkki on / niin siitä tulee komento
            # /msg username viesti

            if message_data:
                message_data_decoded = json.loads(message_data.decode())
                if(message_data_decoded['msg'][0] == '/'):
                    
                    if((message_data_decoded['msg'].rstrip('\n').split(' ')[0].strip()[0:5] == '/join') and (len(message_data_decoded['msg'].split(' ')) == 2)):
                        for channel in channels:
                            if(channel['name'] == message_data_decoded['msg'].split(' ')[1]):
                                client_channel = message_data_decoded['msg'].split(' ')[1]
                                temp_channel_clients = channel['clients']
                                temp_channel_clients.append(client_socket)
                                channel['clients'] = temp_channel_clients

                    elif((message_data_decoded['msg'].rstrip('\n').split(' ')[0].strip()[0:6] == '/exit') and (len(message_data_decoded['msg'].split(' ')) == 1)):
                        print("User {0} ({1}:{2}) disconnected.".format(client_username, client_address[0], client_address[1]))
                        clients.remove(client_socket)
                        usernames.remove(client_username)
                        if(len(client_channel) != 0):
                            for channel in channels:
                                if(channel['name'] == client_channel):
                                    temp_channel_clients = channel['clients']
                                    temp_channel_clients.remove(client_socket)
                                    channel['clients'] = temp_channel_clients

                        
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
