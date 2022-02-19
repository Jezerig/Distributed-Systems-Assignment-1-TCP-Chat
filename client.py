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
USERNAME = input("Username: ")
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((IP_ADDRESS, PORT))


def receive_message_thread():
    while(True):
        message_data = server.recv(BUFFER)
        message_data_decoded = json.loads(message_data.decode())
        print("[{0}]: {1}".format(message_data_decoded['username'], message_data_decoded['msg']))
    
def send_message_thread():
    time.sleep(0.5)
    while(True):
        message = sys.stdin.readline()
        if (message):
            message_data = json.dumps({'username' : USERNAME, 'ip_address' : IP_ADDRESS, 'port' : PORT, 'msg' : message.rstrip('\n')})
            server.send(message_data.encode())
            sys.stdout.write("[{0}]: {1}".format(USERNAME, message))
            sys.stdout.flush()

def main():
    threading.Thread(target = receive_message_thread).start()
    threading.Thread(target = send_message_thread).start()

if __name__ == "__main__":
    main()
