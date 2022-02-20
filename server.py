# server.py
# Distributed Systems Assignment 1
# Jesse Pasanen 0545937
#
# Sources: 
# https://pythonprogramming.net/server-chatroom-sockets-tutorial-python-3/
# https://pythonprogramming.net/client-chatroom-sockets-tutorial-python-3/
# https://www.geeksforgeeks.org/simple-chat-room-using-python/
# https://stackoverflow.com/questions/45774300/using-multi-threading-in-python-to-create-a-basic-chatroom
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
# nested list of connected clients [[client_socket, username]]
clients =  []
# list of available channels with a list of clients that are connected to those channels
channels = [{'name': "channel1", 'clients' : []}, { 'name': "channel2", 'clients' : []}]
# creating a string of the names of the channels to display for the user
available_channels = ""
for channel in channels:
    available_channels += "\n'" + channel['name'] + "'"

def remove_client(client_socket, client_channel, client_address):
# if the client disconnects abruptly the server will remove the client from the clients list
    print("({0}:{1}) Connection lost.".format(client_address[0], client_address[1]))
    for client in clients:
        if(client[0] == client_socket):
            clients.remove(client)
    # if client was in a channel
    if(len(client_channel) != 0):
        for channel in channels:
            if(channel['name'] == client_channel):
                temp_channel_clients = channel['clients']
                temp_channel_clients.remove(client_socket)
                channel['clients'] = temp_channel_clients
    return

def client_thread(client_socket, client_address):

    # welcome message after a succesful creation of a thread and connection to the server
    try:
        welcome_message_data = json.dumps({'username' : SERVER_NAME, 'msg' : "Welcome to the server! Please select a username."})
        client_socket.send(welcome_message_data.encode())
    except:
        remove_client(client_socket, client_channel, client_address)
        return
    # variable for the current channel the client is in (empty)
    client_channel = ""

    # while-loop to check if the given username is available for the client
    while(True):
        try:
            username_exists = False
            # receives username from client
            client_username = client_socket.recv(BUFFER).decode('utf-8')

            # checks all usernames from currently connected clients
            for client in clients:
                if(client[1] == client_username):
                    # sends variable to client to confirm if the username is available or not
                    client_socket.send("1".encode('utf-8'))
                    client_socket.send(json.dumps({'username' : SERVER_NAME, 'msg' : "Username already exists. Please try another one..."}).encode())
                    username_exists = True
            if(username_exists):
                continue
            # sends variable to client to confirm if the username is available or not
            client_socket.send("0".encode('utf-8'))
            client_socket.send(json.dumps({'username' : SERVER_NAME, 'msg' : "Username set as '" + client_username + "'\n\nAvailable commands:\n'/join [Channel name]'\n'/msg [username] [message]'\n'/exit'\n\nAvailable chat channels: " + available_channels + "\n"}).encode())
            # if username doesn't exist it is added to the nested list containing the clients socket
            for client in clients:
                if(client[0] == client_socket):
                    client[1] = client_username
            break
        except:
            # if the client disconnects abruptly (i.e. keyboardInterrupt) the server will remove the client from the clients list
            for client in clients:
                if(client[0] == client_socket):
                    clients.remove(client)
            print("({0}:{1}) Connection lost.".format(client_address[0], client_address[1]))
            return

    #while-loop for receiving messages
    while(True):
        # if the client isn't connected to a channel
        if(len(client_channel) == 0):
            try:
                client_socket.send(json.dumps({'username' : SERVER_NAME, 'msg' : "You're currently not in a chatroom. Use '/join [Channel name]' to join."}).encode())
            except:
                remove_client(client_socket, client_channel, client_address)
                return
        try:
            # incoming message data
            message_data = client_socket.recv(BUFFER)
            if message_data:
                # decoding received data
                message_data_decoded = json.loads(message_data.decode())
                # checks if the sent message is a command (starts with '/')
                if(message_data_decoded['msg'][0] == '/'):
                    # check if the command is '/join' with the correct amount of arguments
                    if((message_data_decoded['msg'].rstrip('\n').split(' ')[0].strip()[0:5] == '/join') and (len(message_data_decoded['msg'].split(' ')) == 2)):
                        # boolean for confirming if the channel exists
                        channel_found = False
                        # if the given channel name is different from current channel
                        if(client_channel != message_data_decoded['msg'].split(' ')[1]):
                            # going through existing channels to check if the channel exists
                            for new_channel in channels:
                                if(new_channel['name'] == message_data_decoded['msg'].split(' ')[1]):
                                    channel_found = True
                                    # if the client was already connected to another channel then the socket will be removed from the old channels list of clients
                                    if(len(client_channel) != 0):                                        
                                        for old_channel in channels:
                                            if(old_channel['name'] == client_channel):
                                                temp_channel_clients = old_channel['clients']
                                                temp_channel_clients.remove(client_socket)
                                                old_channel['clients'] = temp_channel_clients
                                                client_socket.send(json.dumps({'username' : SERVER_NAME, 'msg' : "Disconnected from channel '{0}'".format(client_channel)}).encode())
                                                print("User '{0}' ({1}:{2}) disconnected from channel '{3}'".format(client_username, client_address[0], client_address[1], client_channel))     
                                    # clients channel variable is given the new channel name   
                                    client_channel = message_data_decoded['msg'].split(' ')[1]
                                    # new channel list of clients is updated
                                    temp_new_channel_clients = new_channel['clients']
                                    temp_new_channel_clients.append(client_socket)
                                    new_channel['clients'] = temp_new_channel_clients
                                    client_socket.send(json.dumps({'username' : SERVER_NAME, 'msg' : "Connected to channel '{0}'".format(client_channel)}).encode())
                                    print("User '{0}' ({1}:{2}) connected to channel '{3}'".format(client_username, client_address[0], client_address[1], client_channel))
                            if not (channel_found):
                                client_socket.send(json.dumps({'username' : SERVER_NAME, 'msg' : "Channel not found."}).encode())
                        else:
                            client_socket.send(json.dumps({'username' : SERVER_NAME, 'msg' : "You're already connected to channel '{0}'".format(client_channel)}).encode())

                    # checks if the given command is '/exit'
                    elif((message_data_decoded['msg'].rstrip('\n').split(' ')[0].strip()[0:6] == '/exit') and (len(message_data_decoded['msg'].split(' ')) == 1)):
                        print("User {0} ({1}:{2}) disconnected.".format(client_username, client_address[0], client_address[1]))
                        remove_client(client_socket, client_channel, client_address)
                        return

                    # checks if the command is '/msg' with the right amount of arguments
                    elif((message_data_decoded['msg'].rstrip('\n').split(' ')[0].strip()[0:4] == '/msg') and (len(message_data_decoded['msg'].split(' ')) > 2)):
                        user_found = 0
                        target_username = message_data_decoded['msg'].split(' ')[1]
                        try:
                            if (target_username == client_username):
                                client_socket.send(json.dumps({'username' : SERVER_NAME, 'msg' : "You can't sent a private message to yourself."}).encode())
                                continue
                            # goes through the clients to find the right username and the socket connected to the username
                            for client in clients:
                                if(client[1] == target_username):
                                    private_message = str(message_data_decoded['msg'])[len(target_username) + 6:]
                                    print("User '{0}' sent a private message to user '{1}'".format(client_username, target_username))
                                    try:
                                        # send the message to the socket connected to the username
                                        client[0].send(json.dumps({'username' : client_username+"(Private)", 'msg' : private_message}).encode())
                                    except:
                                        client_socket.send(json.dumps({'username' : SERVER_NAME, 'msg' : "Unable to sent message to user '{0}'".format(target_username)}).encode())
                                    user_found = 1
                            if not(user_found):
                                client_socket.send(json.dumps({'username' : SERVER_NAME, 'msg' : "Username '{0}' not found.".format(target_username)}).encode())
                        except:
                            remove_client(client_socket, client_channel, client_address)
                            return
                    continue

                # if the user is in a channel
                if(len(client_channel) != 0):   
                    # message sent by client
                    print("[{0}][{1}]: {2}".format(client_channel, message_data_decoded['username'], message_data_decoded['msg']))
                    # goes throught all the channels
                    for channel in channels:
                        #finds the channel the user is in
                        if(channel['name'] == client_channel):
                            temp_channel_clients = channel['clients']
                            # goes throught the clients connected to the channel
                            for client in temp_channel_clients:
                                # send a message to all the clients that are connected to the channel
                                if(client != client_socket):
                                    try:
                                        client.send(message_data)
                                    except:
                                        remove_client(client_socket, client_channel, client_address)
                                        return
                else:
                    client_socket.send(json.dumps({'username' : SERVER_NAME, 'msg' : "Couldn't send message."}).encode())
            else:
                remove_client(client_socket, client_channel, client_address)
                return
        except:
            remove_client(client_socket, client_channel, client_address)
            return

def main():
    while(True):
        client_socket, client_address = server.accept()
        # client is added to the clients list without and username
        clients.append([client_socket, ''])
        print("New user connected from {0}:{1}.".format(client_address[0], client_address[1]))
        # creating new thread for each connected client
        threading.Thread(target = client_thread, args=(client_socket, client_address)).start()

if __name__ == "__main__":
    main()
