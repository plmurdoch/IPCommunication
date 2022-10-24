import socket
import select
import sys
import queue
import time
import re

class rdp_sender:
    def __init__(self):
        self.state = "closed"
    def __send(self):
        if self.state == "syn-sent":
        #Write SYN rdp packet into send_buf
        if self.state == "open":
            #Write the available window of DAT rdp packets into send_buf
            #If all data has been sent, call self.close()
        if self.state ="FIN-send":
            #Write FIN rdp packet into send-buf
    def open(self, snd_buf):
        snd_buf.append("SYN")
        snd_buf.append("Sequence: 0")
        snd_buf.append("Length: 0")
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

class rdp_receiver:
    def __init__(self):
        self.state = "closed"
    
    
def udp_initializer(ip_ad, port, read, write):
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setblocking(0)
    udp_address = (ip_ad, port)
    udp_sock.bind(udp_address)
    udp_sock.listen(5)
    socket_listener(udp_sock)
    
def socket_listener(udp):
    send_buf =[]
    rcv_buf = []
    inputs = [udp]
    while inputs:
        readable, writable, exceptional = select.select(inputs, inputs, inputs, 60)
        if udp in readable:
            #receive data and append into rcv_buf
            #if message not recognized:
                #Write rst packet into snd_buf
            #if message in rcv_buf complete:
                #If message is ACK:
                    #rdp_sender.rcv_ack(message)
                #Else:
                    #Rdp_receiver.rcv_data(message)
        if udp in writable:
            bytes_send = udp_sock.send(send_buf)
        if timeout:
            if rdp_sender.getstate() == "closed" and rdp_receiver.getstate() =="closed"
                break
            rdp_sender.timeout()

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
