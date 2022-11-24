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
        self.state = "closed"

def udp_initializer(server):
    server_sock =socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_sock.setblocking(0)
    address = (server.ip, server.port)
    server_sock.bind(address)
    inputs = [server_sock]
    outputs = []
    while inputs:
        readable, writable, exceptional = select.select(inputs, outputs, inputs, timeout)
        for sock in readable:
            data, address = sock.recvfrom(server.payload)
            print(data.decode())
        for sock in writable:
            sys.exit(1)
        for sock in exceptional:
            sys.exit(1)
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
