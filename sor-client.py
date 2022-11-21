import socket
import select
import sys
import queue
import time
import re
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
