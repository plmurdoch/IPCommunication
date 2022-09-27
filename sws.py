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
            #1.if s is server, accept new connection and append new connection socket to the list
            else: 
                message = s.recv(1024).decode()
            if message:
                request_message[s] = request_message[s] + message
                #2.if find "\r\n\r\n" or "\n\n" at the end of message we can process whole
                    whole_message = request_message[s]
                    outputs.append(s)
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
