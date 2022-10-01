import socket
import select
import sys
import queue
import time
import re


def open_simple_web_server(ip_num, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(0)
    server_address = (ip_num, port)
    server.bind(server_address)
    server.listen(5)
    listen_for_sockets(server)


def listen_for_sockets(s):
    input_storage = [s]
    outputs = []
    response_messages = {}
    request_message = {}
    while input_storage:
        readable, writable, exceptional = select.select(input_storage, outputs, input_storage)
        for sock in readable:
            if sock is s:
                new_connection(sock, input_storage)
            else:
                socket_reader(sock, input_storage, request_message, response_messages, outputs)
        for sock in writable:
            socket_writer(sock):
        for sock in exceptional:
            error_handle(sock)


def new_connection(socket, inputs):
    connect, address = socket.accept()
    connect.setblocking(0)
    inputs.append(connect)
    

def socket_reader(socket, input_storage, request_message, response_messages, outputs):
    message = socket.recv(1024).decode()
    if message:
        whole_message = parse_message(socket, message, request_message)
        if socket not in outputs:
            outputs.append(socket)
        for lines in whole_message:
            filter_message(socket, lines, response_messages)
    else:
        if socket in outputs:
            outputs.remove(socket)
        input_storage.remove(socket)
        socket.close()


def parse_message(sock, mess, request):
    limit_string_1 = "\r\n\r\n"
    limit_string_2 ="\n\n"
    while mess != limit_string_1 or mess != limit_string_2:
        request[sock] = request[sock] + mess
    whole = request[sock]
    return whole

#Editing here
#Reference site: http://pymotw.com/3/select/
def filter_message(sock, string, response):   
    if not re.search("GET /* HTTP/1.0", lines):
        response_messages{sock} += "HTTP/1.0 400 Bad Request"
    else:
        response_messages{sock} += "HTTP/1.0 200 OK"
        if re.search("Connection:\s?Keep-alive", lines, re.IGNORECASE):
        else:
            sock.close()
    
    
def socket_writer(socket):

def error_handler(socket):




def main():
    if len(sys.argv) < 3:
        print("Use proper syntax:",sys.argv[0]," ip_address port_number")
        sys.exit(1)
    ip_addy = sys.argv[1]
    port_num = sys.argv[2]
    open_simple_web_server(ip_addy, port_num)

if __name__ == "__main__":
    main()
