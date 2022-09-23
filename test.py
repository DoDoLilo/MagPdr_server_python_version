import numpy as np
import json
import math

# -----------地图系统参数------------------
MAP_SIZE_X = 70.  # 地图坐标系大小 0-MAP_SIZE_X ，0-MAP_SIZE_Y（m）
MAP_SIZE_Y = 28.
BLOCK_SIZE = 0.3  # 地图块大小（m），必须和使用的指纹库文件建库时的块大小一致
EMD_FILTER_LEVEL = 3  # 低通滤波的程度，值越大滤波越强。整型，无单位。
INITAIL_BUFFER_DIS = 6  # 初始态匹配时，缓存池大小（m）
BUFFER_DIS = 5  # 稳定态匹配时，缓冲池大小（m）
DOWN_SIP_DIS = BLOCK_SIZE  # 下采样粒度（m），应为块大小的整数倍？（下采样越小则相同长度序列的匹配点越多，匹配难度越大！）
# --------迭代搜索参数----------------------
SLIDE_STEP = 4  # 滑动窗口步长
SLIDE_BLOCK_SIZE = DOWN_SIP_DIS  # 滑动窗口最小粒度（m），>=下采样粒度！
MAX_ITERATION = 45  # 高斯牛顿最大迭代次数
TARGET_MEAN_LOSS = 13  # 目标损失
STEP = 1 / 25  # 迭代步长，牛顿高斯迭代是局部最优，步长要小
UPPER_LIMIT_OF_GAUSSNEWTEON = 20 * (MAX_ITERATION - 1)  # 当前参数下高斯牛顿迭代MAX_ITERATION的能降低的loss上限
# ---------其他参数----------------------------
PDR_IMU_ALIGN_SIZE = 10  # 1个PDR坐标对应的imu\iLocator数据个数，iLocator与imu已对齐
TRANSFERS_PRODUCE_CONFIG = [[0.265, 0.265, math.radians(1.8)],  # 枚举transfers的参数，[0] = [△x, △y(米), △angle(弧度)]
                            [5, 5, 7]]  # [1] = [枚举的正负个数]
ORIGINAL_START_TRANSFER = [0., 0., math.radians(0.)]  # 初始Transfer[△x, △y(米), △angle(弧度)]：先绕原坐标原点逆时针旋转，然后再平移
# ---------数据文件路径---------------------------
# 地磁指纹库文件，[0]为mv.csv，[1]为mh.csv
PATH_MAG_MAP = [
    "./data/XingHu hall 8F test/mag_map/map_F1_2_B_0.3_full/mv_qiu_2d.csv",
    "./data/XingHu hall 8F test/mag_map/map_F1_2_B_0.3_full/mh_qiu_2d.csv"
]

# 将这些参数保存到json文件中
config_file_path = "D:\pythonProjects\MagPdr_server\server_threads\mag_position_config.json"

