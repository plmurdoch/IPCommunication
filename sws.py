import socket
import select
import sys

def simple_web_server(ip_num, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ip_num, port)
    server.setblocking(0)
    server.listen(5)
    sockets = server
    
    
    
    
    




def main():
    if len(sys.argv) < 3:
        print("Use proper syntax:",sys.argv[0]," ip_address port_number")
        sys.exit(1)
    ip_addy = sys.argv[1]
    port_num = sys.argv[2]
    simple_web_server(ip_addy, port_num)
    
if __name__ == "__main__":
    main()
