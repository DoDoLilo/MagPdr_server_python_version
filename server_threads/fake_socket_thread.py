import threading
import mag_mapping_tools as MMT
import time

# 模拟socket线程，每1s发送200行的数据
# 读取IMU文件，发送数据 time, acc_xyz, gyro_xyz, mag_xyz, gamerotaion_xyzw 到后续线程
class FakeSocketThread(threading.Thread):
    def __init__(self, imu_file_path, out_data_queue):
        super(FakeSocketThread, self).__init__()
        self.imu_file_path = imu_file_path
        self.out_data_queue = out_data_queue

    def run(self) -> None:
        self.read_and_sent_data()
        return

    def read_and_sent_data(self) -> None:
        imu_data = MMT.get_data_from_csv(self.imu_file_path)
        len = len(imu_data)

        for start_i in range(0, len, 200):
            time.sleep(1)
            end_i = start_i + 200
            end_i = len if end_i > len else end_i
            self.out_data_queue.put(imu_data[start_i:end_i, :])  # 获得的是子视图，外部修改等同于修改原数组

        return
