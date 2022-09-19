# -*- coding = utf-8 -*-
# @Time: 2022/6/20 11:15
# @File: car.PY


import csv
import json
import socket
import sys
import threading
import time
from dataclasses import dataclass, field

import jsonpickle

import subscribe_client
from subscribe_client import host, port, clt_id, clt_username, clt_password, ali_pub_topic

HOST_Aliyun = host
PORT_Aliyun = port


def car_class_test():
    # 测试代码

    car = Car('001', 'Truck')  # 车辆信息初始化

    print(car.toJson())  # 打印车辆信息


def csv_1line_test():
    # 清空文件内容
    with open('car.csv', mode='w', encoding='utf-8', newline='') as f:
        f.write('')

    lat = 3116.269116
    one_info = SensorInfo(lat, 'N', 12044.799782, 'E', '270622', '084506.0', '18.7', '0.0')
    vehicle = Car('001', 'car', one_info)
    # 存入50个gps信息对象到Car对象队列
    for i in range(50):
        lat += 1
        two_info = SensorInfo(lat, 'N', 12044.799782, 'E', '270622', '084506.0', '18.7', '0.0')
        vehicle.add_sensor_info(two_info)
    for i in range(20):
        vehicle.csv_1line()


def socket_test():
    vehicle = Car('001', 'car')
    vehicle.set_aliyun_username(clt_id, clt_username, clt_password)
    vehicle.thread_run()
    while not vehicle._socket_conn:
        pass

    def thread_foo():
        lat = 31.16250066
        ang = '0.0'
        count = 1.0
        while 1:
            lat += 0.0003
            count += 1
            if count % 100 == 0:
                ang = '0.0'
            elif count % 50 == 0:
                ang = '90.0'
            two_info = SensorInfo(lat, 'N', 120.44819838, 'E', '270622', '084506.0', ang, '0.0')
            vehicle.add_sensor_info(two_info)
            data = vehicle.get_sensor_info()
            vehicle.send_data(data)
            time.sleep(0.1)

    t = threading.Thread(target=thread_foo)
    t.daemon = True
    t.start()

    input_val = input()
    if input_val == 'exit':
        vehicle.thread_terminate()
        sys.exit(0)


class Car(object):
    ''' This object collects GPS information from AliCloud to simulate movement of vehicle, then send calculated data
        via socket.'''
    _car_sock = None

    def __init__(self, car_id, car_type, init_sensor=None):
        # car info
        self._car_id = car_id
        self._car_type = car_type
        # sensor info
        self.car_sensor = init_sensor
        self._write_counter = self.order_gen(1)
        # attributes regarding communication
        self.__host = '127.0.0.1'
        self.__port = 62333
        if Car._car_sock is None:
            Car._car_sock = self.creat_socket_server()
        self._mqtt_conn = None
        self._username = None
        self._ali_userid = None
        self._pwd = None
        self._on_message = None
        self._socket_conn = None
        self._client_addr = None
        self._prot_rev = 0
        self._attr_send = []
        self.advise = {'Advise': 'No Advise'}
        # thread_info
        self._thread = None
        self._terminate = True

    def get_sensor_info(self):
        return self.car_sensor.toJson()

    def add_sensor_info(self, new_sensor_info):
        self.car_sensor = new_sensor_info

    def reset_car_info(self, new_id, new_type):
        self._car_id = new_id
        self._car_type = new_type

    def toJson(self):
        car_msg = dict(self)
        return jsonpickle.encode(car_msg, False)

    def get_vehicle(self):
        return self

    def set_aliyun_username(self, userid, username, pw):
        self._ali_userid = userid
        self._username = username
        self._pwd = pw

    def csv_1line(self):
        count = next(self._write_counter)
        header_list = ['No.', '_car_id']
        car_info_dict = {'No.': count, '_car_id': self._car_id}
        header_list += self.car_sensor.keys()
        data = self.get_sensor_info()
        data_list = dict(car_info_dict, **dict(data))
        with open('car.csv', mode='a', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, header_list)
            if count == 1:
                writer.writeheader()
            writer.writerow(data_list)
        return data_list

    def creat_socket_server(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.__host, self.__port))
            s.listen(10)
        except socket.error as msg:
            print(msg)
            sys.exit(1)
        print('Server created')
        print('Waiting...')
        return s

    def socket_conn(self):
        while self._socket_conn is None:
            conn, addr = self._car_sock.accept()
            print(f'从地址 {addr}接收到一个新连接')
            self._socket_conn = conn
            self._client_addr = addr
            # self._thread = None
            time.sleep(0.05)

    def dual_way_connect(self):
        '''Connects AliCloud and socket client'''
        def on_message(client, userdata, msg):
            # steps: 1.save data to object 2.check time 3.socket send
            data = str(msg.payload)
            decoded_data = data
            try:
                data = data.strip('b')
                data = data.strip("'")
                data = data.replace(r'\r', '').replace(r'\n', '')
                data = data.replace('\\', '')
                decoded_data = jsonpickle.decode(data)
                decoded_data = decoded_data['content']
            except json.decoder.JSONDecodeError:
                print('Json transforming failed:', data)
            decoded_data = decoded_data.split(',')
            if r'\r' in data:
                decoded_data.remove(r'\r')
            if r'\r\n' in data:
                decoded_data.remove(r'\r\n')
            try:
                decoded_data[0] = float(decoded_data[0]) / 100
                decoded_data[2] = float(decoded_data[2]) / 100
                while len(decoded_data) > 8:
                    decoded_data.pop(-1)
                formatted_data = SensorInfo(*decoded_data)
                self.add_sensor_info(formatted_data)
                self.send_data(self.get_sensor_info())
            except:
                print('data cause error', decoded_data, msg.mid)

        self._mqtt_conn = subscribe_client.ali_connect(self._ali_userid, self._username, self._pwd, HOST_Aliyun,
                                                       PORT_Aliyun)
        self._on_message = on_message
        self._mqtt_conn.on_message = self._on_message
        self._mqtt_conn.loop_start()

        self.socket_conn()

    def send_data(self, data):
        data_processed = {}
        data_2_send = {}
        err_num: int = 0
        if type(data) is str:
            data_processed = Car.readJson(data)
        if type(data) is dict:
            data_processed = data
        for k in self._attr_send:
            try:
                data_2_send.update({k: data_processed[k]})
            except KeyError:
                data_2_send.update({k: 'Err'})
                err_num += 1
        if self._prot_rev == 0:
            data_2_send.update(data_processed)
        data_2_send.update({'prot': self._prot_rev, 'err': err_num})
        try:
            self._socket_conn.sendall(jsonpickle.encode(data_2_send).encode('utf-8'))
        except AttributeError:
            print('Connection Error')
            print('Stop sending messages')
            while not self._socket_conn:
                pass
        except OSError:
            print('OS error')

    def receive_data(self):
        data = None
        try:
            data = self._socket_conn.recv(1024)
            print('receive:', data)
            data = jsonpickle.decode(data)
            if 'req' in data.keys():
                # protocol set msg
                self._prot_rev = data['prot']
                self._attr_send = data['req']
            else:
                # data msg, check protocol
                if data['prot'] == self.prot_set:
                    return data
                elif 'advise' in data.keys():
                    if data != self.advise:
                        self.advise = data
                        self._mqtt_conn.publish(ali_pub_topic, jsonpickle.encode(self.advise).encode('utf-8'))
                else:
                    # wrong format, send request again
                    self.send_form_req(self._attr_send, self.prot_set)
                    return None
        except (ConnectionResetError, AttributeError):
            print('Client shutdown\nReconnecting...')
            self.reconnect()
        except json.decoder.JSONDecodeError:
            if len(data) == 0:
                print('Client shutdown\nReconnecting...')
                self.reconnect()
            else:
                print('wrong msg caused error:')
                print(data)

    def _thread_task(self):
        if self._mqtt_conn is None and self._socket_conn is None:
            self.dual_way_connect()
        while not self._terminate:
            # self.advise = self.receive_data()
            self.receive_data()

            time.sleep(0.01)

    def thread_run(self):
        self._terminate = False
        self._thread = threading.Thread(target=self._thread_task)
        self._thread.daemon = True
        self._thread.start()

    def thread_terminate(self):
        self._terminate = True
        try:
            self._socket_conn.shutdown(socket.SHUT_RDWR)
            self._socket_conn.close()
        except AttributeError:
            print('Connection has closed')
        self._socket_conn = None

    def reconnect(self):
        self._socket_conn = None
        self.socket_conn()

    def keys(self):
        return ('_car_id', '_car_type', 'car_sensor')

    def __getitem__(self, item):
        return getattr(self, item)

    def order_gen(self, num_2_start):
        while True:
            yield num_2_start
            num_2_start += 1

    @staticmethod
    def readJson(string):
        return jsonpickle.decode(string)


@dataclass
class SensorInfo:
    '''Object to store GPS data'''
    lat: float
    lat_semi: str
    lon: float
    lon_semi: str
    date: str
    time: str
    angel: str = '0'
    speed: str = '0'
    timestamp: float = time.time()
    gps_time: float = field(init=False)

    def __post_init__(self):
        self.gps_time = self._format_trans()

    def _format_trans(self) -> float:
        appr_time = self.time[:6]
        factor_time = float(self.time[6:8])
        time_struct = time.strptime(self.date + appr_time, '%d%m%y%H%M%S')
        time_stamp = time.mktime(time_struct) + factor_time
        return time_stamp

    def is_outdated(self):
        if self.timestamp - self.gps_time > 0.1:
            return True
        return False

    def keys(self):
        return [k for k in self.__dict__.keys() if k not in ['time', 'date']]

    def __getitem__(self, item):
        return getattr(self, item)

    def toJson(self):
        msg = dict(self)
        return jsonpickle.encode(msg)
