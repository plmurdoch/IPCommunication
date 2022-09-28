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

def listen_for_sockets(server):
    inputs = [server]
    outputs = []
    response_messages = {}
    request_message = {}
    while True:
        readable, writable, exceptional = select.select(inputs, outputs, inputs)
        for s in readable:
            if s == server:
                s.accept()
                inputs.append(s)
            else:
                message = s.recv(1024).decode()
            if message:
                message_reader(s,message, response_messages, request_message)
                server.close()
                break


def message_reader(s, message, response, request):
    limit_string_1 = "\r\n\r\n"
    limit_string_2 ="\n\n"
    while message != limit_string_1 or message != limit_string_2:
        request_message[s] = request_message[s] + message
    whole_message = request_message[s]
    outputs.append(s)
    for lines in whole_message:
        if not re.search("GET /* HTTP/1.0", lines):
            response_messages{s} += "HTTP/1.0 400 Bad Request"
            break
        else:
            response_messages{s} += "HTTP/1.0 200 OK"
            if re.search("Connection:\s?Keep-alive", lines, re.IGNORECASE):
            else:





def main():
    if len(sys.argv) < 3:
        print("Use proper syntax:",sys.argv[0]," ip_address port_number")
        sys.exit(1)
    ip_addy = sys.argv[1]
    port_num = sys.argv[2]
    open_simple_web_server(ip_addy, port_num)

if __name__ == "__main__":
    main()
