import socket
import select
import sys
import queue
import time
import re

class rdp_send:
    def __init__(self):
        self.state = "closed"
    def __send(self):
        if self.state == "syn-sent":
            snd_buf.append("SYN\nSequence: 0\nLength: 0\n")
        if self.state == "open":
            #Write the available window of DAT rdp packets into send_buf
            #If all data has been sent, call self.close()
        if self.state ="FIN-send":
            #Write FIN rdp packet into send-buf
    def open(self, snd_buf):
        snd_buf.append("SYN\nSequence: 0\nLength: 0\n")
        self.state = "syn-sent"
    def rcv_ack(self, mess):
        if self.state == "syn-sent":
            #if Ack# is correct:
                self.state = "open"
        if self.state == "open":
            #if 3 duplicate received:
                #Resend packets
            #if ack# correct:
                #move the sliding window and call self.send()
        if self.state ="FIN-sent":
            #if ack# correct:
                self.state = "closed"
    def timeout(self):
        if self.state != "closed":
            #Rewrite the rdp into buffer
    def close(self):
        #Write FIN packet to send_buf
        self.state = "FIN-sent"
    def getstate(self):
        return state

class rdp_receive:
    def __init__(self):
        self.state = "closed"
    def getstate(self):
        return state
    def recieve (self, send_state):
        if send_state == "syn-sent":
            
    def rcv_data(self, message):
        #packet handling
    
    
def udp_initializer(ip_ad, port, read, write):
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setblocking(0)
    udp_address = (ip_ad, port)
    udp_sock.bind(udp_address)
    byte_list = separate_by_bytes(read)
    socket_udp(udp_sock)
    
def socket_udp(udp):
    timeout = 60 
    while:
        readable, writable, exceptional = select.select([udp], [udp], [udp], timeout)
        if udp in readable:
            data = udp.recv(1024)
            temp = ""
            while data:
                temp = temp+data.decode()
                data = udp.recv(1024)
            rcv_buf.append(temp)
            if not re.search(".*\\nSequence:.*\\nLength:.*\\n", temp) 
            and not re.search(".*\\nAcknowledgment:.*\\nWindow:.*\\n", temp):
                #Write rst paket into snd_buf
            else:
                if re.search("ACK",temp):
                    rdp_sender.rcv_ack(message)
                else:
                    rdp_receiver.rcv_data(message)
                    
        if udp in writable:
            bytes_send = udp.send(send_buf.encode())
        if timeout:
            if rdp_sender.getstate() == "closed" and rdp_receiver.getstate() =="closed":
                break
            # rdp_sender.timeout()


def separate_by_bytes(read):
    byte_size = 1024
    list_bytes = []
    for i in range(0, len(read), byte_size):
        list_bytes.append(read[i:i+byte_size])
    return list_bytes
    
def main():
    if len(sys.argv) < 5:
        print("Use proper syntax:",sys.argv[0]," ip_address port_number read_file_name write_file_name")
        sys.exit(1)
    ip_add = sys.argv[1]
    port_num = int(sys.argv[2])
    read_file = sys.argv[3]
    write_file = sys.argv[4]
    udp_initializer(ip_add, port_num, read_file, write_file)

if __name__ == "__main__":
    main()
