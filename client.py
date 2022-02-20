# client.py
# Distributed Systems Assignment 1
# Jesse Pasanen 0545937


import socket
import sys
import threading
import time
import json

if(len(sys.argv) != 3):
    print("To establish a connection to a server give two arguments.")
    print("client.py [IP ADDRESS] [PORT]")
    exit(1)
IP_ADDRESS = str(sys.argv[1])
PORT = int(sys.argv[2])
BUFFER = 2048

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((IP_ADDRESS, PORT))


def receive_message_thread():

    while(True):
        try:
            message_data = server.recv(BUFFER)
            message_data_decoded = json.loads(message_data.decode())
            print("[{0}]: {1}".format(message_data_decoded['username'], message_data_decoded['msg']))
        except:
            sys.exit(0)
    
def send_message_thread(username):
    time.sleep(0.5)
    while(True):
        message = sys.stdin.readline()
        if (message):
            if(message[0] == '/'):
                if(message.rstrip('\n').split(' ')[0].strip()[0:5] == '/join'):
                    if (len(message.split(' ')) == 2):
                        message_data = json.dumps({'username' : username, 'msg' : message.rstrip('\n')})
                        server.send(message_data.encode())
                    else:
                        print("Usage: '/join [Channel name]'")
                    continue

                if(message.rstrip('\n').split(' ')[0].strip()[0:6] == '/exit'):
                    if (len(message.split(' ')) == 1):
                        message_data = json.dumps({'username' : username, 'msg' : message.rstrip('\n')})
                        server.send(message_data.encode())
                        print("Disconnected.")
                        sys.exit(0)
                    else:
                        print("Command '/exit' doesn't take any arguments.")
                    continue
                if(message.rstrip('\n').split(' ')[0].strip()[0:4] == '/msg'):
                    if (len(message.split(' ')) > 2):
                        message_data = json.dumps({'username' : username, 'msg' : message.rstrip('\n')})
                        server.send(message_data.encode())
                    else:
                        print("Usage: '/msg [username] [message]'")
                    continue
                else:
                    print("Invalid command.")
        
            else:
                message_data = json.dumps({'username' : username, 'msg' : message.rstrip('\n')})
                server.send(message_data.encode())
                sys.stdout.write("[{0}]: {1}".format(username, message))
                sys.stdout.flush()


def select_username():
    message_data = server.recv(BUFFER)
    message_data_decoded = json.loads(message_data.decode())
    print("[{0}]: {1}".format(message_data_decoded['username'], message_data_decoded['msg']))
    while(True):
        username = input("Username: ")
        server.send(username.encode('utf-8'))
        username_exists = server.recv(BUFFER).decode('utf-8')
        username_msg_data = server.recv(BUFFER)
        username_msg_data_decoded = json.loads(username_msg_data.decode())
        if not (int(username_exists)):
            sys.stdout.write("[{0}]: {1}\n".format(username_msg_data_decoded['username'], username_msg_data_decoded['msg']))
            sys.stdout.flush()
            return username
        else:
            sys.stdout.write("[{0}]: {1}\n".format(username_msg_data_decoded['username'], username_msg_data_decoded['msg']))
            sys.stdout.flush()


def main():
    username = select_username()
    threading.Thread(target = receive_message_thread).start()
    threading.Thread(target = send_message_thread, args = (username,)).start()


if __name__ == "__main__":
    main()
