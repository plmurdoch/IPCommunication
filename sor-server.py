import socket
import select
import sys
import queue
import time
import re

class server_RDP:
    def __init__(self, address, buffer, payload):
        self.address = address
        self.buffer_size = buffer
        self.payload = payload
        self.send_buff = {}
        self.recv_dict = {}
        self.state = "closed"
        self.packet_num = 0
        self.packets = []
        self.next_ack = 0
        self.retransmit = []
        self.prev_recv_mess = ""
        self.prev_sent_mess = ""
 
    def get_state(self):
        return self.state
        
    def unload_packet(self, message):
        tokenized = message.split("\r\n")
        if len(tokenized) == 1:
            tokenized = message.split("\n\n") #special cases as rst_test was inconsistent with its RDP and HTTP headers 
        if re.search('DAT', tokenized[0]):
            temp = self.HTTP_response(tokenized[1], tokenized[0])
            response_mess = self.RDP_response(tokenized[0])
            if not re.search('RST', response_mess):
                    response_mess += temp
            self.send_buff.put(response_mess)
        else:
            response = self.RDP_response(tokenized[0])
            self.send_buff.put(response)


    def RDP_response(self, rdp_mess):
        if self.state == "closed":
            if re.search('SYN',rdp_mess):
                self.state = "SYN-RCV"
                info = re.search("(.+?)\\nSequence:(.+?)\\nLength:(.+?)\\nAcknowledgment:(.+?)\\nWindow:(.+?)\\n",rdp_mess)
                if info is None:
                    info = re.search("(.+?)\\nSequence:(.+?)\\nLength:(.+?)\\nAcknowledgement:(.+?)\\nWindows: (.+)",rdp_mess) #special cases as rst_test was inconsistent with its RDP and HTTP headers 
                commands = info.group(1)
                seq_num = int(info.group(2))
                len_num = int(info.group(3))
                ack_num = int(info.group(4))
                win_num = int(info.group(5))
                if win_num > self.buffer_size or len(self.packets) == 0:
                    response = "RST\nSequence: "+str(seq_num)+"\nLength: 0\nAcknowledgment: "+str(ack_num)+"\nWindow: "+str(self.buffer_size)+"\n\r\n"
                    self.state = "closed"
                    return response
                else:
                    response = ""
                    if (self.packet_num+1) == len(self.packets):
                        response = "ACK|SYN|DAT\nSequence: "+str(seq_num)+"\nLength: "+str(len(self.packets[self.packet_num]))+"\nAcknowledgment: "+str(len_num+1)+"\nWindow: "+str(win_num)+"\n\r\n"
                        self.next_ack = 1+seq_num + len(self.packets[self.packet_num])
                    else:
                        response = "ACK|SYN|DAT\nSequence: "+str(seq_num)+"\nLength: "+str(self.payload)+"\nAcknowledgment: "+str(len_num+1)+"\nWindow: "+str(win_num)+"\n\r\n"
                        self.next_ack = 1+ seq_num + self.payload
                    return response
        elif self.state == "SYN-RCV":
            info = re.search("(.+?)\\nSequence:(.+?)\\nLength:(.+?)\\nAcknowledgment:(.+?)\\nWindow:(.+?)\\n",rdp_mess)
            commands = info.group(1)
            seq_num = int(info.group(2))
            len_num = int(info.group(3))
            ack_num = int(info.group(4))
            win_num = int(info.group(5))
            if re.search('FIN',commands):
                if win_num > self.buffer_size:
                    self.state = "FIN-RCV"
                    response = "RST\nSequence: "+str(seq_num)+"\nLength: 0\nAcknowledgment: "+str(ack_num)+"\nWindow: "+str(self.buffer_size)+"\n\r\n"
                    self.state = "closed"
                    return response
                else:
                    response = "FIN|ACK\nSequence: "+str(ack_num)+"\nLength: 0\nAcknowledgment: "+str(seq_num+1)+"\nWindow: "+str(win_num)+"\n\r\n"
                    self.state = "FIN-SENT"
                    return response
            else:
                if win_num > self.buffer_size or len(self.packets) == 0:
                    response = "RST\nSequence: "+str(seq_num)+"\nLength: 0\nAcknowledgment: "+str(ack_num)+"\nWindow: "+str(self.buffer_size)+"\n\r\n"
                    self.state = 'closed'
                    return response
                else:
                    if not re.search("DAT", commands):
                        self.packet_num += 1
                        if (self.packet_num+1) == len(self.packets):
                            resp = "DAT|ACK\nSequence: "+str(ack_num)+"\nLength: "+str(len(self.packets[self.packet_num]))+"\nAcknowledgment: "+str(seq_num+len_num)+"\nWindow: "+str(win_num)+"\n\r\n"+self.packets[self.packet_num]
                            self.next_ack = ack_num + len(self.packets[self.packet_num])
                            self.packet_num = 0
                            self.retransmit = self.packets
                            self.packets = []
                            return resp
                        else:
                            resp = "DAT|ACK\nSequence: "+str(ack_num)+"\nLength: "+str(self.payload)+"\nAcknowledgment: "+str(seq_num+len_num)+"\nWindow: "+str(win_num)+"\n\r\n"+self.packets[self.packet_num]
                            self.next_ack = ack_num + self.payload
                            return resp
                    else:
                        if (self.packet_num+1) == len(self.packets):
                            resp = "DAT|ACK\nSequence: "+str(ack_num)+"\nLength: "+str(len(self.packets[self.packet_num]))+"\nAcknowledgment: "+str(seq_num+len_num)+"\nWindow: "+str(win_num)+"\n\r\n"
                            self.next_ack = ack_num + len(self.packets[self.packet_num])
                            return resp
                        else:
                            resp = "DAT|ACK\nSequence: "+str(ack_num)+"\nLength: "+str(self.payload)+"\nAcknowledgment: "+str(seq_num+len_num)+"\nWindow: "+str(win_num)+"\n\r\n"
                            self.next_ack = ack_num + self.payload
                            return resp
        elif self.state == "FIN-SENT":
            if re.search('ACK',rdp_mess):
                self.state = "closed"
                self.packets = []
                string = self.RDP_response(rdp_mess)
                return string
 
 
    def HTTP_response(self, http_mess, command):
        temp = ""
        finder = file_finder(http_mess)
        file_name = finder[1]
        temp = finder[0]
        size_info = re.search("Window: (.+)\\n",command)
        if size_info is None:
            size_info = re.search("Windows: (.+)",command) #special cases as rst_test was inconsistent with its RDP and HTTP headers 
        size = int(size_info.group(1))
        if self.buffer_size>= size:
            log_print(self.address,http_mess, temp)
        if file_name != "":
            temp +="Connection: keep-alive\n"
            length = file_length(file_name)
            temp +="Content-Length: "+str(length)+"\n\r\n"
            try:
                file = open(file_name, "r")
            except FileNotFoundError:
                return temp
            else:
                length_http = len(temp)
                self.packets = packetize_file(file, length_http, self) 
                file.close()
                temp += self.packets[0]
        return temp

def udp_initializer(ip, port, buffer, payload):
    sock =socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    address = (ip, port) 
    sock.bind(address)
    connections = {}
    inputs = [sock]
    outputs = []
    client_address= {}
    client_number = 0
    while True:
        readable, writable, exceptional = select.select(inputs, outputs, inputs, 1)
        for s in readable:
            if s is sock:
                new_connection = (s, inputs)
            data, addy = s.recvfrom(payload)
            if addy not in connections:
                client_address[s] = addy
                connections[addy] = rdp_connection(addy, buffer, payload)
                connections[addy].recv_dict = queue.Queue()
                connections[addy].send_buff = queue.Queue()
            if connections[addy].prev_recv_mess == data.decode():
                connections[addy].send_buff.put(connections[addy].prev_sent_mess)
            else:
                connections[addy].prev_recv_mess = data.decode()
                connections[addy].unload_packet(data.decode())
            outputs.append(s)
        for s in writable:
            x = client_address[s]
            if not connections[x].send_buff.empty():
                message = connections[x].send_buff.get()
            if message: 
                connections[x].prev_sent_mess = message
                sock.sendto(message.encode(), x)
            outputs.remove(s)
        for s in exceptional:
            s.close()
            del client_address[s]

def rdp_connection(address, buffer_size, payload_size):
    connection = server_RDP(address, buffer_size, payload_size) 
    return connection

def new_connection(sock, inputs):
    inputs.append(sock)

def file_finder(string):
    file_buf= re.search('GET /(.+?) HTTP/1.0', string)
    resp = ""
    name = ""
    if file_buf:
        file_name = file_buf.group(1)
        name = file_name
        try:
            file = open(file_name, "r")
        except FileNotFoundError:
            resp += "HTTP/1.0 404 Not Found\n"
        else:
            resp += "HTTP/1.0 200 OK\n"
            file.close()
    else:
        resp += "HTTP/1.0 400 Bad Request\n"
    return (resp, name)
    
def file_length(file_name):
    try:
        file = open(file_name, "r")
    except FileNotFoundError:
        return 0
    else:
        length = 0
        for i in file.readlines():
            for x in i:
                length += 1
        file.close()
        return length
    
def packetize_file(filename, length, server):
    file_packets = []
    data = ""
    for i in filename.readlines():
        for x in i:
            data += x
            length += 1
            if(length %server.payload) == 0:
                file_packets.append(data)
                data = ""
    file_packets.append(data)
    return file_packets

def log_print(address, request, response):
    time_string = time.strftime("%a %d %b %H:%M:%S %Z %Y", time.localtime())
    ip_address, port_num = address
    buffer_1 = request.split('\n')
    buffer = buffer_1[0]
    buffer_2 = response.strip('\r\n')
    print(str(time_string)+": "+str(ip_address)+":"+str(port_num)+" "+buffer+"; "+str(buffer_2))

def main():
    if len(sys.argv) < 5:
        print("Use proper syntax:",sys.argv[0]," Server_ip_address server_udp_port_number server_buffer_size server_payload_length")
        sys.exit(1)
    ip_add = sys.argv[1]
    port_num = int(sys.argv[2])
    buffer_size = int(sys.argv[3])
    payload_size = int(sys.argv[4]) 
    udp_initializer(ip_add, port_num, buffer_size, payload_size)

if __name__ == "__main__":
    main()
