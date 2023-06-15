/*
 * Copyright (c) 2020-2023, GetIoT.tech
 *
 * SPDX-License-Identifier: LGPL v2.1
 * 
 * Change Logs:
 * Date           Author       Notes
 * 2023-06-14     luhuadong    the first version
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

// IP头部结构体
struct IPHeader
{
    unsigned char Ver_IHL;       // 版本信息
    unsigned char TOS;           // 服务类型
    unsigned short TotalLen;     // 包总长
    unsigned short ID;           // 标识符
    unsigned short Flag_Segment; // 标识符(高3位) + 片偏移(低13位)
    unsigned char TTL;           // 生存时间(TTL)
    unsigned char Protocol;      // 协议
    unsigned short CheckSum;     // 校验和
    unsigned int SourAddr;       // 源IP地址
    unsigned int DestAddr;       // 目的IP地址
};

// UDP头部结构体
struct UDPHeader
{
    unsigned short SourPort; // 源端口
    unsigned short DestPort; // 目的端口
    unsigned short Length;   // UDP长度
    unsigned short Checksum; // 校验和
};

// 计算校验和
unsigned short cal_check_sum(unsigned short *ip_payload, int payload_len)
{
    unsigned long sum = 0;
    while (payload_len > 1)
    {
        sum += *ip_payload++; // 添加一个字节
        if (sum & 0x80000000)
        {
            sum = (sum & 0xFFFF) + (sum >> 16);
        }
        payload_len -= 2;
    }
    if (payload_len)
    {
        sum += (unsigned long)*ip_payload;
    }
    while (sum >> 16)
    {
        sum = (sum & 0xFFFF) + (sum >> 16);
    }
    return (unsigned short)(~sum);
}

// UDP发送函数
int send_udp_packet(int sockfd, const char *dest_ip, unsigned short dest_port, const void *udp_data, int udp_data_len)
{
    // 填写UDP头部并计算校验和
    struct UDPHeader udp_hdr;
    udp_hdr.SourPort = htons(51234);
    udp_hdr.DestPort = htons(dest_port);
    udp_hdr.Length = htons(udp_data_len + sizeof(struct UDPHeader));
    udp_hdr.Checksum = 0; // UDP不需要校验和

    // 填写IP头部
    struct IPHeader ip_hdr;
    ip_hdr.Ver_IHL = 0x45;
    ip_hdr.TOS = 0;
    ip_hdr.TotalLen = sizeof(struct IPHeader) + sizeof(struct UDPHeader) + udp_data_len;
    ip_hdr.ID = htons(random() % 65535);
    ip_hdr.Flag_Segment = htons(0x4000); // 0x4000表示不分片
    ip_hdr.TTL = 255;
    ip_hdr.Protocol = IPPROTO_UDP;
    ip_hdr.CheckSum = 0;
    ip_hdr.SourAddr = 0; // 后面会修改
    ip_hdr.DestAddr = inet_addr(dest_ip);

    // 计算IP头部校验和
    ip_hdr.CheckSum = cal_check_sum((unsigned short *)&ip_hdr, sizeof(ip_hdr));

    // 构造整个UDP包
    char packet[sizeof(struct IPHeader) + sizeof(struct UDPHeader) + udp_data_len];
    memcpy(packet, &ip_hdr, sizeof(struct IPHeader));
    memcpy(packet + sizeof(struct IPHeader), &udp_hdr, sizeof(struct UDPHeader));
    memcpy(packet + sizeof(struct IPHeader) + sizeof(struct UDPHeader), udp_data, udp_data_len);

    // 填写源IP地址
    struct sockaddr_in dest_addr;
    memset(&dest_addr, 0, sizeof(dest_addr));
    dest_addr.sin_family = AF_INET;
    dest_addr.sin_port = htons(dest_port);
    dest_addr.sin_addr.s_addr = inet_addr(dest_ip);

    printf("UDP client send to %s:%u\n", dest_ip, dest_port);

    // 发送数据包
    int ret = sendto(sockfd, packet, sizeof(packet), 0, (struct sockaddr *)&dest_addr, sizeof(dest_addr));
    if (ret < 0)
    {
        perror("sendto error");
        return ret;
    }
    printf("Send %u bytes\n", ret);
    return ret;
}