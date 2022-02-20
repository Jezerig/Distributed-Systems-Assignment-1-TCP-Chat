# client.py
# Distributed Systems Assignment 1
# Jesse Pasanen 0545937
# Sources: 
# https://pythonprogramming.net/server-chatroom-sockets-tutorial-python-3/
# https://pythonprogramming.net/client-chatroom-sockets-tutorial-python-3/
# https://www.geeksforgeeks.org/simple-chat-room-using-python/
# https://stackoverflow.com/questions/45774300/using-multi-threading-in-python-to-create-a-basic-chatroom

import socket
import sys
import threading
import time
import json

# IP_ADDRESS and PORT given as command line arguments
if(len(sys.argv) != 3):
    print("To establish a connection to a server give two arguments.")
    print("client.py [IP ADDRESS] [PORT]")
    sys.exit(1)
IP_ADDRESS = str(sys.argv[1])
try:
    PORT = int(sys.argv[2])
except:
    print("Invalid port")
    print("client.py [IP ADDRESS] [PORT]")
    sys.exit(1)

# recv buffer
BUFFER = 2048

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    server.connect((IP_ADDRESS, PORT))
except:
    print("Unable to connect to server {0}:{1}".format(IP_ADDRESS, PORT))
    sys.exit(1)

# thread for receiving incoming messages
def receive_message_thread():
    while(True):
        try:
            message_data = server.recv(BUFFER)
            message_data_decoded = json.loads(message_data.decode())
            print("[{0}]: {1}".format(message_data_decoded['username'], message_data_decoded['msg']))
        except:
            sys.exit(1)

# thread for sending messages
def send_message_thread(username):
    time.sleep(0.5)
    while(True):
        # reads messages from stdin
        try:
            message = sys.stdin.readline()
            if (message):
                # parsing message to see if it's a command (starting with '/')
                if(message[0] == '/'):
                    # if the command is '/join'
                    if(message.rstrip('\n').split(' ')[0].strip()[0:5] == '/join'):
                        # correct amount of arguments
                        if (len(message.split(' ')) == 2):
                            message_data = json.dumps({'username' : username, 'msg' : message.rstrip('\n')})
                            server.send(message_data.encode())
                        else:
                            print("Usage: '/join [Channel name]'")
                        continue

                    # if the command is '/exit'
                    if(message.rstrip('\n').split(' ')[0].strip()[0:6] == '/exit'):
                        if (len(message.split(' ')) == 1):
                            message_data = json.dumps({'username' : username, 'msg' : message.rstrip('\n')})
                            server.send(message_data.encode())
                            print("Disconnected.")
                            sys.exit(0)
                        else:
                            print("Command '/exit' doesn't take any arguments.")
                        continue
                    # if the command is '/msg'
                    if(message.rstrip('\n').split(' ')[0].strip()[0:4] == '/msg'):
                        if (len(message.split(' ')) > 2):
                            message_data = json.dumps({'username' : username, 'msg' : message.rstrip('\n')})
                            server.send(message_data.encode())
                        else:
                            print("Usage: '/msg [username] [message]'")
                        continue
                    else:
                        print("Invalid command. Available commands:\n'/join [Channel name]'\n'/msg [username] [message]'\n'/exit'\n")
            
                else:
                    # sending message to server
                    # if message is not empty
                    if(message.strip()):
                        message_data = json.dumps({'username' : username, 'msg' : message.rstrip('\n')})
                        server.send(message_data.encode())
                        # printing message to stdout on client side aswell
                        sys.stdout.write("[{0}]: {1}".format(username, message))
                        sys.stdout.flush()
        except:
            sys.exit(1)

def select_username():
    # selecting username for the server
    try:
        message_data = server.recv(BUFFER)
        message_data_decoded = json.loads(message_data.decode())
        print("[{0}]: {1}".format(message_data_decoded['username'], message_data_decoded['msg']))
        while(True):
            username = input("Username: ")
            if(username.strip()):
                server.send(username.encode('utf-8'))
                # server sends a 1 or a 0 the confirm if the username is available
                username_exists = server.recv(BUFFER).decode('utf-8')
                # additional info regarding username availability
                username_msg_data = server.recv(BUFFER)
                username_msg_data_decoded = json.loads(username_msg_data.decode())
                # if the username doesn't exist
                if not (int(username_exists)):
                    sys.stdout.write("[{0}]: {1}\n".format(username_msg_data_decoded['username'], username_msg_data_decoded['msg']))
                    sys.stdout.flush()
                    return username
                else:
                    # username exists
                    sys.stdout.write("[{0}]: {1}\n".format(username_msg_data_decoded['username'], username_msg_data_decoded['msg']))
                    sys.stdout.flush()
            else:
                print("[Server]: Username can't be empty.")
    except:
        sys.exit(1)

def main():
    username = select_username()
    # start two threads: one for receiving messages and one for sending them out
    threading.Thread(target = receive_message_thread).start()
    threading.Thread(target = send_message_thread, args = (username,)).start()


if __name__ == "__main__":
    main()
