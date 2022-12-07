import pexpect
import socket
import re
import sys
import time
import os


grade = 0
#Clear tc rules
delaycloseprocess = pexpect.spawn('/bin/bash -c "sudo ip netns exec r tc qdisc del dev r-eth0 root netem delay 100ms 20ms distribution normal"',timeout=3)
losscloseprocess = pexpect.spawn('/bin/bash -c "sudo ip netns exec r tc qdisc del dev r-eth0 root netem loss 25%"',timeout=3)
delaycloseprocess.close(force=True)
losscloseprocess.close(force=True)
#run the echo server on h2 without timeout and packet loss
echoserver = pexpect.spawn('/bin/bash -c "sudo ip netns exec h2 ./echoserver.sh"',timeout=3)
time.sleep(1)

#Use tcpdump on r to identify whether there are packets transmitted between h1 and h2
#tcpdumprocess = pexpect.spawn('/bin/bash -c "sudo ip netns exec r tcpdump -n -l -i r-eth1"',timeout=3)


#small file transmission on h1
rdpprocess1 = pexpect.spawn('/bin/bash -c "sudo ip netns exec h1 python3 rdp.py 192.168.1.100 6789 small.html smalltest.html" ')
time.sleep(3)


#Handle small file which is less than 1024bytes, save received packets to a new file, making sure they are identical, check the consistency by using 'dif read_file_name write_file_name' (2 points)
#Handle large file which is larger than 1024bytes, save received packets to a new file, making sure they are identical, check the consistency by using 'dif read_file_name write_file_name' (3 points)
#Print the right log information as required in the p2 spec for both small and large file (2 points, where 1 point for the small file log and 1 for the large file log)

#Observe the log is correct or not
rdpprocess1.expect_exact([pexpect.EOF, pexpect.TIMEOUT])
print("The log for the small file transmission")
print(rdpprocess1.before.decode())
grade_small_log = input("Please give the grade on the log of small file: 4.5 points (3 points for connection management (SYN,FIN), and 1.5 points for log format\n")
grade_small_log = float(grade_small_log)
if grade_small_log>=0 and grade_small_log<=4.5:
    print("Grading successfully, please write comments on Connex about this grade")
    print("Continue Marking...Do not input anything until further notification")
    grade = grade + grade_small_log
else:
    grade_small_log = input("Wrong input!Please give the grade on the log of small file (maximum 4.5 point)\n")
    grade_small_log = int(grade_small_log)
#compare received files
if(os.path.exists("smalltest.html")):
    diffprocess1 = pexpect.spawn('/bin/bash -c "diff small.html smalltest.html"')
    diffprocess1.expect_exact([pexpect.EOF, pexpect.TIMEOUT])
    if (diffprocess1.before == b''):
        print("The file is transmitted successfully and correctly")
        grade = grade + 1.5 #According to the marking break, if small file is transmitted correctly, 2 points are received.
    else:
        print("The trasmitted small file content is not consistent with the orinal one: -2 points. The error information:")
        print(diffprocess1.before)
else:
    print("The small file cannot be transmitted (no transmitted file exists): -2 points")

os.remove("smalltest.html")
diffprocess1.close(force=True)
rdpprocess1.close(force=True)


rdpprocess2 = pexpect.spawn('/bin/bash -c "sudo ip netns exec h1 python3 rdp.py 192.168.1.100 6789 large.html largetest.html" ')
time.sleep(3)
#Observe the log is correct or not
rdpprocess2.expect_exact([pexpect.EOF, pexpect.TIMEOUT])
print("The log for the large file transmission")
print(rdpprocess2.before.decode())
grade_large_log = input("Please give the grade on the log of large file: 3 points (3 points for flow control)\n")
grade_large_log = float(grade_large_log)
if grade_large_log>=0 and grade_large_log<=3:
    print("Grading successfully, please write comments on Connex about this grade.")
    print("Continue Marking...Do not input anything until further notification")
    grade = grade + grade_large_log
else:
    grade_large_log = input("Wrong input! Please give the grade on the log of large file (maximum 3 point)\n")
    grade_large_log = int(grade_large_log)
if(os.path.exists("largetest.html")):
    diffprocess2 = pexpect.spawn('/bin/bash -c "diff large.html largetest.html"')
    diffprocess2.expect_exact([pexpect.EOF, pexpect.TIMEOUT])
    if (diffprocess2.before == b''):
        print("The file is transmitted successfully and correctly")
        grade = grade + 3 #According to the marking break, if large file is transmitted correctly, 3 points are received.
    else:
        print("The trasmitted large file content is not consistent with the orinal one: -3 points. The error information")
        print(diffprocess2.before)
else:
    print("The large file cannot be transmitted (no transmitted file exists): -3 points")
os.remove("largetest.html")
diffprocess2.close(force=True)
rdpprocess2.close(force=True)

#packet loss test 3 points in total
echoserver = pexpect.spawn('/bin/bash -c "sudo ip netns exec h2 ./echoserver.sh"',timeout=3)
lossopenprocess = pexpect.spawn('/bin/bash -c "sudo ip netns exec r tc qdisc add dev r-eth0 root netem loss 25%"',timeout=3)
time.sleep(1)
rdpprocess4 = pexpect.spawn('/bin/bash -c "sudo ip netns exec h1 python3 rdp.py 192.168.1.100 6789 large.html largetest.html" ')
time.sleep(3)
rdpprocess4.expect_exact([pexpect.EOF, pexpect.TIMEOUT])
print("The log for the fast transmission (timeout case)")
print(rdpprocess4.before.decode())
grade_fastretr_log = input("Please give the grade on the log of retransmissions: 3 points\n")
grade_fastretr_log = float(grade_fastretr_log)
if grade_fastretr_log>=0 and grade_fastretr_log<=3:
    print("Grading successfully, please write comments on Connex about this grade")
    print("Continue Marking...Do not input anything until further notification")
    grade = grade + grade_fastretr_log
else:
    grade_fastretr_log = input("Wrong input!Please give the log of retransmission: 3 points\n")
    grade_fastretr_log = int(grade_fastretr_log)
#compare received files
if(os.path.exists("largetest.html")):
    diffprocess4 = pexpect.spawn('/bin/bash -c "diff large.html largetest.html"')
    diffprocess4.expect_exact([pexpect.EOF, pexpect.TIMEOUT])
    if (diffprocess4.before == b''):
        print("The file is transmitted successfully and correctly")
        grade = grade + 0
    else:
        grade = grade - grade_fastretr_log
        print("Timeout retransmission test failed! The trasmitted file content is not consistent with the orinal one: -1 point. The error information:")
        print(diffprocess4.before)
else:
    print("Timeout retransmission test failed! The file cannot be transmitted (no transmitted file exists): -1 point")

os.remove("largetest.html")

losscloseprocess = pexpect.spawn('/bin/bash -c "sudo ip netns exec r tc qdisc del dev r-eth0 root netem loss 25%"',timeout=3)
lossopenprocess.close(force=True)
losscloseprocess.close(force=True)
echoserver.close(force=True)
print("")
print("Final grades")
print(grade)