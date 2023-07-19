import socket
import struct
import numpy as np
from PyQt5.QtWidgets import QApplication
import pyqtgraph.opengl as gl
import threading

UDP_IP = "127.0.0.1"  # 监听所有网络接口
UDP_PORT = 51180   # 自定义的UDP端口号
BUFFER_SIZE = 822  # 数据包总长度
PIXEL_COUNT = 96    # 像素数量
VERTICAL_ANGLE_RANGE = 12.5  # 垂直俯仰角范围
VERTICAL_ANGLE_STEP = 0.26  # 垂直俯仰角步长
HEADER_IDENTIFIER = 0x5BA555AA  # 包头识别符

# 创建UDP套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

# 创建PyQt图形应用程序
app = QApplication([])
w = gl.GLViewWidget()
w.opts['distance'] = 20
w.show()
w.setWindowTitle('3D Point Cloud')

# 创建点云容器
point_cloud_item = gl.GLScatterPlotItem()
w.addItem(point_cloud_item)

# 初始化点云数据
points = np.zeros((PIXEL_COUNT, 4), dtype=np.float32)
point_cloud_item.setData(pos=points[:, :3], color=(1, 0, 0, 1), size=5)  # 更新点云大小为1

frame_number = -1  # 当前帧号
current_frame_points = []  # 当前帧的点云数据

def update_point_cloud(data):
    global frame_number, current_frame_points

    # 解析数据包
    packet_frame_number = struct.unpack('I', data[4:8])[0]  # 数据包中的帧号
    if packet_frame_number != frame_number:
        # 当帧号刷新时，更新点云数据
        if frame_number != -1:
            # 显示上一帧的完整数据
            current_frame_points_array = np.asarray(current_frame_points)
            point_cloud_item.setData(pos=current_frame_points_array[:, :5], color=[1, 0, 0, 1], size=3)

        frame_number = packet_frame_number
        current_frame_points = []

    pixel_data = data[46:814]  # 提取像素数据部分

    # 解析每个像素点
    for i in range(0, PIXEL_COUNT * 8, 8):
        distance = struct.unpack('H', pixel_data[i:i+2])[0] * 0.01  # 径向距离信息
        intensity = struct.unpack('B', pixel_data[i+2:i+3])[0]      # 灰度信息
        confidence = struct.unpack('B', pixel_data[i+3:i+4])[0]     # 置信度信息
        vertical_angle = -VERTICAL_ANGLE_RANGE + (i // 8) * VERTICAL_ANGLE_STEP  # 垂直俯仰角
        horizontal_angle = struct.unpack('H', data[42:44])[0] * 0.01  # 水平方位角信息

        # 计算点云坐标
        x = distance * np.cos(np.deg2rad(vertical_angle)) * np.sin(np.deg2rad(horizontal_angle))
        y = distance * np.cos(np.deg2rad(vertical_angle)) * np.cos(np.deg2rad(horizontal_angle))
        z = distance * np.sin(np.deg2rad(vertical_angle))

        current_frame_points.append([x, y, z, intensity])

    # 更新点云数据
    # current_frame_points_array = np.asarray(current_frame_points)
    # point_cloud_item.setData(pos=current_frame_points_array[:, :3], color=[1,0,0,1], size=3)

def receive_udp_data():
    while True:
        data, _ = sock.recvfrom(BUFFER_SIZE)  # 接收UDP数据包

        # 验证包头识别符
        header = struct.unpack('<I', data[:4])[0]
        if header != HEADER_IDENTIFIER:
            continue

        update_point_cloud(data)

# 创建UDP数据接收线程
udp_thread = threading.Thread(target=receive_udp_data)
udp_thread.daemon = True
udp_thread.start()

# 运行PyQt图形应用程序
if __name__ == '__main__':
    QApplication.instance().exec_()
