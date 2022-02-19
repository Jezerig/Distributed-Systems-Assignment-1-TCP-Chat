# client.py
# Distributed Systems Assignment 1
# Jesse Pasanen 0545937

from inspect import _void
import socket
import select
import sys
import errno
import threading
import time

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
        message = server.recv(BUFFER).decode('utf-8')
        print(message)
    

def send_message_thread():
    time.sleep(0.5)
    while(True):
        message = sys.stdin.readline()
        if (message):
            server.send(message.rstrip('\n').encode('utf-8'))
            sys.stdout.write("[{0}]: {1}".format(USERNAME, message))
            sys.stdout.flush()

def main():
    threading.Thread(target = receive_message_thread).start()
    threading.Thread(target = send_message_thread).start()

if __name__ == "__main__":
    main()
