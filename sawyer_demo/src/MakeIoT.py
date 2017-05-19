#!/usr/bin/env python

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

import pymongo
from pymongo import MongoClient

from intera_interface import (
    Gripper,
    Lights,
    Cuff,
    RobotParams,
)

def move_group_python_interface_tutorial():
  uri = "mongodb://sawyer-mongo:xJENhr8tU9SnRzvn5DVXutJWDsaXBAm6urVHUT6zNirq2ycKx0BQwDbCz6lUqsyYrXc1ENnDIFb3YMTtlE6m5g==@sawyer-mongo.documents.azure.com:10255/?ssl=true"
  client = MongoClient(uri)
  
  db = client.SawyerDB
  collection = db.Command
           
  data = collection.find_one()
  print "Value : %s" %  data.keys() 
  print data
  
  moveit_commander.roscpp_initialize(sys.argv)
  rospy.init_node('move_group_python_interface_tutorial',
                  anonymous=True)

  light = Lights()
  light.set_light_state('head_red_light', True)
    
  rs = intera_interface.RobotEnable(CHECK_VERSION)
 
  robot = moveit_commander.RobotCommander()

  scene = moveit_commander.PlanningSceneInterface()

  group = moveit_commander.MoveGroupCommander("right_arm")


  display_trajectory_publisher = rospy.Publisher(    '/move_group/display_planned_path',
                                      moveit_msgs.msg.DisplayTrajectory, queue_size=20)




  group.clear_pose_targets()

  ## Then, we will get the current set of joint values for the group
  group_variable_values = group.get_current_joint_values()
  #print "============ Joint values: ", group_variable_values

 
  gripper = intera_interface.Gripper("right")
  print "============close"
  #gripper.reboot()
  #gripper.calibrate()
 # gripper.close()
  #gripper.open()
  #return
  print "============Start"
  
  ps  = group.get_current_pose("right_gripper")

  #Referee Point
  jointpos =  data['Joints']
  print jointpos


  position = ast.literal_eval(json.dumps(jointpos))
  print position
 #position ={'right_j6': 3.8832177734375, 'right_j5': -1.0124833984375, 'right_j4': -2.5925, 'right_j3': -2.53425390625, 'right_j2': -2.7182216796875, 'right_j1': -0.02024609375, 'right_j0': -2.2311181640625}
 
  group.set_joint_value_target(position)
  plan2 = group.plan()
  group.go(wait=True)
  return
  #Down
  position ={'right_j6': 3.8086181640625, 'right_j5': -0.8446669921875, 'right_j4': -2.4781865234375, 'right_j3': -2.3397265625, 'right_j2': -2.7640244140625, 'right_j1': 0.087705078125, 'right_j0': -2.1369375}
  group.set_joint_value_target(position)
  plan2 = group.plan()
  group.go(wait=True)

  gripper.close()

  #up
  position = {'right_j6': 3.934345703125, 'right_j5': -1.072455078125, 'right_j4': -2.62596484375, 'right_j3': -2.468337890625, 'right_j2': -2.7010771484375, 'right_j1': 0.0829775390625, 'right_j0': -2.19303515625}
  group.set_joint_value_target(position)
  plan2 = group.plan()
  group.go(wait=True)

  #over
  position ={'right_j6': 3.985046875, 'right_j5': -1.0209921875, 'right_j4': -2.4788056640625, 'right_j3': -2.2808125, 'right_j2': -2.6110234375, 'right_j1': 0.162982421875, 'right_j0': -1.961265625}
  group.set_joint_value_target(position)
  plan2 = group.plan()
  group.go(wait=True)
  
  gripper.open()

  ##GRAB LID
  #up
  position ={'right_j6': 3.985046875, 'right_j5': -1.017466796875, 'right_j4': -2.2719208984375, 'right_j3': -2.391259765625, 'right_j2': -2.437890625, 'right_j1': 0.05647265625, 'right_j0': -1.9700712890625}
  group.set_joint_value_target(position)
  plan2 = group.plan()
  group.go(wait=True)
  

  #over
  position ={'right_j6': 3.048396484375, 'right_j5': -1.313734375, 'right_j4': -1.4312890625, 'right_j3': -1.403357421875, 'right_j2': -1.8894560546875, 'right_j1': 0.33964453125, 'right_j0': -1.7575322265625}
  group.set_joint_value_target(position)
  plan2 = group.plan()
  group.go(wait=True)
  

  #down
  position ={'right_j6': 3.048822265625, 'right_j5': -1.287021484375, 'right_j4': -1.6263349609375, 'right_j3': -1.386447265625, 'right_j2': -1.8890234375, 'right_j1': 0.510974609375, 'right_j0': -1.78403125}

  group.set_joint_value_target(position)
  plan2 = group.plan()
  group.go(wait=True)

  gripper.close()


  #up
  position ={'right_j6': 3.049029296875, 'right_j5': -1.5075927734375, 'right_j4': -1.6273681640625, 'right_j3': -1.570642578125, 'right_j2': -1.6996220703125, 'right_j1': 0.429619140625, 'right_j0': -1.7899296875}

  group.set_joint_value_target(position)
  plan2 = group.plan()
  group.go(wait=True)

  #Over
  position ={'right_j6': 3.8408310546875, 'right_j5': -1.3141474609375, 'right_j4': -2.2509150390625, 'right_j3': -2.22596875, 'right_j2': -2.2963857421875, 'right_j1': 0.400546875, 'right_j0': -2.006712890625}

  group.set_joint_value_target(position)
  plan2 = group.plan()
  group.go(wait=True)

  return
  #Down
  position ={'right_j6': 3.34944140625, 'right_j5': -1.12391796875, 'right_j4': -1.640046875, 'right_j3': -1.93014453125, 'right_j2': -2.17862109375, 'right_j1': 0.374974609375, 'right_j0': -1.9317626953125}


  group.set_joint_value_target(position)
  plan2 = group.plan()
  group.go(wait=True)

  gripper.open()

  #collision_object = moveit_msgs.msg.CollisionObject()



  ## When finished shut down moveit_commander.
  moveit_commander.roscpp_shutdown()

  ## END_TUTORIAL

  print "============ STOPPING"
  light.set_light_state('head_red_light', False)


if __name__=='__main__':
  try:
    move_group_python_interface_tutorial()
  except rospy.ROSInterruptException:
    pass
