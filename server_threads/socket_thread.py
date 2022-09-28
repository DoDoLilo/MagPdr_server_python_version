import threading

# socket server 守护线程
# 往out_data_list中放入：time, acc, gyro, mag, ori

class SocketServerThread(threading.Thread):
    def __init__(self, out_data_queue):
        super(SocketServerThread, self).__init__()
        self.out_data_queue = out_data_queue

    def run(self) -> None:
        self.socket_server_thread(self.out_data_queue)

    def socket_server_thread(self, out_data_queue):
        return