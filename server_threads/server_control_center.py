# 服务器线程控制中心:
# 声明公共数据容器，
# DI到 socket线程、pdr线程、magPdr线程，三个“守护线程”
# 并启动它们
from test_fake_threads.fake_pdr_thread import FakePdrThread
from server_threads.mag_position_thread import MagPositionThread
from test_fake_threads.fake_socket_thread import FakeSocketThread
from server_threads.pdr_thread import PdrThread
from mag_and_other_tools.config_tools import SystemConfigurations
import queue
import matplotlib.pyplot as plt
import numpy as np
import mag_and_other_tools.mag_mapping_tools as MMT
import test_tools as TEST
import mag_and_other_tools.paint_tools as PT
import os
import math
import time

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

# PATH_PDR_RAW = [
#     "D:\pythonProjects\MagPdr_server\data\InfCenter server room\position_test\\5\IMU-812-5-277.2496012617084 Pixel 6_sync.csv.npy",
#     "D:\pythonProjects\MagPdr_server\data\InfCenter server room\position_test\\5\IMU-812-5-277.2496012617084 Pixel 6_sync.csv"]

# PATH_PDR_RAW = [
#     "D:\pythonProjects\MagPdr_server\data\InfCenter server room\position_test\\6\IMU-812-6-269.09426660025395 Pixel 6_sync.csv.npy",
#     "D:\pythonProjects\MagPdr_server\data\InfCenter server room\position_test\\6\IMU-812-6-269.09426660025395 Pixel 6_sync.csv"]

PATH_PDR_RAW = [
    "D:\pythonProjects\MagPdr_server\data\InfCenter server room\position_test\\7\IMU-812-7-195.4948665194862 Pixel 6_sync.csv.npy",
    "D:\pythonProjects\MagPdr_server\data\InfCenter server room\position_test\\7\IMU-812-7-195.4948665194862 Pixel 6_sync.csv"]

# PATH_PDR_RAW = [
#     "D:\pythonProjects\MagPdr_server\data\InfCenter server room\position_test\\8\IMU-812-8-193.38120983931242 Pixel 6_sync.csv.npy",
#     "D:\pythonProjects\MagPdr_server\data\InfCenter server room\position_test\\8\IMU-812-8-193.38120983931242 Pixel 6_sync.csv"]

# PATH_PDR_RAW = [
#     "D:\pythonProjects\MagPdr_server\data\InfCenter server room\position_test\9\IMU-812-9-189.79622112889115 Pixel 6_sync.csv.npy",
#     "D:\pythonProjects\MagPdr_server\data\InfCenter server room\position_test\9\IMU-812-9-189.79622112889115 Pixel 6_sync.csv"]


def main():
    # 读取配置文件，将参数封装为配置对象，输入到各个thread对象中
    config_json_file = "./mag_position_config.json"
    configurations = SystemConfigurations(config_json_file)

    # 如果参数读取失败，直接不启动服务器，
    if not configurations.init_succeed:
        print("读取配置文件初始化参数失败！停止启动服务器程序，请检查")
        # TODO 所有的print要改成打包后的软件使用时可以显示的
        return

    MAP_SIZE_X = configurations.MapSizeX
    MAP_SIZE_Y = configurations.MapSizeY
    MOVE_X = configurations.MoveX
    MOVE_Y = configurations.MoveY

    socket_output_queue = queue.Queue()

    pdr_input_queue = socket_output_queue
    pdr_output_queue = queue.Queue()

    mag_position_input_queue = pdr_output_queue
    mag_position_output_queue = queue.Queue()

    # 定义线程
    fake_socket_thread = FakeSocketThread(PATH_PDR_RAW[1], socket_output_queue)
    pdr_thread = PdrThread(pdr_input_queue, pdr_output_queue, configurations)
    # pdr_thread = FakePdrThread(pdr_input_queue, pdr_output_queue, PATH_PDR_RAW)
    mag_position_thread = MagPositionThread(mag_position_input_queue, mag_position_output_queue,
                                            configurations)
    # 启动线程
    start_time = time.time()

    fake_socket_thread.start()
    pdr_thread.start()
    mag_position_thread.start()

    # 实时绘制结果图片
    final_xy = []
    final_xy.extend(mag_position_output_queue.get())
    xy_range = [0, MAP_SIZE_X * 1, 0, MAP_SIZE_Y * 1]
    plt.figure(num=1, figsize=((xy_range[1] - xy_range[0]) / 4, (xy_range[3] - xy_range[2]) / 4))
    while True:
        plt.xlim(xy_range[0], xy_range[1])
        plt.ylim(xy_range[2], xy_range[3])
        xy_arr = np.array(final_xy)
        plt.plot(xy_arr[:, 0], xy_arr[:, 1])
        plt.pause(0.5)
        cur_data = mag_position_output_queue.get()
        if isinstance(cur_data, str) and cur_data == 'END':
            break
        final_xy.extend(cur_data)
        plt.ioff()
        plt.clf()

    end_time = time.time()

    # 计算性能参数-------------------------------------------------------------------------------------------------------
    print('\n')
    final_index = mag_position_output_queue.get()[:, np.newaxis]

    pdr_xy = np.load(PATH_PDR_RAW[0])[:, 0:2]
    data_all = MMT.get_data_from_csv(PATH_PDR_RAW[1])
    gt_xy = data_all[:, np.shape(data_all)[1] - 5:np.shape(data_all)[1] - 3]
    magPDR_xy = np.concatenate((final_xy, final_index), axis=1)

    MMT.change_axis(gt_xy, MOVE_X, MOVE_Y)
    MMT.change_axis(pdr_xy, MOVE_X, MOVE_Y)

    distance_of_PDR_iLocator_points = TEST.cal_distance_between_GT_and_PDR(
        gt_xy, pdr_xy, xy_align_size=10)
    distance_of_MagPDR_iLocator_points = TEST.cal_distance_between_GT_and_MagPDR(
        gt_xy, magPDR_xy, xy_align_size=10)
    mean_distance = np.mean(distance_of_PDR_iLocator_points[:, 0])
    print("\tMean Distance between PDR and GT: ", mean_distance)
    mean_distance = np.mean(distance_of_MagPDR_iLocator_points[:, 0])
    print("\tMean Distance between MagPDR and GT: ", mean_distance)

    PT.paint_xy_list([gt_xy, pdr_xy], ['GT', 'PDR'], xy_range, 'Contrast of Lines')
    PT.paint_xy_list([gt_xy, magPDR_xy], ['GT', 'MagPDR'], xy_range, "Contrast of Lines")
    PT.paint_xy_list([gt_xy, pdr_xy, magPDR_xy], ['GT', 'PDR', 'MagPDR'], xy_range, "Contrast of Lines")

    total_distance = 0
    for i in range(1, len(pdr_xy)):
        total_distance += math.hypot(pdr_xy[i][0] - pdr_xy[i - 1][0], pdr_xy[i][1] - pdr_xy[i - 1][1])

    print('\tTotal Distance: ', total_distance)
    print('\tCost time: ', end_time - start_time)

    return


if __name__ == '__main__':
    main()
