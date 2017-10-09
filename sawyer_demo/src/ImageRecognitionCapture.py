
import argparse
import sys
import copy
import rospy
import moveit_commander
import moveit_msgs.msg
import geometry_msgs.msg
## END_SUB_TUTORIAL
import json, ast
from std_msgs.msg import String

import intera_interface
import intera_external_devices
from intera_interface import CHECK_VERSION
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import Twist
import numpy as np
from intera_interface import (
    Gripper,
    Lights,
    Cuff,
    RobotParams,
    Head,
)
import uuid



import random
import time
import sys

import IK

# {'position': {'y': -0.5285591614758424, 'x': -0.10842641695707496, 'z': 0.13829145063080797},
# 'orientation': {'y': -0.49416732497866317, 'x': 0.4873692332042257, 'z': 0.5000563568640725, 'w': 0.5178933533162875}}

def ImageRecognition():
    rospy.init_node('mid' + str(uuid.uuid4().hex), anonymous=True)
    
    
    pose_target = geometry_msgs.msg.PoseStamped()
    pose_target.pose.orientation.w = 0.517
    pose_target.pose.orientation.x =  0.48739
    pose_target.pose.orientation.y =  -0.4941
    pose_target.pose.orientation.z =  0.500000
    pose_target.pose.position.x = -0.1084
    pose_target.pose.position.y = -0.5285
    pose_target.pose.position.z = 0.13829

    go(pose_target)
    i=1
    for x in np.arange(0.0, 0.1, 0.01):
        pose_target.pose.position.x = pose_target.pose.position.x + x
        pose_target.pose.position.y =  -0.5285
        for y in np.arange(0.0, 0.1, 0.01):
            pose_target.pose.position.y = pose_target.pose.position.y - y
            pose_target.pose.position.z =  0.13829
       
            for z in np.arange(0.0, 0.1, 0.01):
                pose_target.pose.position.z = pose_target.pose.position.z + z
                go(pose_target) 
#               print({"x":x, "y":y,"z":z})
                i+=1
                print(i)


    #print(joints)


def go(pose_target):
   
    ik = IK.IK()
    success,joints = ik.ik_service_client(pose_target,rospy)
    limb_joints = dict(zip(joints.joints[0].name, joints.joints[0].position))


    limb = intera_interface.Limb("right")
    limb.set_joint_position_speed(.2 )

    limb.move_to_joint_positions(limb_joints, timeout=20.0,threshold=intera_interface.settings.JOINT_ANGLE_TOLERANCE)

ImageRecognition()