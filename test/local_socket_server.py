# 测试以127.0.0.1作为loopback能否实现
# 避免冲突，使用1w以上的端口号

import threading
import socket


class SocketServerThread(threading.Thread):
    def __init__(self, server_port):
        super(SocketServerThread, self).__init__()
        self.server_port = server_port

    def run(self) -> None:
        self.socket_server_thread()

    def socket_server_thread(self):
        # socket服务器端，一直在监听，同一时刻只允许连接一个socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('0.0.0.0', self.server_port))  # 监听端口
        s.listen()

        while True:
            print('Waiting for connection... Port =', self.server_port)
            sock, addr = s.accept()
            # 建立socket连接
            self.socket_data_reciver(sock, addr)
            # t = threading.Thread(target=self.socket_data_reciver, args=(sock, addr))
            # t.start()

        return

    def socket_data_reciver(self, sock, addr):
        # print('Accept new connection from %s:%s...' % addr)
        # socket_file = sock.makefile(mode='r')
        #
        # is_first_line = True
        # while True:
        #     try:
        #         line = socket_file.readline()
        #         # 数据为空，代表输入结束（Java中为null）
        #         if line == '':
        #             break
        #         if is_first_line:
        #             is_first_line = False
        #             self.user_phone = int(line)
        #             print("user phone = ", self.user_phone)
        #             continue
        #
        #         str_list = line.split(',')
        #         float_list = [int(str_list[0])]
        #         for s in str_list[1:]:
        #             float_list.append(float(s))
        #         print(float_list)
        #     except Exception as e:
        #         print(e)
        #         break
        #
        # # 不知什么原因结束的，都要放入结束标记
        # socket_file.close()
        # sock.close()
        # print('Connection closed.')

        print('Accept new connection from %s:%s...' % addr)
        socket_file = sock.makefile(mode='r')

        while True:
            try:
                line = socket_file.readline()
                # 数据为空，代表输入结束（Java中为null）
                if line == '':
                    break

                print(self.server_port, ':', line)
            except Exception as e:
                break

        # 不知什么原因结束的，都要放入结束标记
        socket_file.close()
        sock.close()
        print('Connection closed.')



if __name__ == '__main__':
    mag_position_server_port = 10000 + 1
    pdr_server_port = 10000 + 2
    SocketServerThread(mag_position_server_port).start()
    SocketServerThread(pdr_server_port).start()

    # server_port = 2212
    # SocketServerThread(server_port).start()


