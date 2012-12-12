import os
import dynamixel
import time
import random
import sys
import subprocess
import math

class Robot:
    STAY = 'STAY'
    
    def __init__(self, servo_map, theta0, speed=80, grasp_angle=10, release_angle=-30, port="COM15", bps=1000000):
        self.port = port
        self.theta0 = theta0
        self.speed = speed
        self.bps = bps
        self.grasp_angle = grasp_angle
        self.release_angle = release_angle
        self.servos = {}
        self.servo_num = 0

        lastServoId = max(servo_map)+1
        self.serial = dynamixel.SerialStream(port=self.port, baudrate=self.bps, timeout=1)
        self.net = dynamixel.DynamixelNetwork(self.serial)
        self.net.scan(1, lastServoId)

        print "Scanning for servos..."
        for dyn in self.net.get_dynamixels():
            print "Found", dyn.id
            self.servos[servo_map.index(dyn.id)] = self.net[dyn.id]
            self.servo_num+=1

        if not self.servos:
            print 'No servos found! Check USB2Dynamixel connection.'
            sys.exit(0)
        else:
            print "...Done!"

        for id, servo in self.servos.items():
            servo.moving_speed = self.speed
            servo.synchronized = True
            servo.torque_enable = True
            servo.torque_limit = 800
            servo.max_torque = 800

    def convert_angle(self, deg):
        return int((deg+150.0)/300 * 1024.0)

    def move(self, joint, angle):
        if angle != Robot.STAY and not (math.isnan(angle)):
            self.servos[joint].goal_position = self.convert_angle(angle)
        self.net.synchronize()

    def move_all(self, angles):
        for i, angle in enumerate(angles):
            if angle != Robot.STAY and not (math.isnan(angle)):
                self.servos[i].goal_position = self.convert_angle(angle)
        self.net.synchronize()

    def go_home(self):
        self.move_all(self.theta0)

    def read_pos(self, servo_id):
        servo = self.servos[servo_id]
        servo.read_all()
        return servo.cache[dynamixel.defs.REGISTER['CurrentPosition']]

    def read_all_pos(self):
        return [self.read_pos(i) for i in range(0, self.servo_num)]

    def rotate_base(self, angle):
        self.move(0, angle)

    def rotate_shoulder(self, angle):
        self.move(1, angle)

    def rotate_elbow(self, angle):
        self.move(2, angle)

    def rotate_wrist(self, angle):
        self.move(3, angle)

    def rotate_hand(self, angle):
        self.move(4, angle)

    def grasp(self, force=1):
        self.move(5, self.grasp_angle)

    def release(self):
        self.move(5, self.release_angle)
    
