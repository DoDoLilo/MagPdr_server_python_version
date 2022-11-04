from collections import OrderedDict

import numpy as np
# import queue
# from server_threads import socket_thread
#
# port = 2212
# socket_output_queue = queue.Queue()
# socket_server_thread = socket_thread.SocketServerThread(socket_output_queue, port)
# socket_server_thread.start()
#
# while True:
#     cur_data = socket_output_queue.get()
#     print(cur_data)

from mag_and_other_tools.config_tools import SystemConfigurations
config_json_file = './server_threads/mag_position_config.json'
system_configurations = SystemConfigurations(config_json_file)
print(system_configurations.init_succeed)