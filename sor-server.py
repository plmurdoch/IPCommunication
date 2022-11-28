import socket
import select
import sys
import queue
import time
import re

class server_RDP:
    def __init__(self, ip, port, buffer, payload):
        self.ip = ip
        self.port = port
        self.buffer_size = buffer
        self.payload = payload
        self.send_dict = {}
        self.recv_dict = {}
        self.state = "closed"
        
    def get_state(self):
        return self.state
        
    def unload_packet(self, message, send_queue):
        tokenized = message.split("\r\n")
        if len(tokenized) == 2:
            RDP_response(tokenized[0])
            HTTP_response(tokenized[1])
        else:
            RDP_response(tokenized[0])
        
    

def udp_initializer(server):
    server_sock =socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_sock.setblocking(0)
    address = (server.ip, server.port)
    server_sock.bind(address)
    inputs = [server_sock]
    outputs = [server_sock]
    while True:
        readable, writable, exceptional = select.select(inputs, outputs, inputs, 1)
        if server_sock in readable:
            data, addy = server_sock.recvfrom(server.payload)
            if addy not in server.recv_dict:
                server.recv_dict[addy] = {}
                server.send_dict[addy] = {}
            server.unload_packet(data.decode(),server.send_dict[addy])
        if server_sock in writable:
            send_to_client(server_sock ,server.send_dict)
        if server_sock in exceptional:
            sys.exit(1)

def send_to_client(socket,dictionary):
    for x in dictionary:
        while len(dictionary[x]) != 0:
            message = dictionary[x].dequeue()
            socket.sendto(message.decode(), x)
 

def main():
    if len(sys.argv) < 5:
        print("Use proper syntax:",sys.argv[0]," Server_ip_address server_udp_port_number server_buffer_size server_payload_length")
        sys.exit(1)
    ip_add = sys.argv[1]
    port_num = int(sys.argv[2])
    buffer_size = int(sys.argv[3])
    payload_size = int(sys.argv[4])
    server = server_RDP(ip_add, port_num, buffer_size, payload_size) 
    udp_initializer(server)

if __name__ == "__main__":
    main()
