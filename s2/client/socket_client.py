# -*- coding = utf-8 -*-
# @Time: 2022/7/18 15:14
# @File: socket_client.PY
import os
import socket
import time
import sys
import json
import jsonpickle
import threading

HOST = '127.0.0.1'
PORT = 62333
default_init_lat = 31.27375
default_init_lon = 120.7353


class Socket_client:
    """
    The socket client class to connect to assigned socket server created locally. Receives data in Json format,
    output and store as a dict object. Also able to send request for data which users expect if available and
    accessible on server.
    A method will be given as sample at the end of this module with its name containing 'sample'.
    """
    command_list = [{'prot': 1, 'attr': ['lat', 'lon', 'timestamp', 'angel', 'speed']},
                    {'prot': 2, 'attr': ['lat', 'lon']}]
    server_stat = False

    def __init__(self, host, port, init_lat=default_init_lat, init_lon=default_init_lon):
        self.__class__.start_server()
        self.__host = host
        self.__port = port
        self.socket = None
        self.conn = None
        self._prot_set = self.command_list[0]['prot']
        self.prot_rev = 0
        self.data_rev = {'lat': init_lat, 'lon': init_lon}
        self._attr_send = self.command_list[0]['attr']
        self.position_update_time = time.time()
        self.last_position = [default_init_lat, default_init_lon]
        self.position_before_last = self.last_position
        self.thread = None
        self._terminate = True

    @classmethod
    def start_server(cls):
        # 关闭可能正在运行的服务端，然后启动服务端
        if not cls.server_stat:
            try:
                os.system(r'taskkill /IM main.exe')
            except:
                pass
            time.sleep(0.01)
            os.startfile(r'C:\Users\Jiang Ziqiu\Desktop\SocketServer v0.4\dist\main\main.exe')
            time.sleep(0.02)

    def conn_to_server(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # 获取本地主机名
            s.connect((self.__host, self.__port))  # 要连接的IP与端口
            self.conn = s
            self.send_form_rqt()
        except socket.error as msg:  # 错误处理
            print(msg)
            sys.exit(1)

    def send_data(self, data):

        data_processed = {}
        data_2_send = {}
        if type(data) is str:
            data_processed = dict(jsonpickle.decode(data), **{'prot': self.prot_rev})
        if type(data) is dict:
            data_processed = dict(data, **{'prot': self.prot_rev})

        if self.prot_rev == 0:
            data_processed['prot'] = 0
            data_2_send = data_processed
        else:
            for k in self._attr_send:
                try:
                    data_2_send.update({k: data_processed[k]})
                except KeyError:
                    data_2_send.update({k: 'Err'})
            data_2_send.update({'prot': self.prot_rev})
        try:
            self.conn.sendall(jsonpickle.encode(data_2_send).encode('utf-8'))
        except (OSError, AttributeError) as e:
            print(str(e))
            self.conn = None
            self.reconnect()

    def set_form_rqt(self, attrs: list = None, command: int = None):
        if command is None:
            self._prot_set = self.command_list[0]['prot']
            self._attr_send = self.command_list[0]['attr']
        else:
            self._prot_set = command
            self._attr_send = attrs

    def send_form_rqt(self):
        rqt_dict = {'req': self._attr_send, 'prot': self._prot_set}
        self.conn.sendall(jsonpickle.encode(rqt_dict).encode('utf-8'))
        print('msg sent')

    def send_new_form_rqt(self, attrs: list = None, command: int = None):
        if command != self._prot_set:
            self.set_form_rqt(attrs, command)
            self.send_form_rqt()
        else:
            print('No Need to Update Request')

    def receive_data(self):
        data = None
        try:
            data = self.conn.recv(1024)
            data = jsonpickle.decode(data)
            if 'req' in data.keys():
                # protocol set msg
                self.prot_rev = data['prot']
                self._prot_set = data['prot']
                self._attr_send = data['req']
            else:
                # data msg, check protocol
                if data['prot'] == self._prot_set:
                    if 'err' in data.keys() and data['err'] == 0:
                        pass
                    else:
                        print('Error Exist:', data)
                    return data
                else:
                    # wrong format, send request again
                    print('incorrect format:')
                    print(data)
                    self.send_form_rqt()
                    return None
        except json.decoder.JSONDecodeError:
            if len(data) == 0:
                print('Server Closed')
                self.thread_terminate()
            else:
                print('wrong msg caused error:')
                print(data)

    def _thread_task(self):
        while not self._terminate:
            try:
                self.receive_data()
                if self.data_rev['lat'] != default_init_lat:
                    print(self.data_rev['lat'], self.data_rev['lon'], self.data_rev['angel'])
                    print(self.data_rev['timestamp'])
                time.sleep(0.01)
            except ConnectionResetError:
                self.thread_terminate()
            except OSError:
                self.thread_terminate()
            except KeyError:
                print('format error')
                print(self.data_rev)

    def thread_run(self):
        if self.conn is None:
            print('No Connection')
            return
        self._terminate = False
        self.thread = threading.Thread(target=self._thread_task)
        self.thread.daemon = True
        self.thread.start()

    def thread_terminate(self):
        self._terminate = True
        try:
            self.conn.shutdown(socket.SHUT_RDWR)
            self.conn.close()
        except AttributeError:
            print('Server Closed. Client thread stops')
        self.conn = None
        print('Client close')
        sys.exit(0)

    def compensate_task(self):
        while 1:
            if time.time() - self.position_update_time > 0.15:
                if [self.data_rev['lat'], self.data_rev['lon']] == self.last_position:

                    self.data_rev['lat'] += self.last_position[0] - self.position_before_last[0]
                    self.data_rev['lon'] += self.last_position[1] - self.position_before_last[1]
                self.position_update_time = time.time()
                self.position_before_last = self.last_position
                self.last_position = [self.data_rev['lat'], self.data_rev['lon']]
            time.sleep(0.15)

    def reconnect(self):
        while self.conn:
            pass
        self.conn_to_server()


def socket_client_test():
    s = Socket_client(HOST, PORT)
    s.conn_to_server()
    s.thread_run()
    retval = input()
    if retval == 'exit':
        s.thread_terminate()


def socket_client_sample():
    s = Socket_client(HOST, PORT)
    s.conn_to_server()
    s.thread_run()
    """Till now, the client starts running. It keeps receiving messages and printing them per 0.01s. However, 
    the real rate of message update also depends on the sending rate of server. The receiving data is accessible with 
    attribute 'data_rev' """
    while 1:
        """it is recommended to check if s.data_rev is None before using it as shown below. Then, you can use it as 
        you want """
        # if s.data_rev:
        #     # print(s.data_rev['lat'], s.data_rev['lon'])
        #     # print(s.data_rev)
        time.sleep(0.1)
