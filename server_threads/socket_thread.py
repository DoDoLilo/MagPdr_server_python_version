import threading
import socket


# socket server 守护线程
# 往out_data_list中放入：time, acc, gyro, mag, ori

class SocketServerThread(threading.Thread):
    def __init__(self, out_data_queue, server_port=2212):
        super(SocketServerThread, self).__init__()
        self.out_data_queue = out_data_queue
        self.server_port = server_port

    def run(self) -> None:
        self.socket_server_thread()

    def socket_server_thread(self):
        # socket服务器端，一直在监听，同一时刻只允许连接一个socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('0.0.0.0', self.server_port))  # 监听端口
        s.listen()

        while True:
            print('Waiting for connection...')
            sock, addr = s.accept()
            # 建立socket连接，不开启子线程，因为同一时刻只允许连接一个socket
            self.socket_data_reciver(sock, addr)

        return

    def socket_data_reciver(self, sock, addr):
        print('Accept new connection from %s:%s...' % addr)
        socket_file = sock.makefile(mode='r')

        while True:
            try:
                line = socket_file.readline()
                # 数据为空行 or 接收到结束标记
                if line == '' or line == 'END':
                    break
                str_list = line.split(',')
                float_list = [int(str_list[0])]
                for s in str_list[1:]:
                    float_list.append(float(s))
                self.out_data_queue.put(float_list)
            except Exception as e:
                break

        # 不知什么原因结束的，都要放入结束标记
        self.out_data_queue.put('END')
        socket_file.close()
        sock.close()
        print('Connection closed.')
