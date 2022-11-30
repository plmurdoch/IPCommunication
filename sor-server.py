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
        
    def unload_packet(self, message, send_queue, address):
        tokenized = message.split("\r\n")
        if re.search('DAT', tokenized[0]):
            response_mess = self.RDP_response(tokenized[0])
            response_mess += self.HTTP_response(tokenized[1],address)
            send_queue.put(response_mess)
        else:
            response = self.RDP_response(tokenized[0])
            send_queue.put(response)

  
    def RDP_response(self, rdp_mess):
        if self.state == "closed":
            if re.search('SYN',rdp_mess):
                info = re.search("(.+?)\\nSequence:(.+?)\\nLength:(.+?)\\nAcknowledgment:(.+?)\\nWindow:(.+?)\\n",rdp_mess)
                commands = info.group(1)
                seq_num = int(info.group(2))
                len_num = int(info.group(3))
                ack_num = int(info.group(4))
                win_num = int(info.group(5)) 
                response = "ACK|SYN|DAT\nSequence: "+str(seq_num)+"\nLength: "+str(self.payload)+"\nAcknowledgment: "+str(len_num+1)+"\nWindow: "+str(win_num)+"\n\r\n"
                self.state = "SYN-RCV"
                return response
        elif self.state == "SYN-RCV":
            info = re.search("(.+?)\\nSequence:(.+?)\\nLength:(.+?)\\nAcknowledgment:(.+?)\\nWindow:(.+?)\\n",rdp_mess)
            commands = info.group(1)
            seq_num = int(info.group(2))
            len_num = int(info.group(3))
            ack_num = int(info.group(4))
            win_num = int(info.group(5))
            if re.search('FIN',commands):
                response = "FIN|ACK\nSequence: "+str(ack_num)+"\nLength: 0\nAcknowledgment: "+str(seq_num+1)+"\nWindow: "+str(win_num)+"\n\r\n"
                self.state = "CON-FIN-RCV"
                return response
            else:
                print("here")
        elif self.state == "CON-FIN-RCV":
            self.state = "closed"
            
 
 
    def HTTP_response(self, http_mess, socket):
        temp = ""
        finder = file_finder(http_mess)
        file_name = finder[1]
        temp = finder[0]
        log_print(socket,http_mess, temp)
        if file_name != "":
            temp +="Connection: keep-alive\n"
            length = file_length(file_name)
            temp +="Content-Length: "+str(length)+"\n\r\n"
            file = open(file_name, "r")
            length_http = len(temp)
            packets = packetize_file(file, length_http) 
            file.close()
            temp += packets[0]
        return temp


def udp_initializer(server):
    server_sock =socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_sock.setblocking(0)
    address = (server.ip, server.port)
    server_sock.bind(address)
    inputs = [server_sock]
    outputs = []
    client_address= ("", 0)
    while True:
        readable, writable, exceptional = select.select(inputs, outputs, inputs, 1)
        if server_sock in readable:
            data, addy = server_sock.recvfrom(server.payload)
            print(data.decode())
            if addy not in server.recv_dict:
                server.recv_dict[addy] = queue.Queue()
                server.send_dict[addy] = queue.Queue()
                client_address = addy
            server.unload_packet(data.decode(),server.send_dict[addy], client_address)
            outputs.append(server_sock)
        if server_sock in writable:
            if client_address in server.send_dict:
                message = server.send_dict[client_address].get()
                if message: 
                    server_sock.sendto(message.encode(), client_address)
                outputs.remove(server_sock)
        if server_sock in exceptional:
            server_sock.close()

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
    file = open(file_name, "r")
    length = 0
    for i in file.readlines():
        for x in i:
            length += 1
    file.close()
    return length
    
def packetize_file(filename, length):
    file_packets = []
    data = ""
    for i in filename.readlines():
        for x in i:
            data += x
            length += 1
            if(length %1024) == 0:
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
    server = server_RDP(ip_add, port_num, buffer_size, payload_size) 
    udp_initializer(server)

if __name__ == "__main__":
    main()
