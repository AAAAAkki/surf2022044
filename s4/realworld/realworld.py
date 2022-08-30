import json
import pyproj
from math import sqrt
from controller import Supervisor
import pandas as pd
from projection import Projection
import optparse
import math
import sys
import socket
import time
import jsonpickle
import threading
from socket_client import Socket_client
from socket_client import socket_client_sample

HOST = '127.0.0.1'
PORT = 62333

s = Socket_client(HOST, PORT)
s.conn_to_server()
s.thread_run()
#lat = s.data_rev['lat']
#lon = s.data_rev['lon']

try:
    import pyproj
except:
    sys.exit("Error: pyproj python module not installed. You can install it using pip: 'pip install pyproj'")

## lat0 and long0  can be read from gpsReference
lat0 =31.27375
long0 = 120.73530

utm_zone = 1 + math.floor((float(long0) + 180) / 6)
hemisphere = 'south' if lat0 < 0 else 'north'
projectionString = \
    "+proj=utm +%s +zone=%d +lon_0=%f +lat_0=%f +x_0=0 +y_0=0 +ellps=WGS84 +units=m +no_defs" % \
    (hemisphere, utm_zone, long0, lat0)

utm_coord_zero = pyproj.Proj(projectionString)

xoffest, yoffset = utm_coord_zero(long0, lat0)

TIME_STEP = 32

supervisor = Supervisor()

# get handle to robot's translation field
robot_node = supervisor.getFromDef("REALWORLD_VEHICLE0")
trans_field = robot_node.getField("translation")
rot_field = robot_node.getField("rotation")
optParser = optparse.OptionParser(usage="usage: %prog --input=file.osm [options]")


# evaluate robot during 60 seconds (simulation time)
#t = supervisor.getTime()
#while supervisor.getTime() - t < 0.1:
#t = supervisor.getBasicTimeStep()
while supervisor.getBasicTimeStep() != -1:
#while 1:    
    if s.data_rev:
        lat1 = s.data_rev['lat']
        long1 = s.data_rev['lon']
        
        latint=int(lat1)
        longint=int(long1)

        latde=(lat1-latint)*100/60
        longde=(long1-longint)*100/60

        lat2=latint+latde
        long2=longint+longde

        x1, y1 = utm_coord_zero(long2, lat2)

        ## calculate the coordiantes of realworld vehicle in Webots map
        x = xoffest-x1
        y = y1-yoffset
        z = 0.5

        POSITION = [x, y, z]
        
        
    #rotation计算
        rotation = [0, 1, 2, 3]
        yaw = float(s.data_rev['angel'])
        roll = 0
        pitch = 0

        a = math.cos(roll) * math.cos(yaw)
        b = -math.sin(roll)
        c = math.cos(roll) * math.sin(yaw)
        d = math.sin(roll) * math.cos(yaw) * math.cos(pitch) + math.sin(yaw) * math.sin(pitch)
        e = math.cos(roll) * math.cos(pitch)
        f = math.sin(roll) * math.sin(yaw) * math.cos(pitch) - math.cos(yaw) * math.sin(pitch)
        g = math.sin(roll) * math.cos(yaw) * math.sin(pitch) - math.sin(yaw) * math.cos(pitch)
        h = math.cos(roll) * math.sin(pitch)
        i = math.sin(roll) * math.sin(yaw) * math.sin(pitch) + math.cos(yaw) * math.cos(pitch)

        cosAngle = 0.5 * (a + e + i - 1.0)

        rotation[0] = 0
        rotation[1] = 0
        rotation[2] = 1
        rotation[3] = math.acos(cosAngle)

        length = math.sqrt(rotation[0] * rotation[0] + rotation[1] * rotation[1] + rotation[2] * rotation[2])
        if length != 0:
                rotation[0] = rotation[0] / length
                rotation[1] = rotation[1] / length
                rotation[2] = rotation[2] / length
        if rotation[0] == 0 and rotation[1] == 0 and rotation[2] == 0:
                rotation[0] = 0
                rotation[1] = 0
                rotation[2] = 1
                rotation[3] = 0
        else:
                rotation[0] = 0
                rotation[1] = 0
                rotation[2] = 1
                rotation[3] = math.acos(cosAngle)
            
        #rotation=[0,1,2,3]
            
            
        trans_field.setSFVec3f(POSITION)
        rot_field.setSFRotation(rotation)
        robot_node.resetPhysics()
        # perform robot control according to a, b
        # (and possibly t) parameters.

        # controller termination
        if supervisor.step(TIME_STEP) == -1:
           quit()

        # compute travelled distance
   # values = trans_field.getSFVec3f()
    #dist = sqrt(values[0] * values[0] + values[2] * values[2])
    #print("a=%d, b=%d -> dist=%g" % (a, b, dist))
