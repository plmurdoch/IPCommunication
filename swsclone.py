import socket
import select
import sys
import queue
import time
import re


def open_simple_web_server(ip_num, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setblocking(0)
    server_address = (ip_num, port)
    server.bind(server_address)
    server.listen(5)
    listen_for_sockets(server)


    
def listen_for_sockets(s):
    input_storage = [s]
    output = []
    response_messages = {}
    request_message = {}
    while input_storage:
        readable, writable, exceptional = select.select(input_storage, output, input_storage)
        for sock in readable:
            if sock is s:
                new_connection(sock, input_storage, response_messages, request_message)
            else:
                socket_reader(sock, input_storage, response_messages, output, request_message)
        for sock in writable:
            socket_writer(sock, response_messages, output,input_storage, request_message)
        for sock in exceptional:
            input_storage.remove(sock)
            if sock in output:
                output.remove(sock)
            sock.close()
            del response_messages[sock]
            del request_message[sock]



def new_connection(socket, inp, response, request):
    connect, address = socket.accept()
    connect.setblocking(0)
    inp.append(connect)
    response[connect] = queue.Queue()
    request[connect] = queue.Queue()
    connect.settimeout(60)

    

def socket_reader(socket, input_storage, response_messages, output, request_message):
    mess = socket.recv(1024)
    if re.search('\n\n', mess) or re.search('\r\n\r\n',mess):
        request_multi = []
        file_exist = ""
        keep_count = 0
        queue_for_break = 0
        ls = mess.splitlines(keepends = True)
        for lines in ls:
            request_multi.append(lines.decode())
            if request[len(request)-1] == '\r\n' and  re.search(r'\r\n',request[len(request)-2]):
                queue_for_break = 1
            elif request[len(request)-1] == '\n' and re.search(r'\n',request[len(request)-2]):
                queue_for_break = 1
            if keep_count == 0:
                file_exist = response_header(socket, lines.decode(), response_messages)
                keep_count = 1
                request_message[socket].put(lines.decode())
                if not file_exist and queue_for_break == 0:
                    response_messages[socket].put("Connection: Close\r\n\r\n")  
                    break
            else:
                keep_alive(socket, lines.decode(), response_messages)
                html_file(socket, file_exist, response_messages)
                file_exist = ""
                keep_count = 0
        if socket not in output:
            output.append(socket)
    elif mess:
        request = []
        file_exist = ""
        keep_count = 0
        queue_for_break = 0
        ls = mess.splitlines()
        while mess:
            request.append(mess.decode())
            if request[len(request)-1] == '\r\n' and  re.search(r'\r\n',request[len(request)-2]):
                queue_for_break = 1
            elif request[len(request)-1] == '\n' and re.search(r'\n',request[len(request)-2]):
                queue_for_break = 1
            if keep_count == 0:
                file_exist = response_header(socket, mess.decode(), response_messages)
                keep_count = 1
                request_message[socket].put(mess.decode())
                if not file_exist and queue_for_break == 0:
                    response_messages[socket].put("Connection: Close\r\n\r\n")  
                    break
            else:
                keep_alive(socket, message.decode(), response_messages)
                html_file(socket, file_exist, response_messages)
                file_exist = ""
            if queue_for_break == 1:
                break
            else:
                mess = socket.recv(1024)
        if socket not in output:
            output.append(socket)
        
    else:
        if socket in output:
            output.remove(socket)
        socket.close()


        
def response_header(sock, string, response):
    file_buf= re.search('GET /(.+?) HTTP/1.0', string)
    html_data = []
    name = ""
    if file_buf:
        file_name = file_buf.group(1)
        name = file_name
        try:
            file = open(file_name, "r")
        except FileNotFoundError:
            response[sock].put("HTTP/1.0 404 Not Found\r\n\r\n")
        else:
            response[sock].put("HTTP/1.0 200 OK\r\n\r\n")
    else:
        response[sock].put("HTTP/1.0 400 Bad Request\r\n\r\n")
    return name



def keep_alive(sock, string, response):
    if re.search("Connection:\sKeep-alive", string, re.IGNORECASE) or re.search("Connection:Keep-alive", string, re.IGNORECASE):
        response[sock].put("Connection: Keep-alive\r\n\r\n")
    elif string != '\n'and string != '\r\n':
        response[sock].put("Connection: Close\r\n\r\n")      

    
    
def html_file(sock, file_name, response):
    html_data = []
    try:
        file = open(file_name, "r")
    except FileNotFoundError:
        pass
    else: 
        lines = file.readlines()
        while lines:
            html_data.append(lines)
            lines = file.readlines()
    if html_data:
        for data in html_data:
            response[sock].put(data)
                        
                        

def socket_writer(socket, response, output, input_storage, request):
    keep_alive = 1
    try:
        message =response[socket].get_nowait()
    except queue.Empty:
        try:
            socket.gettimeout()
        except Socket.TimeoutError:
            socket.close()
        else:
            if keep_alive == 0:
                socket.close()
            output.remove(socket)
    else:
        if isinstance(message, str):
            if re.search("HTTP/1.0 4",message) or re.search("HTTP/1.0 2", message):
                log_print(socket, request, message)
            elif re.search("Connection: Close", message):
                input_storage.remove(socket)
            socket.send(message.encode())
        else:
            for lines in message:
                socket.send(lines.encode())
            
        
            
def log_print(socket, request, response):
    time_string = time.strftime("%a %d %b %H:%M:%S %Z %Y", time.gmtime())
    ip_address, port_num = socket.getpeername()
    buffer = str(request[socket].get())
    buffer = buffer.strip('\n')
    response = response.strip('\r\n')
    print(str(time_string)+": "+str(ip_address)+":"+str(port_num)+" "+buffer+"; "+str(response))


    
def main():
    if len(sys.argv) < 3:
        print("Use proper syntax:",sys.argv[0]," ip_address port_number")
        sys.exit(1)
    ip_add = sys.argv[1]
    port_num = int(sys.argv[2])
    open_simple_web_server(ip_add, port_num)

if __name__ == "__main__":
    main()
