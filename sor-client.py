import socket
import select
import sys
import queue
import time
import re

class Client_RDP:
    def __init__(self, ip, port, buffer, payload, read, write):
        self.ip = ip
        self.port = port
        self.buffer = buffer
        self.payload = payload
        self.read = read
        self.write = write
        self.recv_buff = []
        self.send_buff = []
        self.state = "closed"


    def get_state(self):
        return self.state


    def init_syn(self):
        HTTP_header ="GET /"
        name = self.read[0]
        HTTP_header+=name
        HTTP_header+=" HTTP/1.0\nConnection: keep-alive\n\r\n"
        length = len(HTTP_header)
        signal = "SYN|DAT|ACK\nSequence: 0\nLength: "+str(length)+"\nAcknowledgment:-1\nWindow: "+str(self.buffer)+"\n\r\n"+HTTP_header
        self.send_buff.append(signal)
        self.state = "SYN-SENT"

    def decapsulate(self, message):
        info = re.search("(.+?)\\nSequence:(.+?)\\nLength:(.+?)\\nAcknowledgment:(.+?)\\nWindow(.+?)\\n",message)
        commands = info.group(1)
        seq_num = int(info.group(2))
        length = int(info.group(3))
        acknowledgment = int(info.group(4))
        Win_num = int(info.group(5))
        
        print(commands)

def udp_initialize(client):
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_sock.setblocking(0)
    address = (client.ip, client.port)
    client.init_syn()
    inputs = [client_sock]
    outputs = [client_sock]
    while True:
        readable, writable, exceptional = select.select(inputs, outputs, inputs, 1)
        if client_sock in readable:
            message, address = client_sock.recvfrom(client.buffer)
            client.decapsulate(message.decode())
        if client_sock in writable:
            send_to_server(client_sock,client.send_buff, address)
        if client_sock in exceptional:
            sys.exit(1)

def send_to_server(socket, sender, addy):
    ##sending to server function (control flow)
    for x in sender:
        sender.remove(x)
        socket.sendto(x.encode(),addy)
    
#Window size that the server sends restricts the ack send size
def main():
    if len(sys.argv) < 6:
        print("Use proper syntax:",sys.argv[0]," server_ip_address udp_port_number client_buffer_size client_payload_length read_file_name write_file_name [read_file_name write_file_name]*")
        sys.exit(1)
    elif (len(sys.argv)%2) != 1:
        print("Use proper syntax:",sys.argv[0]," server_ip_address udp_port_number client_buffer_size client_payload_length read_file_name write_file_name [read_file_name write_file_name]*")
        sys.exit(1)
    ip_add = sys.argv[1]
    port_num = int(sys.argv[2])
    client_buff_size = int(sys.argv[3])
    client_pay_size = int(sys.argv[4])
    counter = 5
    read_file = []
    write_file = []
    while counter < len(sys.argv):
        if (counter % 2) == 1:
            read_file.append(sys.argv[counter])
        else:
            write_file.append(sys.argv[counter])
        counter+= 1
    client = Client_RDP(ip_add, port_num, client_buff_size, client_pay_size, read_file, write_file)
    udp_initialize(client)

if __name__ == "__main__":
    main()
