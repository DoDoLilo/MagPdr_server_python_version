import numpy as np
import mag_mapping_tools as MMT
import time
import threading

PDR_IMU_ALIGN_SIZE = 10  # 1个PDR坐标对应的imu数据个数


class PdrThread(threading.Thread):

    def __init__(self, in_data_queue, out_data_queue):
        super(PdrThread, self).__init__()
        self.in_data_queue = in_data_queue
        self.out_data_queue = out_data_queue

    def run(self) -> None:
        self.pdr_thread(self.in_data_queue, self.out_data_queue)

    # 以线程的方式模拟PDR线程：time, pdr_xy, mag_vector
    # 公共容器data_container，从文件中读取数据， 每隔1s向里面存入20个pdr_xy、对齐后的20个mag 数据
    # 从in_data_queue中获取:time, acc, gyro, mag, ori
    # 往out_data_queue中放入:[time, [pdr_x, y], [10*[mag x, y, z, quat x, y, z, w]]]
    # TODO 当socket thread端接收到'END'并发送标记过来 or imu数据的两次time间隔超过阈值，
    #  则pdr thread往out data queue中置入[-1, [],[]]以通知mag thread
    def pdr_thread(self, in_data_queue, out_data_queue) -> None:
        # 由PDR线程实现对齐，目前先用文件载入进行
        PATH_PDR_RAW = [
            "D:\pythonProjects\MagPdr_server\data\XingHu hall 8F test\position_test\\5\IMU-88-5-291.0963959547511 Pixel 6_sync.csv.npy",
            "D:\pythonProjects\MagPdr_server\data\XingHu hall 8F test\position_test\\5\IMU-88-5-291.0963959547511 Pixel 6_sync.csv"]

        # 载入数据
        pdr_xy = np.load(PATH_PDR_RAW[0])[:, 0:2]
        imu_data = MMT.get_data_from_csv(PATH_PDR_RAW[1])

        num = 20
        for pdr_index in range(0, len(pdr_xy), num):
            time.sleep(1)
            for offset in range(0, num):
                # 每隔1s向里面存入20个pdr_xy、20*10个mag+quat数据，所以不需要time去对齐pdr_xy与imu数据，time只是一个信息
                imu_index = (pdr_index + offset) * PDR_IMU_ALIGN_SIZE
                # [time, [pdr_xy], [10 * mag]] = (1, 2, (10, 3+4))
                mag_quat_list = []
                for i in range(imu_index, imu_index + PDR_IMU_ALIGN_SIZE):
                    mag_quat_list.append([imu_data[i][21], imu_data[i][22], imu_data[i][23],
                                          imu_data[i][7], imu_data[i][8], imu_data[i][9], imu_data[i][10]])

                index = pdr_index + offset
                if index >= len(pdr_xy):
                    break

                out_data_queue.put([imu_data[imu_index][0],
                                    [pdr_xy[index][0], pdr_xy[index][1]],
                                    mag_quat_list])
