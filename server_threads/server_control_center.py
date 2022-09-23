# 服务器线程控制中心:
# 声明公共数据容器，
# DI到 socket线程、pdr线程、magPdr线程，三个“守护线程”
# 并启动它们
import threading
import time
from server_threads.pdr_thread import PdrThread
from server_threads.mag_position_thread import MagPositionThread
import queue


def main():
    socket_output_queue = queue.Queue()

    pdr_input_queue = socket_output_queue
    pdr_output_queue = queue.Queue()

    mag_position_input_queue = pdr_output_queue
    mag_position_output_queue = queue.Queue()
    mag_position_config_file = "D:\pythonProjects\MagPdr_server\server_threads\mag_position_config.json"

    try:
        pdr_thread = PdrThread(pdr_input_queue, mag_position_output_queue)
        mag_position_thread = MagPositionThread(mag_position_input_queue, mag_position_output_queue,
                                                mag_position_config_file)

        pdr_thread.start()
        mag_position_thread.start()
    except:
        print("Error: unable to start thread")

    return


if __name__ == '__main__':
    main()
