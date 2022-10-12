# 服务器线程控制中心:
# 声明公共数据容器，
# DI到 socket线程、pdr线程、magPdr线程，三个“守护线程”
# 并启动它们
from server_threads.fake_pdr_thread import FakePdrThread
from server_threads.mag_position_thread import MagPositionThread
import queue
import matplotlib.pyplot as plt
import numpy as np
import mag_mapping_tools as MMT
import test_tools as TEST
import paint_tools as PT

MAP_SIZE_X = 70.  # 地图坐标系大小 0-MAP_SIZE_X ，0-MAP_SIZE_Y（m）
MAP_SIZE_Y = 28.
MOVE_X = 10.
MOVE_Y = 15.

# PATH_PDR_RAW = [
#     "D:\pythonProjects\MagPdr_server\data/XingHu hall 8F test/position_test/5/IMU-88-5-291.0963959547511 Pixel 6_sync.csv.npy",
#     "D:\pythonProjects\MagPdr_server\data/XingHu hall 8F test/position_test/5/IMU-88-5-291.0963959547511 Pixel 6_sync.csv"]
#
PATH_PDR_RAW = [
    "D:\pythonProjects\MagPdr_server\data\XingHu hall 8F test\position_test/6\IMU-88-6-194.9837361431375 Pixel 6_sync.csv.npy",
    "D:\pythonProjects\MagPdr_server\data\XingHu hall 8F test\position_test/6\IMU-88-6-194.9837361431375 Pixel 6_sync.csv"]

# PATH_PDR_RAW = [
#     "D:\pythonProjects\MagPdr_server\data\XingHu hall 8F test\position_test\\7\IMU-88-7-270.6518297687728 Pixel 6_sync.csv.npy",
#     "D:\pythonProjects\MagPdr_server\data\XingHu hall 8F test\position_test\\7\IMU-88-7-270.6518297687728 Pixel 6_sync.csv"]

# PATH_PDR_RAW = [
#     "D:\pythonProjects\MagPdr_server\data\XingHu hall 8F test\position_test\8\IMU-88-8-189.88230883318997 Pixel 6_sync.csv.npy",
#     "D:\pythonProjects\MagPdr_server\data\XingHu hall 8F test\position_test\8\IMU-88-8-189.88230883318997 Pixel 6_sync.csv"]

def main():
    socket_output_queue = queue.Queue()

    pdr_input_queue = socket_output_queue
    pdr_output_queue = queue.Queue()

    mag_position_input_queue = pdr_output_queue
    mag_position_output_queue = queue.Queue()
    mag_position_config_file = "D:\pythonProjects\MagPdr_server\server_threads\mag_position_config.json"

    # 定义线程
    pdr_thread = FakePdrThread(pdr_input_queue, pdr_output_queue, PATH_PDR_RAW)
    mag_position_thread = MagPositionThread(mag_position_input_queue, mag_position_output_queue,
                                            mag_position_config_file)
    # 启动线程
    pdr_thread.start()
    mag_position_thread.start()

    # 实时绘制结果图片
    final_xy = []
    final_xy.extend(mag_position_output_queue.get())
    xy_range = [0, MAP_SIZE_X * 1, 0, MAP_SIZE_Y * 1]
    plt.figure(num=1, figsize=((xy_range[1] - xy_range[0]) / 5, (xy_range[3] - xy_range[2]) / 5))
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

    # 计算性能参数
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

    return


if __name__ == '__main__':
    main()
