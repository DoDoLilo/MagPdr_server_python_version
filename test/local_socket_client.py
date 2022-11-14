import socket
import time
import threading



def local_socket_client(msg, num):
    local_host = '127.0.0.1'
    local_port = 10000 + 1

    s = socket.socket()
    s.connect((local_host, local_port))
    s_file = s.makefile(mode='w')

    for i in range(0, num):
        s_file.write(str(i) + ':' + msg + '\n')
        s_file.flush()
        time.sleep(1)

    s_file.close()
    s.close()

if __name__ == '__main__':
    threading.Thread(target=local_socket_client, args=('local client 1', 10)).start()
    threading.Thread(target=local_socket_client, args=('local client 2', 10)).start()
