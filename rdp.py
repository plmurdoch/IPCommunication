import socket
import select
import sys
import queue
import time
import re

send_buf = []
rcv_buf = []
class rdp_sender:
    def __init__(self, state):
        state = "closed"
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
    def rcv_ack(self):
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
class rdp_receiver:
    def __init__(self):
def main():
    if len(sys.argv) < 5:
        print("Use proper syntax:",sys.argv[0]," ip_address port_number read_file_name write_file_name")
        sys.exit(1)
    ip_add = sys.argv[1]
    port_num = int(sys.argv[2])
    read_file = sys.argv[3]
    write_file = sys.argv[4]

if __name__ == "__main__":
    main()
