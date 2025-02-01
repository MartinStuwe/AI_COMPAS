
import json
import socket
import os


def start_connection():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    with open(os.path.expanduser("~/act-r-port-num.txt"), 'r') as f:
        port = int(f.readline())
    
    with open(os.path.expanduser("~/act-r-address.txt"), 'r') as f:
        host = f.readline()
    sock.connect((host, port))

    sock.setblocking(0)

    return sock


# Send message
def send(socket,message):
    m = message + chr(4)
    socket.sendall(m.encode('utf-8'))


def receive(socket):
    buffer= ''
    try:
        while not chr(4) in buffer:
            data = socket.recv(1)
            buffer += data.decode('utf-8')
    
        return json.loads(buffer[0:-1])
    except BlockingIOError:
        # No more data available to read
        return


def communicate_socket(sock, message):
    send(sock, message)
    message = receive(sock)

    return message
