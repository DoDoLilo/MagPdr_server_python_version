import math
import mag_mapping_tools as MMT
import numpy as np
import paint_tools as PT
import os

# -----------地图系统参数------------------
MOVE_X = 10.  # iLocator真值坐标平移参数（m）
MOVE_Y = 15.
MAP_SIZE_X = 70.  # 地图坐标系大小 0-MAP_SIZE_X ，0-MAP_SIZE_Y（m）
MAP_SIZE_Y = 28.
BLOCK_SIZE = 0.3  # 地图块大小，（m）
EMD_FILTER_LEVEL = 3  # 低通滤波的程度，值越大滤波越强。整型，无单位。
BUFFER_DIS = 5  # 缓冲池大小（m）
DOWN_SIP_DIS = BLOCK_SIZE  # 下采样粒度（m），应为块大小的整数倍？（下采样越小则相同长度序列的匹配点越多，匹配难度越大！）
# --------迭代搜索参数----------------------
SLIDE_STEP = 4  # 滑动窗口步长
SLIDE_BLOCK_SIZE = DOWN_SIP_DIS  # 滑动窗口最小粒度（m），最小应为下采样粒度！
MAX_ITERATION = 45  # 高斯牛顿最大迭代次数
TARGET_MEAN_LOSS = 20  # 目标损失
STEP = 1 / 50  # 迭代步长，牛顿高斯迭代是局部最优，步长要小
UPPER_LIMIT_OF_GAUSSNEWTEON = 20 * (MAX_ITERATION - 1)  # 当前参数下高斯牛顿迭代MAX_ITERATION的能降低的loss上限
# ---------其他参数----------------------------
PDR_IMU_ALIGN_SIZE = 10  # 1个PDR坐标对应的imu\iLocator数据个数，iLocator与imu已对齐
TRANSFERS_PRODUCE_CONFIG = [[0.265, 0.265, math.radians(1.8)],  # 枚举transfers的参数，[0] = [△x, △y(米), △angle(弧度)]
                            [5, 5, 7]]  # [1] = [枚举的正负个数]
ORIGINAL_START_TRANSFER = [0., 0., math.radians(0.)]  # 初始Transfer[△x, △y(米), △angle(弧度)]：先绕原坐标原点逆时针旋转，然后再平移
# PDR_IMU_START = 20  # PDR舍弃了所使用的IMU数据开头的一定数量的帧数
# ---------数据文件路径---------------------------
# PATH_PDR_RAW = [
#     "./data/XingHu hall 8F test/position_test/5/IMU-88-5-291.0963959547511 Pixel 6_sync.csv.npy",
#     "./data/XingHu hall 8F test/position_test/5/IMU-88-5-291.0963959547511 Pixel 6_sync.csv"]
# PATH_PDR_RAW = [
#     "./data/XingHu hall 8F test/position_test/6/IMU-88-6-194.9837361431375 Pixel 6_sync.csv.npy",
#     "./data/XingHu hall 8F test/position_test/6/IMU-88-6-194.9837361431375 Pixel 6_sync.csv"]
# PATH_PDR_RAW = [
#     "./data/XingHu hall 8F test/position_test/7/IMU-88-7-270.6518297687728 Pixel 6_sync.csv.npy",
#     "./data/XingHu hall 8F test/position_test/7/IMU-88-7-270.6518297687728 Pixel 6_sync.csv"]

PATH_PDR_RAW = [
    "./data/XingHu hall 8F test/position_test/8/IMU-88-8-189.88230883318997 Pixel 6_sync.csv.npy",
    "./data/XingHu hall 8F test/position_test/8/IMU-88-8-189.88230883318997 Pixel 6_sync.csv"]

# 地磁指纹库文件，[0]为mv.csv，[1]为mh.csv
PATH_MAG_MAP = [
    "./data/XingHu hall 8F test/mag_map/map_F1_2_B_0.3_full/mv_qiu_2d.csv",
    "./data/XingHu hall 8F test/mag_map/map_F1_2_B_0.3_full/mh_qiu_2d.csv"
]


def main():
    # 0.创建保存定位结果的文件夹
    result_dir_path = os.path.dirname(PATH_PDR_RAW[0]) + '/result_3'
    if not os.path.exists(result_dir_path):
        os.mkdir(result_dir_path)
    result_msg_file = open(result_dir_path + '/inf.txt', "w", encoding='GBK')
    paint_map_size = [0, MAP_SIZE_X * 1.0, 0, MAP_SIZE_Y * 1.0]

    print("MOVE_X = {0}\nMOVE_Y = {1}\nMAP_SIZE_X = {2}\nMAP_SIZE_Y = {3}\nBLOCK_SIZE = {4}\nEMD_FILTER_LEVEL = {5}\n"
          "BUFFER_DIS = {6}\nDOWN_SIP_DIS = {7}\nSLIDE_STEP = {8}\nSLIDE_BLOCK_SIZE = {9}\nMAX_ITERATION = {10}\n"
          "TARGET_MEAN_LOSS = {11}\nSTEP = {12}\nUPPER_LIMIT_OF_GAUSSNEWTEON = {13}\nPDR_IMU_ALIGN_SIZE = {14}\n"
          "TRANSFERS_PRODUCE_CONFIG = {15}\nORIGINAL_START_TRANSFER = {16}\n\n"
          "PATH_PDR_GT_IMU = {17}\nPATH_MAG_MAP = {18}\n\n".format(
        MOVE_X, MOVE_Y, MAP_SIZE_X, MAP_SIZE_Y, BLOCK_SIZE, EMD_FILTER_LEVEL,
        BUFFER_DIS, DOWN_SIP_DIS, SLIDE_STEP, SLIDE_BLOCK_SIZE, MAX_ITERATION,
        TARGET_MEAN_LOSS, STEP, UPPER_LIMIT_OF_GAUSSNEWTEON, PDR_IMU_ALIGN_SIZE,
        TRANSFERS_PRODUCE_CONFIG, ORIGINAL_START_TRANSFER,
        PATH_PDR_RAW, PATH_MAG_MAP
    ), file=result_msg_file)
    print("MOVE_X = {0}\nMOVE_Y = {1}\nMAP_SIZE_X = {2}\nMAP_SIZE_Y = {3}\nBLOCK_SIZE = {4}\nEMD_FILTER_LEVEL = {5}\n"
          "BUFFER_DIS = {6}\nDOWN_SIP_DIS = {7}\nSLIDE_STEP = {8}\nSLIDE_BLOCK_SIZE = {9}\nMAX_ITERATION = {10}\n"
          "TARGET_MEAN_LOSS = {11}\nSTEP = {12}\nUPPER_LIMIT_OF_GAUSSNEWTEON = {13}\nPDR_IMU_ALIGN_SIZE = {14}\n"
          "TRANSFERS_PRODUCE_CONFIG = {15}\nORIGINAL_START_TRANSFER = {16}\n\n"
          "PATH_PDR_GT_IMU = {17}\nPATH_MAG_MAP = {18}\n\n".format(
        MOVE_X, MOVE_Y, MAP_SIZE_X, MAP_SIZE_Y, BLOCK_SIZE, EMD_FILTER_LEVEL,
        BUFFER_DIS, DOWN_SIP_DIS, SLIDE_STEP, SLIDE_BLOCK_SIZE, MAX_ITERATION,
        TARGET_MEAN_LOSS, STEP, UPPER_LIMIT_OF_GAUSSNEWTEON, PDR_IMU_ALIGN_SIZE,
        TRANSFERS_PRODUCE_CONFIG, ORIGINAL_START_TRANSFER,
        PATH_PDR_RAW, PATH_MAG_MAP
    ))

    # 全流程
    # 1.建库
    # 读取提前建库的文件，并合并生成原地磁指纹地图mag_map
    mag_map = MMT.rebuild_map_from_mvh_files(PATH_MAG_MAP)
    if mag_map is None:
        print("Mag map rebuild failed!")
        print("Mag map rebuild failed!", file=result_msg_file)
        return
    PT.paint_heat_map(mag_map, save_dir=result_dir_path + '/')

    # 2、缓冲池给匹配段（内置稀疏采样），此阶段的data与上阶段无关
    pdr_xy = np.load(PATH_PDR_RAW[0])[:, 0:2]
    data_all = MMT.get_data_from_csv(PATH_PDR_RAW[1])
    # 将iLocator_xy\pdr_xy的坐标平移到MagMap中
    MMT.change_axis(pdr_xy, MOVE_X, MOVE_Y)
    PT.paint_xy_list([pdr_xy], ['PDR'], paint_map_size, ' ')
    data_mag = data_all[:, 21:24]
    data_quat = data_all[:, 7:11]

    match_seq_list, slide_number_list = MMT.samples_buffer_with_pdr_and_slidewindow(
        BUFFER_DIS, DOWN_SIP_DIS,
        data_quat, data_mag, pdr_xy,
        do_filter=True,
        lowpass_filter_level=EMD_FILTER_LEVEL,
        pdr_imu_align_size=PDR_IMU_ALIGN_SIZE,
        slide_step=SLIDE_STEP,
        slide_block_size=SLIDE_BLOCK_SIZE
    )  # match_seq_list：[?][?][x,y, mv, mh, PDRindex] (多条匹配序列)

    seq_num = len(match_seq_list)
    print("Match seq number:", seq_num, file=result_msg_file)
    print("Match seq number:", seq_num)

    if match_seq_list is None:
        print("Get match seq list failed!")
        print("Get match seq list failed!", file=result_msg_file)
        return

    # 3、迭代匹配段
    #  迭代结束情况：A：迭代out_of_map返回True；B：迭代次数超出阈值但last_loss仍未达标；C：迭代last_loss小于阈值。AB表示匹配失败
    #   3.1 给初始transfer
    transfer = ORIGINAL_START_TRANSFER

    #    3.2 基于初始匹配进行迭代
    map_xy_list = []
    for i in range(0, len(match_seq_list)):
        print("\nMatch Seq {0}/{1} :".format(i, seq_num))
        print("\nMatch Seq {0}/{1} :".format(i, seq_num), file=result_msg_file)
        match_seq = np.array(match_seq_list[i])  # 待匹配序列match_seq[N][x,y, mv, mh, PDRindex]
        start_transfer = transfer.copy()  # NOTE: Use copy() if just pointer copy caused unexpect data changed
        print("\tStart transfer:[{0:.5}, {1:.5}, {2:.5}°]"
              .format(start_transfer[0], start_transfer[1], math.degrees(start_transfer[2])))
        print("\tStart transfer:[{0:.5}, {1:.5}, {2:.5}°]"
              .format(start_transfer[0], start_transfer[1], math.degrees(start_transfer[2])), file=result_msg_file)
        # 1.核心循环搜索代码
        transfer, map_xy = MMT.produce_transfer_candidates_and_search(start_transfer, TRANSFERS_PRODUCE_CONFIG,
                                                                      match_seq, mag_map,
                                                                      BLOCK_SIZE, STEP, MAX_ITERATION,
                                                                      TARGET_MEAN_LOSS,
                                                                      UPPER_LIMIT_OF_GAUSSNEWTEON,
                                                                      MMT.SearchPattern.BREAKE_ADVANCED_BUT_USE_MIN_WHEN_FAILED)
        # 修改每个滑动窗口的实际生效坐标数量
        map_xy = map_xy[0: slide_number_list[i]]
        map_xy_list.append(map_xy)

        # 找到新的transfer
        if not np.array_equal(transfer, start_transfer):
            print("\tFound new transfer:[{0:.5}, {1:.5}, {2:.5}°]"
                  .format(transfer[0], transfer[1], math.degrees(transfer[2])))
            print("\tFound new transfer:[{0:.5}, {1:.5}, {2:.5}°]"
                  .format(transfer[0], transfer[1], math.degrees(transfer[2])), file=result_msg_file)

    # -----------4 计算结果参数------------------------------------------------------------------------------------------
    print("\n\n====================MagPDR End =============================================")
    # 4.1.png 将计算的分段mag xy合并还原为一整段 final_xy
    final_xy = []
    for map_xy in map_xy_list:
        for xy in map_xy:
            final_xy.append(xy)
    final_xy = np.array(final_xy)
    # 4.4 利用前面记录的初始变换向量start_transfer，将PDR xy转换至MagMap中，作为未经过较准的对照组
    pdr_xy = MMT.transfer_axis_of_xy_seq(pdr_xy, ORIGINAL_START_TRANSFER)

    # -----------5 输出结果参数------------------------------------------------------------------------------------------

    # 5.3 对Ground Truth(iLocator)、PDR、MagPDR进行绘图
    PT.paint_xy_list([pdr_xy], ["PDR"], paint_map_size, ' ', save_file=result_dir_path + '/PDR.png')
    PT.paint_xy_list([final_xy],
                     ['MagPDR'],
                     paint_map_size,
                     "The MagPDR: BlockSize={0}, BufferDis={1}, MaxIteration={2}, Step={3:.8f}, TargetLoss={4}"
                     .format(BLOCK_SIZE, BUFFER_DIS, MAX_ITERATION, STEP, TARGET_MEAN_LOSS),
                     save_file=result_dir_path + '/MagPDR.png')
    PT.paint_xy_list([pdr_xy, final_xy], ['PDR', 'MagPDR'], paint_map_size, "Contrast of Lines",
                     save_file=result_dir_path + '/PDR MagPDR.png')

    result_msg_file.close()
    return


if __name__ == '__main__':
    main()
