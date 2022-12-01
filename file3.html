import socket
import select
import sys
import queue
import time
import re
#pipelined through string rdp 
#Good for test case 1 and medium files, possibly large files
#RDP sender class
class rdp_send:
    #initializer function
    def __init__(self, read_file):
        self.state = "closed"
        self.bytes_loaded = 0
        self.read = read_file
    #Send function for sending SYN/DAT and FIN Command messages to buffer     
    def __send(self, mess, win):
        if self.state == "syn-sent":
            strn = "SYN\nSequence: 0\nLength: 0\n"
            return (strn,0)
        if self.state == "open":
            count = 0
            info = re.search("ACK\\nAcknowledgment:(.+?)\\n", mess)
            ac = int(info.group(1))
            strn = ""
            while win> 0:
                (payload, length) = self.packetize_file()
                temp = "DAT\nSequence: "+str(ac)+"\nLength: "+str(length)+"\n\n"+payload+"\r\n"
                strn = strn + temp
                timestamps(temp, 0)
                if length < 1024:
                    return (strn,1)
                ac += length
                win -= length
            return(strn,0)
        if self.state =="FIN-sent":
            timestamps(mess, 1)
            info = re.search("ACK\\nAcknowledgment:(.+?)\\n", mess)
            ack = info.group(1)
            message = "FIN\nSequence: "+ack+"\nLength: 0\n"
            return (message,1)
    #open function for initializing sender        
    def open(self):
        message = "SYN\nSequence: 0\nLength: 0\n"
        self.state = "syn-sent"
        timestamps(message, 0)
        return (message, 0)
    #Fucntion for when acknowledgements are received
    def rcv_ack(self, mess, fin, wind):
        if self.state == "syn-sent":
            self.state = "open"
        if self.state == "open":
            mess = mess.rstrip('\r\n')
            snd_buf = mess.split('\r\n')
            ack = 0
            for i in snd_buf:
                info = re.search("ACK\\nAcknowledgment:(.+?)\\n", i)
                if not re.search("ACK\\nAcknowledgment:.*\\nWindow:.*\\n",i):
                    i = i+'\n'
                timestamps(i, 1)
                ack = info.group(1)
                mess = i
            if fin == 1:
                return self.close(mess)
            if (self.bytes_loaded+1)== int(ack):
                return self.__send(mess, wind)
        if self.state =="FIN-sent":
            self.state = "closed"
            timestamps(mess, 1)
            return("", 0)
    #Once function is done processing information, close
    def close(self,mess):
        info = re.search("ACK\\nAcknowledgment:(.+?)\\n", mess)
        ack = int(info.group(1))
        message = "FIN\nSequence: "+str(ack)+"\nLength: 0\n"
        self.state = "FIN-sent"
        timestamps(message, 0)
        return (message, 0)
    #returns state    
    def getstate(self):
        return self.state
    #def for turning file information into packets
    def packetize_file(self):
        reading = open(self.read, "r")
        string = ""
        reading.seek(self.bytes_loaded)
        count = 0
        while count < 1024:
            temp = str(reading.read(1))
            if temp == '':
                string = string+temp
                break
            else:
                string = string +temp
                count = count +1 
        self.bytes_loaded = self.bytes_loaded + count
        return (string,count)

#RDP receiver class
class rdp_receive:
    def __init__(self, write):
        self.state = "open"
        self.write = write
        self.window = 5120
    def getstate(self):
        return self.state
    #recieving data and sending ack
    def rcv_data(self, rec,fin_find):
        if re.search("SYN", rec):
            timestamps(rec, 1)
            ack_mess = "ACK\nAcknowledgment: 1\nWindow: "+str(self.window)+"\r\n"
            timestamps(ack_mess, 0)
            return ack_mess
        if re.search("DAT", rec):
            rec = rec.rstrip('\r\n')
            recv_buf = rec.split('\r\n')
            ack_strn = ""
            for i in recv_buf:
                timestamps(i, 1)
                info = re.search("DAT\\nSequence:(.+?)\\nLength:(.+?)\\n\\n", i)
                seq = int(info.group(1))
                length = int(info.group(2))
                data = i.split("\n\n", 1)
                self.file_write(data[1],fin_find)
                acknowno = seq + length
                string = ""
                if length < 1024:
                    string = "ACK\nAcknowledgment: "+str(acknowno)+"\nWindow: "+str(self.window - length)+"\r\n"
                else:
                    string ="ACK\nAcknowledgment: "+str(acknowno)+"\nWindow: "+str(self.window) +"\r\n"
                timestamps(string, 0)
                ack_strn = ack_strn +string
            return ack_strn
        if re.search("FIN", rec):
            timestamps(rec, 1)
            self.state = "closed"
            info = re.search("FIN\\nSequence:(.+?)\\nLength:(.+?)\\n", rec)
            sequence = int(info.group(1))
            ack_2 = "ACK\nAcknowledgment: "+str(sequence+1)+"\nWindow: "+str(self.window)+"\n"
            timestamps(ack_2, 0)
            return ack_2
    #Write content to file
    def file_write(self,information,fin_find):
        file = open(self.write,"a")
        file.write(information)
        if fin_find == 1:
            file.close()
    
#function for udp client communicating with udp echo server    
def udp_initializer(ip_ad, port, read, write):
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setblocking(0)
    sent_pkt = []
    recv_pkt = []
    rdp_sender = rdp_send(read)
    rdp_receiver =rdp_receive(write)
    send_buf,fin_find = rdp_sender.open() 
    address = ("10.10.1.100", port)
    timeout = 60
    bytes_sent = 0
    inputs = [udp_sock]
    outputs = [udp_sock]   
    while True:
        readable, writable, exceptional = select.select(inputs, outputs, inputs, timeout)
        if udp_sock in readable:
            data,address = udp_sock.recvfrom(bytes_sent)
            if len(data) != bytes_sent:
                send_buf = "RST\nSequence: 0\n Length: 0\n"
            if not re.search(".*\\nSequence:.*\\nLength:.*\\n", 
                             data.decode()) and not re.search(".*\\nAcknowledgment:.*\\nWindow:.*\\n", 
                                                              data.decode()):
                send_buf = "RST\nSequence: 0\nLength: 0\n"
            else:
                if re.search("ACK",data.decode()):
                    count = 0
                    send_buf,fin_find = rdp_sender.rcv_ack(data.decode(), fin_find, rdp_receiver.window)
                else:
                    send_buf = rdp_receiver.rcv_data(data.decode(),fin_find) 
        if udp_sock in writable:
            bytes_sent = udp_sock.sendto(send_buf.encode(),address)
            time.sleep(0.01)
        if udp_sock in exceptional:
            udp_sock.close()
            break
        if timeout:
            if rdp_sender.getstate() == 'closed' and rdp_receiver.getstate() == 'closed':
                udp_sock.close()
                break
#printing timestamps
def timestamps(message, send_or_recv):
    time_string = time.strftime("%a %d %b %H:%M:%S %Z %Y", time.localtime())
    if send_or_recv == 0:
        info = re.search("(.+?)\\n(.+?)\\n(.+?)\\n", message)
        command = info.group(1)
        header_1 = info.group(2)
        header_2 = info.group(3)
        print(str(time_string)+": Send;"+command+";"+header_1+";"+header_2)
    else:
        info = re.search("(.+?)\\n(.+?)\\n(.+?)\\n", message)
        command = info.group(1)
        header_1 = info.group(2)
        header_2 = info.group(3)
        print(str(time_string)+": Receive;"+command+";"+header_1+";"+header_2)
#main        
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
