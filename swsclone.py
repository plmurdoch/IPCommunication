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


#Fix formatting errors should go: HTTP OK or 404 not etc. then connection declaration, then file.
def socket_reader(socket, input_storage, request_message, response_messages, outputs):
    message = socket.recv(1024)
    if message:
        request = []
        while message:
            request = request.append(message.decode())
            if request[len(request-1)] == '\r\n' and request[len(request-2)] =='\r\n':
                break
            elif request[len(request-1)] == '\n' and request[len(request-2)] =='\n':
                break
            else:
                message = socket.recv(1024)
        request_message[socket].put(request)
        if socket not in outputs:
            outputs.append(socket)
        file_data = ""
        for lines in request:
            html_file_data = response_header(socket, lines, response_messages)
            #does not change the position of the html_file_data, need something to make sure
            #it does not send to request queue before getting connection data
            if html_file_data:
                file_data = html_file_data
                if not re.search("Connection:\s?Keep-alive", lines, re.IGNORECASE):
                request_message[socket].put(html_file_data)
    else:
        if socket in outputs:
            outputs.remove(socket)
        socket.close()


def response_header(sock, string, response):
    file_buf= re.search('GET /(.+?) HTTP/1.0', string)
    html_data = []
    if file_buf:
        file_name = file_buf.group(1)
        file = open(file_name, "r")
        keep_alive = 0
        if file:
            response[sock].put("HTTP/1.0 200 OK\r\n")
            lines = file.readlines()
            while lines:
                html_data.append(lines)
                lines = file.readlines()
        else:
            response[sock].put("HTTP/1.0 404 Not Found\r\n\r\n")
    else:
        if not re.search("Connection:\s?Keep-alive", string, re.IGNORECASE):
            if not re.search("Connection:",string) and not re.search("GET /.* HTTP/1.0",string):
                response_messages[socket].put("HTTP/1.0 400 Bad Request\r\n")
            response[sock].put("Connection: Close\r\n\r\n")
        else:
            response[sock].put("Connection: Keep-alive\r\n\r\n")
    return html_data



#create response log in sws
def response_log(socket, request, response):
    ip, port_num = socket.getpeername()
    string_time = time.strftime("%a %b %d, %H:%M:%S %Z %Y: ", time.localtime())
    print(string_time+ip+" : "+port_num)



#See more info on handling writer sockets.
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
