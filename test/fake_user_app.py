from test_fake_threads.fake_socket_thread import FakeSocketThread
import queue
import socket

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

# 模拟手机APP采集发送的数据，实际读取的是文件数据
if __name__ == '__main__':
    socket_output_queue = queue.Queue()
    fake_socket_thread = FakeSocketThread(PATH_PDR_RAW[1], socket_output_queue)
    fake_socket_thread.start()

    # 从socket_output_queue拿出数据，弄成csv的格式发到服务器端
    server_port = 2212
    server_ip = '127.0.0.1'
    server_sock = socket.socket()
    server_sock.connect((server_ip, server_port))
    server_sock_file = server_sock.makefile(mode='w')

    user_phone = '123456789'
    server_sock_file.write(user_phone + '\n')
    server_sock_file.flush()

    while True:
        cur_data = socket_output_queue.get()
        if isinstance(cur_data, str) and cur_data == 'END':
            break
        else:
            # 弄成csv的格式
            csv_str = str(cur_data[0])
            for i in range(1, len(cur_data)):
                csv_str += ','
                csv_str += str(cur_data[i])

            server_sock_file.write(csv_str + '\n')
            server_sock_file.flush()

    server_sock_file.close()
    server_sock.close()
