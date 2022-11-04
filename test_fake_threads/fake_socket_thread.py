import threading
import mag_and_other_tools.mag_mapping_tools as MMT
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
        len_imu_data = len(imu_data)

        for start_i in range(0, len_imu_data, 200):
            time.sleep(1)
            end_i = start_i + 200
            end_i = len_imu_data if end_i > len_imu_data else end_i
            # 放入[time, acc, gyro, mag, ori]
            for line in imu_data[start_i:end_i, :]:
                self.out_data_queue.put([line[0],
                                         line[1], line[2], line[3],
                                         line[4], line[5], line[6],
                                         line[21], line[22], line[23],
                                         line[7], line[8], line[9], line[10]])
        self.out_data_queue.put('END')
        return
