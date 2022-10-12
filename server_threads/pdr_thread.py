import threading
import enum


class PdrState(enum.Enum):
    STOP = 0  # 初始状态，置Px,Py = 0, 0，清空window_buffer
    RUNNING = 1  # 运行状态，当接收到time = -1时，转换置STOP状态


class PdrThread(threading.Thread):

    def __init__(self, in_data_queue, out_data_queue):
        super(PdrThread, self).__init__()
        self.in_data_queue = in_data_queue
        self.out_data_queue = out_data_queue
        self.window_size = 200
        self.slide_size = 10
        self.state = PdrState.STOP

    def run(self) -> None:
        self.pdr_thread()

    # 接收从socket线程发送过来的数据 time, acc_xyz, gyro_xyz, mag_xyz, gamerotaion_xyzw
    # 滑动窗口大小 = 200，滑动距离 = 10
    # 如果接收到的time = -1，则清空坐标Px,Py，重新计算
    # 模型返回的是Vx,Vy，需要外部记录时间戳进行位置Px,Py计算
    def pdr_thread(self) -> None:
        window_buffer = []
        px, py = 0, 0
        window_size = 200
        slide_size = 10

        while True:
            if self.state == PdrState.STOP:
                window_buffer = []
                px, py = 0, 0
                # 接收 window_size 个数据，过程中遇到 time = -1则继续
                succeed = True
                for i in range(0, window_size):
                    cur_data = self.in_data_queue.get()
                    if cur_data[0] == -1:
                        succeed = False
                        break
                    else:
                        window_buffer.append(cur_data)

                # 成功接收满一个window的数据，则进入到运行态
                if succeed:
                    self.state = PdrState.RUNNING
                continue

            if self.state == PdrState.RUNNING:
                # TODO 调用模型计算window_buffer数据的输出Vx,Vy，
                #  ΔT = (window_buffer.time[slide_size] - window_buffer.time[0]) / 1000  因为time是ms
                #  Px,Py = Vx * ΔT, Vy * ΔT
                #  将结果放入out_data_queue中

                # 继续接收 slide_size 个数据，过程中遇到 time = -1，不仅要转换状态，还要往out_data_queue中放入-1让后续线程知晓
                del window_buffer[0: slide_size]  # 删除开头，滑动窗口
                for i in range(0, slide_size):
                    cur_data = self.in_data_queue.get()
                    if cur_data[0] == -1:
                        self.state = PdrState.STOP
                        break
                    else:
                        window_buffer.append(cur_data)
                continue
