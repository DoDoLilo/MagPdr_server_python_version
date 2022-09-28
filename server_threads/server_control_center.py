# 服务器线程控制中心:
# 声明公共数据容器，
# DI到 socket线程、pdr线程、magPdr线程，三个“守护线程”
# 并启动它们
from server_threads.pdr_thread import PdrThread
from server_threads.mag_position_thread import MagPositionThread
from server_threads.fake_ui_thread import FakeUiThread
import queue

MAP_SIZE_X = 70.  # 地图坐标系大小 0-MAP_SIZE_X ，0-MAP_SIZE_Y（m）
MAP_SIZE_Y = 28.


def main():
    socket_output_queue = queue.Queue()

    pdr_input_queue = socket_output_queue
    pdr_output_queue = queue.Queue()

    mag_position_input_queue = pdr_output_queue
    mag_position_output_queue = queue.Queue()
    mag_position_config_file = "D:\pythonProjects\MagPdr_server\server_threads\mag_position_config.json"

    fake_ui_input_queue = mag_position_output_queue

    # try:
    pdr_thread = PdrThread(pdr_input_queue, pdr_output_queue)
    mag_position_thread = MagPositionThread(mag_position_input_queue, mag_position_output_queue,
                                            mag_position_config_file)
    fake_ui_thread = FakeUiThread(fake_ui_input_queue, MAP_SIZE_X, MAP_SIZE_Y)

    pdr_thread.start()
    mag_position_thread.start()
    fake_ui_thread.start()
    # except:
    #     print("Error: unable to start thread")

    return


if __name__ == '__main__':
    main()
