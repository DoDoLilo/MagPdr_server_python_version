import threading
import socket
from mag_and_other_tools.config_tools import SystemConfigurations


# socket server 守护线程
# 往out_data_list中放入：time, acc, gyro, mag, ori
# TODO 如何解决 连上客户端后，客户端与网络断开(客户端自己会知晓，然后不断重复连接)，但本服务端却无法知晓，该socket连接仍占用着
class SocketServerThread(threading.Thread):
    def __init__(self, out_data_queue, configurations):
        super(SocketServerThread, self).__init__()
        self.out_data_queue = out_data_queue
        self.server_port = configurations.ServerPort
        self.user_phone = None

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
            # t = threading.Thread(target=self.socket_data_reciver, args=(sock, addr))
            # t.start()

        return

    def socket_data_reciver(self, sock, addr):
        print('Accept new connection from %s:%s...' % addr)
        socket_file = sock.makefile(mode='r')

        is_first_line = True
        while True:
            try:
                line = socket_file.readline()
                # 数据为空，代表输入结束（Java中为null）
                if line == '':
                    break
                if is_first_line:
                    is_first_line = False
                    self.user_phone = line
                    continue

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

