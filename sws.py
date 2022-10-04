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
        readable, writable, exceptional = select.select(input_storage, outputs, input_storage, 60)
        for sock in readable:
            if sock is s:
                new_connection(sock, input_storage, response_messages, request_message)
            else:
                socket_reader(sock, input_storage, request_message, response_messages, outputs)
        for sock in writable:
            socket_writer(sock, response_messages)
        for sock in exceptional:
            input_storage.remove(sock)
            if sock in outputs:
                outputs.remove(sock)
            sock.close()
            


def new_connection(socket, inputs, response, request):
    connect, address = socket.accept()
    connect.setblocking(0)
    inputs.append(connect)
    response[connect] = queue.Queue()
    request[connect] = queue.Queue()
    connect.settimeout(60)
    
    

def socket_reader(socket, input_storage, request_message, response_messages, outputs):
    message = socket.recv(1024)
    if message:
        request = ""
        while message:
            request = request + message.decode()
            if message.find(b'\n') == 0 or message.find(b'\r\n') == 0:
                break
            else:
                message = socket.recv(1024)
        request_message[socket].put(request)
        if not re.search("GET /.* HTTP/1"+r"\."+"0", request):
            response_messages[socket].put("HTTP/1.0 400 Bad Request\r\nConnection: Close\r\n\r\n")
            if socket not in outputs:
                outputs.append(socket)
        else:
            if socket not in outputs:
                outputs.append(socket)
            keep_alive = file_exist(socket, request, response_messages)
            if keep_alive == 0:
                response_messages[socket].put("Connection: Close\r\n\r\n")
                input_storage.remove(socket)
            else:
                socket_reader(socket, input_storage, request_message, response_messages, outputs)
        response_log(socket, request_message, response_messages)
    else:
        if socket in outputs:
            outputs.remove(socket)
        socket.close()


def file_exist(sock, string, response):
        
        file_buf= re.search('GET /(.+?) HTTP/1.0', string)
        file_name = file_buf.group(1)
        file = open(file_name, "r")
        if file:
            response[sock].put("HTTP/1.0 200 OK\n")
            lines = file.readlines()
            while lines:
                response[sock].put(lines)
                lines = file.readlines()
        else:
            response[sock].put("HTTP/1.0 404 Not Found")
        if not re.search("Connection:\s?Keep-alive", string, re.IGNORECASE):
            return 0
        else:
            response[sock].put("Connection: Keep-alive\r\n\r\n")
            return 1
    
def response_log(socket, request, response):
    ip, port_num = socket.getpeername()
    print(time.strftime("%a %b %d, %H:%M:%S %Z %Y:", time.localtime())+ip+":"+port_num)
    
    
    
def socket_writer(socket, response):
    message = response[socket].get()
    for lines in message:  
        socket.send(lines.encode())




def main():
    if len(sys.argv) < 3:
        print("Use proper syntax:",sys.argv[0]," ip_address port_number")
        sys.exit(1)
    ip_add = sys.argv[1]
    port_num = int(sys.argv[2])
    open_simple_web_server(ip_add, port_num)

if __name__ == "__main__":
    main()
