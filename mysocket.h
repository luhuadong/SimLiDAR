/*
 * Copyright (c) 2020-2023, GetIoT.tech
 *
 * SPDX-License-Identifier: LGPL v2.1
 * 
 * Change Logs:
 * Date           Author       Notes
 * 2023-06-14     luhuadong    the first version
 */

#ifndef __MY_SOCKET_H__
#define __MY_SOCKET_H__

int send_udp_packet(int sockfd, const char *dest_ip, unsigned short dest_port, 
                    const void *udp_data, int udp_data_len);

#endif /* __MY_SOCKET_H__ */