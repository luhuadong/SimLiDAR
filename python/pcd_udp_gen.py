import socket
import struct
import random
import time

UDP_IP = "127.0.0.1"  # 目标IP地址
UDP_PORT = 51180     # 目标UDP端口号
BUFFER_SIZE = 822    # 数据包总长度
PIXEL_COUNT = 96     # 像素数量

# 创建UDP套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

frame_number = 0  # 帧号
packet_number = 0  # 包序号
start_azimuth = 30.0  # 水平方位角起始位置（单位：度）
end_azimuth = 150.0  # 水平方位角结束位置（单位：度）
horizontal_resolution = 1  # 水平角度分辨率（单位：度）

while True:
    # 生成随机数据
    status_info = "Status Information"  # 状态信息
    block_number = 0  # Block序号
    channel_count = 96  # 通道数
    azimuth = start_azimuth + packet_number * horizontal_resolution  # 水平方位角，0.1°为单位
    invalid_chars = b'\x00\x00'  # 无效字符
    pixels = []
    for _ in range(PIXEL_COUNT):
        # distance = random.randint(0, 10000)  # 径向距离信息
        distance = 1000  # 径向距离信息
        intensity = 255   # 灰度信息
        confidence = 255  # 置信度信息
        status = 0  # 像素状态信息
        pixels.append(struct.pack('HBBI', distance, intensity, confidence, status))
    pixel_data = b''.join(pixels)

    # 构建数据包
    packet = (
        struct.pack('I', 0x55aa5aa5) +               # 包头识别符
        struct.pack('H', frame_number) +             # 帧号
        struct.pack('H', packet_number) +            # 包序号
        status_info.encode('utf-8').ljust(32, b'\x00') +  # 状态信息
        struct.pack('B', block_number) +            # Block序号
        struct.pack('B', channel_count) +           # 通道数
        struct.pack('H', int(azimuth * 100)) +      # 水平方位角
        invalid_chars +                             # 无效字符
        pixel_data +                                # 像素数据
        b'\x00' * 8                                 # 包尾字节
    )

    # 发送数据包
    sock.sendto(packet, (UDP_IP, UDP_PORT))

    # 更新帧号和包序号
    packet_number += 1
    time.sleep(0.00001)
    if azimuth >= end_azimuth - horizontal_resolution:
        time.sleep(0.1)
        packet_number = 0
        frame_number += 1
        if frame_number > 65535:
            frame_number = 0