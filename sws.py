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
                message_reader(message, response_messages, request_message)


def message_reader(message, response, request):
    limit_string_1 = "\r\n\r\n"
    limit_string_2 ="\n\n"
    while message != limit_string_1 or message != limit_string_2:
        request_message[s] = request_message[s] + message
    whole_message = request_message[s]
    outputs.append(s)
    for lines in whole_message:
        if lines != 
        #3.for each line in whole_message:
            #4.if not in correct format: "GET /filename HTTP/1.0"
                response_messages{s} += "HTTP/1.0 400 Bad Request"
            else:
                #5. response messages with more oomf
                response_messages{s} += "HTTP/1.0 200 OK"



def main():
    if len(sys.argv) < 3:
        print("Use proper syntax:",sys.argv[0]," ip_address port_number")
        sys.exit(1)
    ip_addy = sys.argv[1]
    port_num = sys.argv[2]
    open_simple_web_server(ip_addy, port_num)

if __name__ == "__main__":
    main()
