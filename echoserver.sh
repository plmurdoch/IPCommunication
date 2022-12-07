mkfifo fifo
cat fifo | nc -u -l 8888 > fifo