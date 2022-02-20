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
# nested list [[client_socket, username]]
clients =  []
channels = [{'name': "channel1", 'clients' : []}, { 'name': "channel2", 'clients' : []}]
available_channels = ""
for channel in channels:
    available_channels += "\n'" + channel['name'] + "'"



def client_thread(client_socket, client_address):
    try:
        welcome_message_data = json.dumps({'username' : SERVER_NAME, 'msg' : "Welcome to the server! Please select a username."})
    except:
        print("({0}:{1}) Connection lost.".format(client_address[0], client_address[1]))
        for client in clients:
            if(client[0] == client_socket):
                clients.remove(client)
        if(len(client_channel) != 0):
            for channel in channels:
                if(channel['name'] == client_channel):
                    temp_channel_clients = channel['clients']
                    temp_channel_clients.remove(client_socket)
                    channel['clients'] = temp_channel_clients
        return
    client_socket.send(welcome_message_data.encode())
    client_channel = ""
    while(True):
        try:
            username_exists = False
            client_username = client_socket.recv(BUFFER).decode('utf-8')

            for client in clients:
                if(client[1] == client_username):
                    client_socket.send("1".encode('utf-8'))
                    client_socket.send(json.dumps({'username' : SERVER_NAME, 'msg' : "Username already exists. Please try another one..."}).encode())
                    username_exists = True
            if(username_exists):
                continue
            client_socket.send("0".encode('utf-8'))
            client_socket.send(json.dumps({'username' : SERVER_NAME, 'msg' : "Username set as '" + client_username + "'\n\nAvailable commands:\n'/join [Channel name]'\n'/msg [username] [message]'\n'/exit'\n\nAvailable chat channels: " + available_channels + "\n"}).encode())
            for client in clients:
                if(client[0] == client_socket):
                    client[1] = client_username
            break
        except:
            for client in clients:
                if(client[0] == client_socket):
                    clients.remove(client)
            print("({0}:{1}) Connection lost.".format(client_address[0], client_address[1]))
            return

    while(True):
        if(len(client_channel) == 0):
            try:
                client_socket.send(json.dumps({'username' : SERVER_NAME, 'msg' : "You're currently not in a chatroom. Use '/join [Channel name]' to join."}).encode())
            except:
                print("({0}:{1}) Connection lost.".format(client_address[0], client_address[1]))
                for client in clients:
                    if(client[0] == client_socket):
                        clients.remove(client)
                if(len(client_channel) != 0):
                    for channel in channels:
                        if(channel['name'] == client_channel):
                            temp_channel_clients = channel['clients']
                            temp_channel_clients.remove(client_socket)
                            channel['clients'] = temp_channel_clients
                return
        try:
            message_data = client_socket.recv(BUFFER)
            if message_data:
                message_data_decoded = json.loads(message_data.decode())
                if(message_data_decoded['msg'][0] == '/'):
                    if((message_data_decoded['msg'].rstrip('\n').split(' ')[0].strip()[0:5] == '/join') and (len(message_data_decoded['msg'].split(' ')) == 2)):
                        channel_found = False
                        if(client_channel != message_data_decoded['msg'].split(' ')[1]):
                            for new_channel in channels:
                                if(new_channel['name'] == message_data_decoded['msg'].split(' ')[1]):
                                    channel_found = True
                                    if(len(client_channel) != 0):                                        
                                        for old_channel in channels:
                                            if(old_channel['name'] == client_channel):
                                                temp_channel_clients = old_channel['clients']
                                                print("Old channel clients before: ", temp_channel_clients)
                                                temp_channel_clients.remove(client_socket)
                                                old_channel['clients'] = temp_channel_clients
                                                client_socket.send(json.dumps({'username' : SERVER_NAME, 'msg' : "Disconnected from channel '{0}'".format(client_channel)}).encode())
                                                print("User '{0}' ({1}:{2}) disconnected from channel '{3}'".format(client_username, client_address[0], client_address[1], client_channel))
                                                print("Old channel clients after: ", temp_channel_clients)           
                                    client_channel = message_data_decoded['msg'].split(' ')[1]
                                    temp_new_channel_clients = new_channel['clients']
                                    print("New channel clients before: ", temp_new_channel_clients)
                                    temp_new_channel_clients.append(client_socket)
                                    print("New channel clients after: ", temp_new_channel_clients)
                                    new_channel['clients'] = temp_new_channel_clients
                                    client_socket.send(json.dumps({'username' : SERVER_NAME, 'msg' : "Connected to channel '{0}'".format(client_channel)}).encode())
                                    print("User '{0}' ({1}:{2}) connected to channel '{3}'".format(client_username, client_address[0], client_address[1], client_channel))
                            if not (channel_found):
                                client_socket.send(json.dumps({'username' : SERVER_NAME, 'msg' : "Channel not found."}).encode())
                        else:
                            client_socket.send(json.dumps({'username' : SERVER_NAME, 'msg' : "You're already connected to channel '{0}'".format(client_channel)}).encode())


                    elif((message_data_decoded['msg'].rstrip('\n').split(' ')[0].strip()[0:6] == '/exit') and (len(message_data_decoded['msg'].split(' ')) == 1)):
                        print("User {0} ({1}:{2}) disconnected.".format(client_username, client_address[0], client_address[1]))
                        for client in clients:
                            if(client[0] == client_socket):
                                clients.remove(client)
                        if(len(client_channel) != 0):
                            for channel in channels:
                                if(channel['name'] == client_channel):
                                    temp_channel_clients = channel['clients']
                                    temp_channel_clients.remove(client_socket)
                                    channel['clients'] = temp_channel_clients
                        break

                    elif((message_data_decoded['msg'].rstrip('\n').split(' ')[0].strip()[0:4] == '/msg') and (len(message_data_decoded['msg'].split(' ')) > 2)):
                        user_found = 0
                        target_username = message_data_decoded['msg'].split(' ')[1]
                        try:
                            if (target_username == client_username):
                                client_socket.send(json.dumps({'username' : SERVER_NAME, 'msg' : "You can't sent a private message to yourself."}).encode())
                                continue
                            for client in clients:
                                if(client[1] == target_username):
                                    private_message = str(message_data_decoded['msg'])[len(target_username) + 6:]
                                    print(private_message)
                                    print("User '{0}' sent a private message to user '{1}'".format(client_username, target_username))
                                    try:
                                        client[0].send(json.dumps({'username' : client_username+"(Private)", 'msg' : private_message}).encode())
                                    except:
                                        client_socket.send(json.dumps({'username' : SERVER_NAME, 'msg' : "Unable to sent message to user '{0}'".format(target_username)}).encode())
                                    user_found = 1
                            if not(user_found):
                                client_socket.send(json.dumps({'username' : SERVER_NAME, 'msg' : "Username '{0}' not found.".format(target_username)}).encode())
                        except:
                            for client in clients:
                                if(client[0] == client_socket):
                                    clients.remove(client)
                            if(len(client_channel) != 0):
                                for channel in channels:
                                    if(channel['name'] == client_channel):
                                        temp_channel_clients = channel['clients']
                                        temp_channel_clients.remove(client_socket)
                                        channel['clients'] = temp_channel_clients
                            return
                    continue
                              
                if(len(client_channel) != 0):    
                    print("[{0}][{1}]: {2}".format(client_channel, message_data_decoded['username'], message_data_decoded['msg']))
                    for channel in channels:
                        if(channel['name'] == client_channel):
                            temp_channel_clients = channel['clients']
                            for client in temp_channel_clients:
                                if(client != client_socket):
                                    try:
                                        client.send(message_data)
                                    except:
                                        for client in clients:
                                            if(client[0] == client_socket):
                                                clients.remove(client)
                                                temp_channel_clients.remove(client_socket)
                                                channel['clients'] = temp_channel_clients
                            
                else:
                    client_socket.send(json.dumps({'username' : SERVER_NAME, 'msg' : "Couldn't send message."}).encode())
            else:
                for client in clients:
                    if(client[0] == client_socket):
                        clients.remove(client)
        except:
            continue

def main():
    while(True):
        client_socket, client_address = server.accept()
        clients.append([client_socket, ''])
        print("New user connected from {0}:{1}.".format(client_address[0], client_address[1]))
        threading.Thread(target = client_thread, args=(client_socket, client_address)).start()

if __name__ == "__main__":
    main()
