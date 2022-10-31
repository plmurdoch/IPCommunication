import socket
import select
import sys
import queue
import time
import re
#Need to implement:
# -acknowledgment number tracking
# -Window tracking
# -File packet partitioning
# -Account for loss of packets
class rdp_send:
    def __init__(self):
        self.state = "closed"
    def __send(self):
        if self.state == "syn-sent":
            snd_buf = "SYN\nSequence: 0\nLength: 0\n"
            return snd_buf
        if self.state == "open":
            message = "DAT\nSequence: 0\nLength: 1024\n\nPAYLOAD\n"
            return message
            #Write the available window of DAT rdp packets into send_buf
            #If all data has been sent, call self.close()
        if self.state =="FIN-send":
            print("HERE")
            #Write FIN rdp packet into send-buf
    def open(self):
        snd_buf = "SYN\nSequence: 0\nLength: 0\n"
        self.state = "syn-sent"
        return snd_buf
    def rcv_ack(self, mess):
        if self.state == "syn-sent":
            self.state = "open"
        if self.state == "open":
            #Check acknowledgement #
            #if 3 duplicate received:
                #Resend packets
            #if ack# correct:
            return self.__send()
        if self.state =="FIN-sent":
            #if ack# correct:
                self.state = "closed"
    def timeout(self):
        if self.state != "closed":
            #Rewrite the rdp into buffer
            print('HERE')
    def close(self):
        #Write FIN packet to send_buf
        self.state = "FIN-sent"
    def getstate(self):
        return self.state

class rdp_receive:
    def __init__(self):
        self.state = "closed"
    def getstate(self):
        return self.state
    def rcv_data(self, message):
        if re.search("SYN", message):
            return "ACK\nAcknowledgment: 1\nWindow: 1024\n"
        if re.search("DAT", message):
            print('PAYLOAD Reciever')
            return "ACK\nAcknowledgment: 1\nWindow: 1024\n"
        #ACK sending
    
    
def udp_initializer(ip_ad, port, read, write):
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_sock.setblocking(0)
    udp_address = (ip_ad, port)
    udp_sock.bind(udp_address)
    byte_list = separate_by_bytes(read)
    socket_udp(udp_sock)
    
def socket_udp(udp):
    rdp_sender = rdp_send()
    rdp_receiver =rdp_receive()
    send_buf = rdp_sender.open()
    timeout = 60 
    while True:
        readable, writable, exceptional = select.select([udp], [udp], [udp], timeout)
        if udp in readable:
            data,address = udp.recvfrom(1024)
            recv_buf = data.decode()
            #loop back if within window
            if not re.search(".*\\nSequence:.*\\nLength:.*\\n", recv_buf) and not re.search(".*\\nAcknowledgment:.*\\nWindow:.*\\n", recv_buf):
                send_buf.append("RST\nSequence: 0\nLength: 0\n")
            else:
                if re.search("ACK",recv_buf):
                    send_buf = rdp_sender.rcv_ack(recv_buf)
                else:
                    send_buf = rdp_receiver.rcv_data(recv_buf)
                    
                    
        if udp in writable:
            print(send_buf)
            bytes_send = udp.sendto(send_buf.encode(),udp.getsockname())
        if timeout:
            if rdp_sender.getstate() == "closed" and rdp_receiver.getstate() =="closed":
                break
            # rdp_sender.timeout()


def separate_by_bytes(read):
    byte_size = 1024
    list_bytes = []
    file = open(read)
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
