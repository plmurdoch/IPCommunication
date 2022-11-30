import socket
import select
import sys
import queue
import time
import re


#Simple web server with limited time out capabilities
#open_simple_web_server binds the server to the port and ip address
def open_simple_web_server(ip_num, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Setting Socket
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #Allowing for reuse of socket address
    server.setblocking(0) #Non-blocking to allow for multiple connections
    server_address = (ip_num, port) 
    server.bind(server_address)
    server.listen(5) 
    listen_for_sockets(server) 


#Listen for sockets undergoes select process to find readable, writable and exceptionals
def listen_for_sockets(s):
    input_storage = [s] #input storage array
    output = [] #output storage array 
    response_messages = {} #queue for responses
    request_message = {} #queue for request message
    while input_storage: #get select based of inputs 
        readable, writable, exceptional = select.select(input_storage, output, input_storage) 
        for sock in readable: #Search through readable sockets
            if sock is s:
                new_connection(sock, input_storage, response_messages, request_message) #if server pass to new connection
            else:
                socket_reader(sock, input_storage, response_messages, output, request_message) #if connected pass to reader
        for sock in writable: #Search through writable sockets
            socket_writer(sock, response_messages, output,input_storage, request_message)
        for sock in exceptional: #Search through exceptions
            input_storage.remove(sock)
            if sock in output:
                output.remove(sock)
            sock.close() #Close socket!
            del response_messages[sock]
            del request_message[sock]


#if the socket is the server, accept the new connection and set timeout.
def new_connection(socket, inp, response, request):
    connect, address = socket.accept() #Accept connection
    connect.setblocking(0) #Set blocking to 0
    inp.append(connect) #append to input array 
    response[connect] = queue.Queue() #Create queue corresponding socket id in response_messages
    request[connect] = queue.Queue() #Creat queue corresponding socekt id in request_messages
    connect.settimeout(60)
    
#Reader which takes command line inputs from socket connection
def socket_reader(socket, input_storage, response_messages, output, request_message):
    message = socket.recv(1024) #Recieve data from socket
    if re.search(br'\r\n\r\n', message) or re.search(br'\n\n', message): #check if multi line input
        full_input = message.decode() 
        split = full_input.splitlines(True)
        request_list = []
        for lines in split: #loop to remove unneeded new lines
            if lines != '\n' and lines !='\r\n': 
                request_list.append(lines)
        i = 0
        while i in range(len(request_list)-1): #While loop to examine 2 inputs at a time
            j = i+1
            file_ex = response_header(socket, request_list[i], response_messages)
            if file_ex:
                if re.search("Connection:\sKeep-alive", request_list[j], re.IGNORECASE) or re.search("Connection:Keep-alive", request_list[j], re.IGNORECASE):
                    request_message[socket].put(request_list[i])
                    keep_alive(socket, request_list[j],response_messages, 0)
                    html_file(socket, str(file_ex), response_messages)
                    i = i+2
                else:
                    request_message[socket].put(request_list[i])
                    response_messages[socket].put("Connection: Close\r\n\r\n")
                    html_file(socket, str(file_ex), response_messages)
                    break
            else:
                request_message[socket].put(request_list[i])
                response_messages[socket].put("Connection: Close\r\n\r\n")
                break
        if i == range(len(request_list)-2):
            i = i + 1
            file_ex = response_header(socket, request_list[i], response_messages)
            if file_ex:
                request_message[socket].put(request_list[i])
                response_messages[socket].put("Connection: Close\r\n\r\n")
                html_file(socket, str(file_ex), response_messages)
            else:
                request_message[socket].put(request_list[i])
                response_messages[socket].put("Connection: Close\r\n\r\n")
        if socket not in output:
            output.append(socket)
    elif message:
        request = []
        file_exist = ""
        keep_count = 0
        queue_for_break = 0
        while message:
            request.append(message.decode())
            if request[len(request)-1] == '\r\n' and  re.search(r'\r\n',request[len(request)-2]):
                queue_for_break = 1
            elif request[len(request)-1] == '\n' and re.search(r'\n',request[len(request)-2]):
                queue_for_break = 1
            if keep_count == 0:
                file_exist = response_header(socket, message.decode(), response_messages)
                keep_count = 1
                request_message[socket].put(message.decode())
                if not file_exist and queue_for_break == 0:
                    response_messages[socket].put("Connection: Close\r\n\r\n")  
                    break
            elif keep_count == 1:
                keep_alive(socket, message.decode(), response_messages, queue_for_break)
                html_file(socket, file_exist, response_messages)
                file_exist = ""
                keep_count = 2
            if queue_for_break == 1:
                break
            else:
                message = socket.recv(1024)
        if socket not in output:
            output.append(socket)
        
    else:
        if socket in output:
            output.remove(socket)
        socket.close()


#Response with appropriate header        
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


#Keep socket alive or not
def keep_alive(sock, string, response, for_break):
    if re.search("Connection:\sKeep-alive", string, re.IGNORECASE) or re.search("Connection:Keep-alive", string, re.IGNORECASE):
        response[sock].put("Connection: Keep-alive\r\n\r\n")
    elif string != '\n'and string != '\r\n':
        response[sock].put("Connection: Close\r\n\r\n")
    elif string == '\n'or string == '\r\n' and for_break == 1:
        response[sock].put("Connection: Close\r\n\r\n")

    
#If there is file data send back to server
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
                        
                        
#write all the stored info back to server
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
            
        
#print log in server
def log_print(socket, request, response):
    
    time_string = time.strftime("%a %d %b %H:%M:%S %Z %Y", time.localtime())
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
