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
            socket_writer(sock)
            outputs.remove(sock)
        for sock in exceptional:
            input_storage.remove(sock)
            if sock in outputs:
                outputs.remove(sock)
            sock.close()
            


def new_connection(socket, inputs):
    connect, address = socket.accept()
    connect.setblocking(0)
    inputs.append(connect)
    

def socket_reader(socket, input_storage, request_message, response_messages, outputs):
    message = socket.recv(1024).decode()
    if message:
        if not re.search("GET /* HTTP/1.0", message):
            response_messages{socket} += "HTTP/1.0 400 Bad Request\nConnection: Close\n"
            if socket not in outputs:
                outputs.append(socket)
            input_storage.remove(socket)
            socket.close()
        else:
            whole_message = parse_message(socket, message, request_message)
            if socket not in outputs:
                outputs.append(socket)
            for lines in whole_message:
                keep_alive = file_exist(socket, lines, response_messages)
                if keep_alive is 0:
                    input_storage.remove(socket)
                    socket.close()
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
def file_exist(sock, string, response):
        left_buf, file_buf, right_buf = string.split(" ")
        file_name = file_buf[1:]
        file = open(file_name, "r")
        if file:
            response{sock} += "HTTP/1.0 200 OK\n"
            lines = file.readlines()
            while lines:
                response{sock}+= lines
                lines = file.readlines()
        else:
            response{sock} += "HTTP/1.0 404 Not Found"
        if not re.search("Connection:\s?Keep-alive", string, re.IGNORECASE):
            return 0
        else:
            response{sock} += "Connection: Keep-alive\n"
            return 1
    
    
def socket_writer(socket, response):
    message = response{socket}.encode()
    socket.send(message)




def main():
    if len(sys.argv) < 3:
        print("Use proper syntax:",sys.argv[0]," ip_address port_number")
        sys.exit(1)
    ip_addy = sys.argv[1]
    port_num = sys.argv[2]
    open_simple_web_server(ip_add, port_num)

if __name__ == "__main__":
    main()
