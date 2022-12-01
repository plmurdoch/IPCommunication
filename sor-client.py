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
        self.possible_loss = ""

    def get_state(self):
        return self.state
    
   
    def init_syn(self):
        length, HTTPheader = self.HTTP_header()
        signal = "SYN|DAT|ACK\nSequence: 0\nLength: "+str(length)+"\nAcknowledgment: -1\nWindow: "+str(self.buffer)+"\n\r\n"+HTTPheader
        self.send_buff.append(signal)
        self.state = "SYN-SENT"

    def HTTP_header(self): 
        HTTP ="GET /"
        name = self.read[self.current_file]
        HTTP+=name
        HTTP+=" HTTP/1.0"
        if (self.current_file+1) != len(self.read):
            HTTP += "\nConnection: keep-alive\n"
        length = len(HTTP)
        HTTP +="\n\r\n"
        return (length, HTTP)

    def decapsulate(self, message):
        info = re.search("(.+?)\\nSequence:(.+?)\\nLength:(.+?)\\nAcknowledgment:(.+?)\\nWindow:(.+?)\\n(.+)",message, re.DOTALL)
        commands = info.group(1)
        seq_num = int(info.group(2))
        if seq_num == 0:
            seq_num = 1
        len_no = int(info.group(3))
        acknowledgment = int(info.group(4))
        Win_num = int(info.group(5))
        possible_http_info = info.group(6)
        if self.state == "SYN-SENT":
            if re.search("RST", commands):
                self.state = "closed"
                self.send_buff.append("")
            else:
                self.state = "Connect"
                http_info = possible_http_info.lstrip('\r\n')
                packet_size = len(http_info)
                write = re.search("(.+?)\\n\\r\\n(.+)",http_info, re.DOTALL)
                file_info = write.group(2)
                file_writer(file_info, self.write[self.current_file])
                if packet_size < self.payload:
                    if (self.current_file+1) == len(self.read):
                        response = "FIN|ACK\nSequence: "+str(acknowledgment)+"\nLength: 0\nAcknowledgment:"+str(len_no+seq_num)+"\nWindow: "+str(self.buffer)+"\n\r\n"
                        self.send_buff.append(response)
                        self.state = "FIN-SENT"
                    else:
                        self.current_file += 1 
                        header_size, header_info = self.HTTP_header()
                        resp = "DAT|ACK\nSequence: "+str(acknowledgment+header_size)+"\nLength: "+str(header_size)+"\nAcknowledgment: "+str(len_no+seq_num)+"\nWindow: "+str(Win_num)+"\n\r\n"+header_info
                        self.send_buff.append(resp)
                else:
                    response = "ACK\nSequence: "+str(acknowledgment)+"\nLength: 0\nAcknowledgment:"+str(packet_size+seq_num)+"\nWindow: "+str(self.buffer)+"\n\r\n"
                    self.send_buff.append(response)
        elif self.state == "Connect":
            file_info = possible_http_info[2:]
            packet_size = len(file_info)
            if re.search("HTTP/1.0 (.+?)\\nConnection: keep-alive\\nContent-Length:",file_info):
                temp = re.search("(.+?)\\n\\r\\n(.+)", file_info, re.DOTALL)
                if len_no < len(file_info):
                    packet_size = len(temp.group(2))
                file_info = temp.group(2)
            file_writer(file_info, self.write[self.current_file])
            if packet_size < self.payload:
                if (self.current_file+1) == len(self.read):
                    if not re.search("RST",commands):
                        response = "FIN|ACK\nSequence: "+str(acknowledgment)+"\nLength: 0\nAcknowledgment:"+str(packet_size+seq_num)+"\nWindow: "+str(self.buffer)+"\n\r\n"
                        self.send_buff.append(response)
                        self.state = "FIN-SENT"
                    else:
                        self.state = "closed"
                else:
                    self.current_file += 1 
                    header_size, header_info = self.HTTP_header()
                    resp = "DAT|ACK\nSequence: "+str(acknowledgment+header_size)+"\nLength: "+str(header_size)+"\nAcknowledgment: "+str(len_no+seq_num)+"\nWindow: "+str(Win_num)+"\n\r\n"+header_info
                    self.send_buff.append(resp)
            else:
                response = "ACK\nSequence: "+str(acknowledgment)+"\nLength: 0\nAcknowledgment:"+str(packet_size+seq_num)+"\nWindow: "+str(self.buffer)+"\n\r\n"
                self.send_buff.append(response)
        elif self.state == "FIN-SENT":
            self.state = "closed"
            if re.search("RST",commands):
                resp = ""
                self.send_buff.append(resp)
            else:
                resp = "ACK\nSequence: "+str(acknowledgment)+"\nLength: 0\nAcknowledgment: "+str(seq_num+1)+"\nWindow "+str(Win_num)+"\n\r\n"
                self.send_buff.append(resp)

def udp_initialize(client):
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_sock.setblocking(1)
    client_sock.settimeout(3)
    address = (client.ip, client.port)
    client.init_syn()
    inputs = [client_sock]
    outputs = [client_sock]
    while True:
        readable, writable, exceptional = select.select(inputs, outputs, inputs, 1)
        if client_sock in readable:
            try:
                message, address = client_sock.recvfrom(client.buffer)
            except client_sock.TimeoutError:
                if len(client.possible_loss) != 0:
                    send_timestamps(client.possible_loss)
                client_sock.sendto(client.possible_loss.encode(),address)
            else:
                receive_timestamps(message.decode())
                client.decapsulate(message.decode())
        if client_sock in writable:
            if len(client.send_buff) != 0:
                mess = client.send_buff[0]
                client.possible_loss = mess
                client.send_buff.remove(client.send_buff[0])
                if len(mess) != 0:
                    send_timestamps(mess)
                client_sock.sendto(mess.encode(), address)
            if client.get_state() == "closed":
                break
        if client_sock in exceptional:
            break

    
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

def receive_timestamps(message):
    time_string = time.strftime("%a %d %b %H:%M:%S %Z %Y", time.localtime())
    info = re.search("(.+?)\\n(.+?)\\n(.+?)\\n(.+?)\\n(.+?)\\n", message)
    command = info.group(1)
    header_1 = info.group(2)
    header_2 = info.group(3)
    header_3 = info.group(4)
    header_4 = info.group(5)
    temp = command.split('|')
    if len(temp) > 2:
        first = temp[0]
        second = temp[1]
        third = temp[2]
        command_1 = second+"|"+first
        command_2 = third+"|"+first
        info = re.search("Sequence: (.+?)", header_1)
        seq_no = int(info.group(1))
        print(str(time_string)+": Receive; "+command_1+"; "+header_1+"; Length: 0; Acknowledgment: 1; "+header_4)
        print(str(time_string)+": Receive; "+command_2+"; Sequence: "+str(seq_no+1)+"; "+header_2+"; "+header_3+"; "+header_4)
    else:
        print(str(time_string)+": Receive; "+command+"; "+header_1+"; "+header_2+"; "+header_3+"; "+header_4)

def send_timestamps(message):
    time_string = time.strftime("%a %d %b %H:%M:%S %Z %Y", time.localtime())
    if not re.search("(.+?)\\n(.+?)\\n(.+?)\\n(.+?)\\n(.+?)\\n", message):
        return
    info = re.search("(.+?)\\n(.+?)\\n(.+?)\\n(.+?)\\n(.+?)\\n", message)
    command = info.group(1)
    header_1 = info.group(2)
    header_2 = info.group(3)
    header_3 = info.group(4)
    header_4 = info.group(5)
    print(str(time_string)+": Send; "+command+"; "+header_1+"; "+header_2+"; "+header_3+"; "+header_4)
  
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
