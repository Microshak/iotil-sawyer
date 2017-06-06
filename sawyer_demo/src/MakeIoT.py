#!/usr/bin/env python

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

import pymongo
from pymongo import MongoClient

from intera_interface import (
    Gripper,
    Lights,
    Cuff,
    RobotParams,
    Head,
)
import uuid

class PlayCommands(object):

  def __init__(self, Name):
    
    moveit_commander.roscpp_initialize(sys.argv)
    rospy.init_node('mid' + str(uuid.uuid4().hex) ,     anonymous=True)

    self.head_display = intera_interface.HeadDisplay()
    self.head_display.display_image("/home/microshak/Pictures/Ready.png", False, 1.0) 
    self.head = intera_interface.Head()
    self.head.set_pan(0.5,1.0)
    self.head.set_pan(-0.5,1.0)
    rp = RobotParams()
    valid_limbs = rp.get_limb_names()
 
    robot = moveit_commander.RobotCommander()
        
    scene = moveit_commander.PlanningSceneInterface()

    self.group = moveit_commander.MoveGroupCommander("right_arm")

    
    display_trajectory_publisher = rospy.Publisher('/move_group/display_planned_path',  moveit_msgs.msg.DisplayTrajectory, queue_size=20)

     
  

    uri = "mongodb://sawyer-mongo:xJENhr8tU9SnRzvn5DVXutJWDsaXBAm6urVHUT6zNirq2ycKx0BQwDbCz6lUqsyYrXc1ENnDIFb3YMTtlE6m5g==@sawyer-mongo.documents.azure.com:10255/?ssl=true"
    client = MongoClient(uri)
  
    db = client.SawyerDB
    collection = db.Command
           
    data = collection.find({"Name": Name}).sort("Order", pymongo.ASCENDING)
    
   
       

   # light = Lights()
   # light.set_light_state('head_red_light', True)
       
  #  rs = intera_interface.RobotEnable(CHECK_VERSION)
  

   
    self.group.clear_pose_targets()

  ## Then, we will get the current set of joint values for the group
   # group_variable_values = self.group.get_current_joint_values()
  #print "============ Joint values: ", group_variable_values

 
    self.endeffector = intera_interface.Gripper("right")
 #   print "============close"
  #gripper.reboot()
  #gripper.calibrate()
 # gripper.close()
  #gripper.open()
  #return


    switch = {
      "Move": lambda x: self.move(x),
      "Gripper": lambda x: self.gripper(x),
      "Neutral":lambda x:self.neutral(x)
    }

    print "============Start"
    rospy.sleep(1)
    ps  = self.group.get_current_pose("right_gripper")
    
    for record in data:
      rospy.sleep(1)
      switch[record["Action"]](record)

   # limb = intera_interface.Limb("right")
   # limb.move_to_neutral() 
   #  collision_object = moveit_msgs.msg.CollisionObject()

  ## When finished shut down moveit_commander.
   # moveit_commander.roscpp_shutdown()


 #Referee Point
   # self.jointpos =  data['Joints']
   # return

  #Down
#    limb = intera_interface.Limb("right")
#    limb.move_to_neutral()
  def gripper(self,data):
    if data["Open"]:
      self.endeffector.open()
      self.head_display.display_image("/home/microshak/Pictures/GripperO.png", False, 1.0) 
    else:
       self.endeffector.close()
       self.head_display.display_image("/home/microshak/Pictures/GripperC.png", False, 1.0) 
  
  def move(self, jointpos):
    self.head_display.display_image("/home/microshak/Pictures/Moving.png", False, 1.0) 
    
    print "MOVING!!!!!!!!!!!!!!!!!"

    position = ast.literal_eval(json.dumps(jointpos['Joints']))

    
    
    group = moveit_commander.MoveGroupCommander("right_arm")

    
    group.set_joint_value_target(position)
    plan2 = group.plan()
    group.go(wait=True)

    '''  

  ## END_TUTORIAL

  print "============ STOPPING"
  #light.set_light_state('head_red_light', False)
  '''

def main():
 
  arg_fmt = argparse.RawDescriptionHelpFormatter
  parser = argparse.ArgumentParser(formatter_class=arg_fmt,
                                     description=main.__doc__)
    
  parser.add_argument('-n', '--name', dest='name')
  args = parser.parse_args(rospy.myargv()[1:])


  
  print "Init"
  
  command =  PlayCommands(args.name)
 # command.move(command.jointpos)

   
  return 0

if __name__ == '__main__':
    sys.exit(main())
O