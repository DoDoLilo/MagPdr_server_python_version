import threading
from enum import Enum
import math
import queue
import mag_mapping_tools as MMT

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


# 地磁定位线程，状态枚举类
class MagPositionState(Enum):
    INITIALIZING = 0  # 初始化状态：从BROKEN态转来，正处于初始固定区域遍历
    STABLE_RUNNING = 1  # 平稳运行状态：从INITIALIZING态转来，初始遍历成功，以此基础进行匹配定位
    STOP = 2  # 停止态：由STABLE_RUNNING转来，in_data_queue得到time=-1的主动结束标志


# 地磁定位 守护线程：检查公共数据容器中的数据，并根据数据进行状态转移、定位计算
# 初始态：清空历史数据，当容器中的数据量达到initial_dis则调用初始遍历算法
# 运行态：基于之前的transfer进行计算
class MagPositionThread(threading.Thread):
    def __init__(self, in_data_queue, out_data_queue, config_file_path):
        super(MagPositionThread, self).__init__()
        # 初始化各种参数
        self.state = MagPositionState.STOP
        self.in_data_queue = in_data_queue
        self.out_data_queue = out_data_queue
        self.config_file_path = config_file_path
        # TODO 从配置文件中读取各种参数，并赋予成员变量
        self.coordinate_offset = []  # move_x,move_y
        self.entrance_lsit = [[]]

        mag_map = MMT.rebuild_map_from_mvh_files(PATH_MAG_MAP)
        if mag_map is None:
            print("地磁指纹文件错误，初始化失败！")
            return
        self.mag_map = mag_map

    def run(self) -> None:
        self.mag_position_thread(self.in_data_queue, self.out_data_queue, self.coordinate_offset, self.entrance_lsit)

    # 输入：容器引用、地图坐标系参数（左下角、右上角坐标）、地图所有入口的坐标
    #    coordinate_offset，将entrance坐标平移到指纹库坐标系0-map_size_x, 0-map_size_y的move_x,move_y
    # 从in_data_queue中获取pdr_thread输出的 [time, [pdr_x, y], [10*[mag x, y, z]]]
    # 往out_data_list中放入[time, [mag_position_x,y]]
    def mag_position_thread(self, in_data_queue, out_data_queue, coordinate_offset, entrance_list) -> None:
        while True:
            # 根据不同的状态对该数据做对应的处理
            if self.state == MagPositionState.STOP:
                # 重新开始
                self.state = MagPositionState.INITIALIZING
                # 从数据输入流中取地足够初始遍历的数据。注意如果过程中遇到-1，则回到STOP状态
                inital_data_buffer = [in_data_queue.get()]
                distance = 0
                while distance < INITAIL_BUFFER_DIS:
                    last_data = inital_data_buffer[len(inital_data_buffer) - 1]
                    if last_data[0] == -1:
                        self.state = MagPositionState.STOP
                        break
                    cur_data = in_data_queue.get()
                    inital_data_buffer.append(cur_data)
                    distance += math.hypot(cur_data[1][0] - last_data[1][0], cur_data[1][1] - last_data[1][1])

                if self.state == MagPositionState.STOP:
                    continue
                # 先要将entrance_list坐标根据coordinate_offset映射到0-map_size_x, 0-map_size_y的坐标系下 → move_x, move_y
                for e in range(0, len(entrance_list)):
                    entrance_list[e][0] += coordinate_offset[0]
                    entrance_list[e][1] += coordinate_offset[1]

                # 初始化搜索成功，状态转移至稳定搜索阶段，*而pdr坐标，并不需要使用move xy!都会包含在transfer里面
                # 预处理pdr发送过来的数据，将[N][time, [pdr_x, y], [10*[mag x, y, z]]]变为[N][x,y, mv, mh]
                match_seq = MMT.change_pdr_thread_data_to_match_seq(inital_data_buffer)

                # 调用初始化固定区域搜索
                inital_transfer, inital_map_xy, inital_loss = MMT.inital_full_deep_search(
                    entrance_list, match_seq,
                    self.mag_map, BLOCK_SIZE,
                    STEP, MAX_ITERATION, UPPER_LIMIT_OF_GAUSSNEWTEON
                )

                # 将结果放入输出队列中，注意外部如果不及时取走结果，这一步可能（队列满）会阻塞，导致后续代码全部停止！
                out_data_queue.put(inital_map_xy)

                self.state = MagPositionState.STABLE_RUNNING
                continue
            if self.state == MagPositionState.STABLE_RUNNING:
                # 正在运行，从数据输入流中
                # TODO 基于 inital_transfer, inital_map_xy, inital_loss，
                #  按照上面的状态写法，写后续的匹配

                continue

        # TODO 当数据中出现“离开机房”的标记时，从“运行态”→“初始态”
        # 先要将room_coordinate\entrance_list坐标映射到0-map_size_x, 0-map_size_y的坐标系下 → move_x, move_y
        # 之后的坐标都需要先做move_x, move_y平移处理了
