# -*- coding = utf-8 -*-
# @Time: 2022/4/18 12:14
# @File: main.PY
import socket
import sys
import xml.etree.ElementTree as ET
import json
import time
import random as rn

import jsonpickle


def motor_xml(rpm, current):
    root = ET.Element('Data')
    tree = ET.ElementTree(root)
    element = ET.Element('rpm')
    element.text = str(rpm)
    root.append(element)
    element = ET.Element('current')
    element.text = str(current)
    root.append(element)
    tree.write('default.txt', encoding='utf-8', xml_declaration=True)


def socket_client():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('192.168.31.219', 8080))
    except socket.error as msg:
        print(msg)
        sys.exit(1)
    while 1:
        send_msg = ''
        f = open(file='default.txt', mode='r')
        data = f.readlines()
        f.close()
        if data == 'exit':
            break
        for lines in data:
            send_msg += lines
        send_msg.replace('\n', '')
        s.send(send_msg.encode())
        s.recv(1024)
    s.close()


def socket_client(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 获取本地主机名
        s.connect((host, port))  # 要连接的IP与端口
    except socket.error as msg:  # 错误处理
        print(msg)
        sys.exit(1)
    # print(s.recv(1024))
    deal_data(s)
    # while 1:
    #     # data = ['120.62', 'N', '31.32', 'E', time.time()]
    #     data = 'test_string'
    #     s.send(data.encode('utf-8'))
    #     time.sleep(0.5)


def deal_data(conn):
    import jsonpickle
    import demjson
    while 1:
        recvd_size = 0
        data = conn.recv(1024)
        recvd_size += len(data)
        if recvd_size != 0:
            print(f'received {recvd_size} bytes:', data)
            dict_of_data = demjson.decode(data)
            for v in dict_of_data.items():
                print(v)
            print(dict_of_data['lat'])


if __name__ == '__main__':
    # socket_client('127.0.0.1', 62333)
    # motor_xml(rn.random() + rn.randint(0, 20), rn.randrange(500, 10000))
    # import socket_client
    # socket_client.socket_client_sample()
    # socket_client.socket_client_test()
    # 将file后改为json文件路径
    # json_file = open(file='file.json', mode='r')
    # # 将文件内容载入到json_data
    # json_data = json.load(json_file)
    # json_file.close()
    # # 创建list lon, lat
    # lon = [i['lon'] for i in json_data]
    # lat = [i['lat'] for i in json_data]
    a: int = 1 << 3
    b: int = 1
    key_offset = a | b


    def key_pressed(input):
        print(key_offset & input == key_offset and key_offset | input == key_offset)


    key_pressed(1 << 3 )
