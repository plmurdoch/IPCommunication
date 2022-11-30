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
        self.current_file = 0
        self.state = "closed"


    def get_state(self):
        return self.state
    
   
    def init_syn(self):
        HTTP_header ="GET /"
        name = self.read[self.current_file]
        HTTP_header+=name
        HTTP_header+=" HTTP/1.0"
        length = len(HTTP_header)
        HTTP_header += "\n\r\n"
        signal = "SYN|DAT|ACK\nSequence: 0\nLength: "+str(length)+"\nAcknowledgment: -1\nWindow: "+str(self.buffer)+"\n\r\n"+HTTP_header
        self.send_buff.append(signal)
        self.state = "SYN-SENT"


    def decapsulate(self, message):
        info = re.search("(.+?)\\nSequence:(.+?)\\nLength:(.+?)\\nAcknowledgment:(.+?)\\nWindow:(.+?)\\n",message)
        commands = info.group(1)
        seq_num = int(info.group(2))
        len_no = int(info.group(3))
        acknowledgment = int(info.group(4))
        Win_num = int(info.group(5))
        command_token = commands.split('|')
        if self.state == "SYN-SENT":
            self.state = "Connect"
            ind_pack = message.split("\r\n")
            http_info = ind_pack[1]
            length = content_length(http_info)
            file_info = ind_pack[2]
            file_writer(file_info, self.write[self.current_file])
            if length < self.payload:
                response = "FIN|ACK\nSequence: "+str(acknowledgment)+"\nLength: 0\nAcknowledgment:"+str(length)+"\nWindow: "+str(self.buffer)+"\n\r\n"
                self.send_buff.append(response)
                self.state = "FIN-SENT"
            else:
                response = "ACK\nSequence: "+str(acknowledgment)+"\nLength: 0\nAcknowledgment:"+str(len_no+seq_num)+"\nWindow: "+str(self.buffer)+"\n\r\n"
                self.send_buff.append(response)
        elif self.state == "Connect":
            ind_pack = message.split("\r\n")
            file_info = ind_pack[1]
            file_writer(file_info, self.write[self.current_file])
            if length < self.payload:
                response = "FIN|ACK\nSequence: "+str(acknowledgment)+"\nLength: 0\nAcknowledgment:"+str(length)+"\nWindow: "+str(self.buffer)+"\n\r\n"
                self.send_buff.append(response)
                self.state = "FIN-SENT"
            else:
                response = "ACK\nSequence: "+str(acknowledgment)+"\nLength: 0\nAcknowledgment:"+str(length+seq_num)+"\nWindow: "+str(self.buffer)+"\n\r\n"
        elif self.state == "FIN-SENT":
            self.state = "closed"
            resp = "ACK\nSequence: "+str(acknowledgment)+"\nLength: 0\nAcknowledgment: "+str(seq_num+1)+"\nWindow "+str(Win_num)+"\n\r\n"
            self.send_buff.append(resp)
   
   

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
            if len(client.send_buff) != 0:
                mess = client.send_buff[0]
              
                client.send_buff.remove(client.send_buff[0])
                client_sock.sendto(mess.encode(), address)
            if client.get_state() == "closed":
                break
        if client_sock in exceptional:
            sys.exit(0)

    
def file_writer(file_data, file_name):
        file = open(file_name, "a")
        file.write(file_data)
        file.close()

def content_length(http_mess):
    information = re.search("(.+?)\n(.+?)\nContent-Length:(.+?)\n", http_mess)
    length = int(information.group(3))
    length += len(http_mess)
    length += 1
    return length
    
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
