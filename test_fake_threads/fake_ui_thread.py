import threading
import time
import mag_and_other_tools.paint_tools as PT
import numpy as np


class FakeUiThread(threading.Thread):
    def __init__(self, in_data_queue, map_size_x, map_size_y):
        super(FakeUiThread, self).__init__()
        self.in_data_queue = in_data_queue
        self.paint_map_size = [0, map_size_x * 1.0, 0, map_size_y * 1.0]

    def run(self) -> None:
        self.get_result_and_paint(self.in_data_queue, self.paint_map_size)

    # in_data_queue每个单位 = [Ni][x, y]，每隔0.5秒获取其中的所有数据、拼接到final_xy、并paint到画布上
    def get_result_and_paint(self, in_data_queue, paint_map_size) -> None:
        final_xy = []

        while True:
            final_xy.extend(in_data_queue.get())
            PT.paint_xy_list([np.array(final_xy)], ['MagPDR'], paint_map_size, "Result")
