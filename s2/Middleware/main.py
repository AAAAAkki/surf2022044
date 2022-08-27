# Press Shift+F10 to execute it or replace it with your code.
import car
from car import socket_test
import util

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # subscribe_client.run()
    # subscribe_client.latency_test()
    # car.csv_1line_test()
    # socket_test()
    # so.socket_client()
    # util.run_1_car()
    # a = '{"content":"3116.248679,N,12044.808839,E,220822,111252.0,84.2,0.0,\\r"}'
    # print(a)
    # b = car.jsonpickle.decode(a)
    # print(b)
    a = 'a\\r\\r\\n'
    print(a.replace(r'\r', '').replace('\\n', ''))
