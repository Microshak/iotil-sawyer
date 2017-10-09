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
import numpy as np
import intera_interface
import intera_external_devices
from intera_interface import CHECK_VERSION

import pymongo
from pymongo import MongoClient
from std_msgs.msg import Header
from intera_interface import (
    Gripper,
    Lights,
    Cuff,
    RobotParams,
    Head,
)
import uuid

import cv2

import random
import time
import sys
import iothub_client
from iothub_client import IoTHubClient, IoTHubClientError, IoTHubTransportProvider
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError, DeviceMethodReturnValue
#from iothub_client_args import get_iothub_opt, OptionError
import IK
RECEIVE_CONTEXT = 10000
MESSAGE_TIMEOUT = 1000000
RECEIVE_CALLBACKS = 0
IoTHubMessages = []
MINIMUM_POLLING_TIME = 5


def receive_message_callback(message, counter):
    headLight('green')
    
    global RECEIVE_CALLBACKS
    global IoTHubMessages 
   
    message_buffer = message.get_bytearray()
    size = len(message_buffer)
    lit =  ast.literal_eval(message_buffer[:size].decode('utf-8')) 
    print(lit)
    for key in lit:
        print key +"---" +str(lit[key])

    IoTHubMessages.insert(0,lit)
    print(IoTHubMessages[0]["Cartisian.orientation.w"])
    counter += 1
    RECEIVE_CALLBACKS += 1
    headLight('blue')
    
    return IoTHubMessageDispositionResult.ACCEPTED

def headLight(value):
      colors = ["red","blue","green"]
      light = Lights()
      for color in colors:
          light.set_light_state('head_{0}_light'.format(color), on=bool(value == color))


class PlayCommands(object):

  def __init__(self, Name):
    
    CONNECTION_STRING = "HostName=RobotForman.azure-devices.net;DeviceId=PythonTest;SharedAccessKey=oh9Fj0mAMWJZpNNyeJ+bSecVH3cBQwbzjDnoVmeSV5g="
  
    self.protocol=IoTHubTransportProvider.HTTP
    self.client = IoTHubClient(CONNECTION_STRING, self.protocol)
    self.client.set_option("messageTimeout", MESSAGE_TIMEOUT)
    self.client.set_option("MinimumPollingTime", MINIMUM_POLLING_TIME)

    self.client.set_message_callback(receive_message_callback, RECEIVE_CONTEXT)

    
    moveit_commander.roscpp_initialize(sys.argv)
    print 'ROS INIT'
    rospy.init_node('mid' + str(uuid.uuid4().hex), anonymous=True)
    print 'mid' + str(uuid.uuid4().hex)
    self.head_display = intera_interface.HeadDisplay()
    self.headText("Hi")
    self.head = intera_interface.Head()
    rp = RobotParams()
    valid_limbs = rp.get_limb_names()
 
    robot = moveit_commander.RobotCommander()
    rp.max_velocity_scaling_factor = .5    
    scene = moveit_commander.PlanningSceneInterface()

    self.group = moveit_commander.MoveGroupCommander("right_arm")
    
    display_trajectory_publisher = rospy.Publisher('/move_group/display_planned_path',  moveit_msgs.msg.DisplayTrajectory, queue_size=20)
    


    self.light = Lights()
    self.headLight("green")
       
  #  rs = intera_interface.RobotEnable(CHECK_VERSION)
   
    self.group.clear_pose_targets()
    self.endeffector = intera_interface.Gripper("right")

    self.uri = "mongodb://sawyer-mongo:xJENhr8tU9SnRzvn5DVXutJWDsaXBAm6urVHUT6zNirq2ycKx0BQwDbCz6lUqsyYrXc1ENnDIFb3YMTtlE6m5g==@sawyer-mongo.documents.azure.com:10255/?ssl=true"
    self.Mongoclient = MongoClient(self.uri)

    if Name == None:
      self.poleIoTHub()
    else:
      self.completeCommands(Name)
  
  def poleIoTHub(self):
    
      while True:
        if len(IoTHubMessages ) > 0:
          self.handleIoT()
        #rospy.sleep(2)
      

  def headText(self, text):
    img = np.zeros((600,1024,3), np.uint8)
    cv2.putText(img,"Hello World!!!", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)
    cv2.imwrite("/home/microshak/Pictures/head.png",img)
    self.head_display.display_image("/home/microshak/Pictures/head.png", False, 1.0) 
   

  def completeCommands(self, Name):
    db = self.Mongoclient.SawyerDB
    collection = db.Command
           
    data = collection.find({"Name": Name}).sort("Order", pymongo.ASCENDING)


    switch = {
      "Move": lambda x: self.move(x),
      "Gripper": lambda x: self.gripper(x)
     
    }

    print "============Start"
    #rospy.sleep(1)
    ps  = self.group.get_current_pose("right_gripper")
    self.neutral()

    for record in data:
      print IoTHubMessages
      if len(IoTHubMessages ) > 0:
        self.handleIoT()
      self.headLight("green")
      #rospy.sleep(1)
      switch[record["Action"]](record)

  ## When finished shut down moveit_commander.
    moveit_commander.roscpp_shutdown()


  
  def neutral(self):
    limb = intera_interface.Limb("right")
    limb.move_to_neutral() 
    self.headLight("blue")
    self.head_display.display_image("/home/microshak/Pictures/Neutral.png", False, 1.0) 
  def headLight(self,value):
      colors = ["red","blue","green"]
      for color in colors:
          self.light.set_light_state('head_{0}_light'.format(color), on=bool(value == color))

  def gripper(self,data):
    if data["Open"]:
      self.endeffector.open()
      self.head_display.display_image("/home/microshak/Pictures/GripperO.png", False, 1.0) 
    else:
       self.endeffector.close()
       self.head_display.display_image("/home/microshak/Pictures/GripperC.png", False, 1.0) 
  
  def handleIoT(self):
    while len(IoTHubMessages ) > 0:
      self.headLight("red")
      rospy.sleep(1)

      temp = IoTHubMessages.pop()
              
      message = {}
      message["Action"] = temp["Action"]
      message["Order"] = temp["Order"]
      message["FriendlyName"] = temp["FriendlyName"]

    #  print(message) 
      print ("Executing " + message["FriendlyName"])

      if(message["Action"] == "Run"):
       #  message = IoTHubMessages.pop()
         self.completeCommands("Test2") 
         
      if(message["Action"] == "Neutral"):
         self.neutral()
      if(message["Action"] == "Move" ):
          
          
          message["Cartisian"] = {}
          message["Cartisian"]["orientation"] = {}
          message["Cartisian"]["position"] = {}
          
          message["Action"] = temp["Action"]
          message["Speed"] = temp["Speed"]
          message["Cartisian"]["orientation"]["x"] =float(temp["Cartisian.orientation.x"])
          message["Cartisian"]["orientation"]["y"] = float(temp["Cartisian.orientation.y"])
          message["Cartisian"]["orientation"]["z"] = float(temp["Cartisian.orientation.z"])
          message["Cartisian"]["orientation"]["w"] = float(temp["Cartisian.orientation.w"])
          message["Cartisian"]["position"]["x"] = float(temp["Cartisian.position.x"])
          message["Cartisian"]["position"]["y"] = float(temp["Cartisian.position.y"])
          message["Cartisian"]["position"]["z"] = float(temp["Cartisian.position.z"])
        
          self.move(message)
        

      if(message["Action"] == "Stop"):
        stop = True
        self.head_display.display_image("/home/microshak/Pictures/Stop.png", False, 1.0) 
   
        while stop :
          if len(IoTHubMessages)>0:
            message = IoTHubMessages.pop()
            if message["Action"] == "Continue":
              stop = False
              self.head_display.display_image("/home/microshak/Pictures/Resume.png", False, 1.0) 
   
  def receive_message_callback(message, counter):
    global RECEIVE_CALLBACKS
    print "Listening"
    message_buffer = message.get_bytearray()
    size = len(message_buffer)
    lit =  ast.literal_eval(message_buffer[:size].decode('utf-8')) 
    for key in lit:
        self.IotHubMessages.insert({key:lit[key]})
        print key +"---" +str(lit[key])
    
    
    counter += 1
    RECEIVE_CALLBACKS += 1
    return IoTHubMessageDispositionResult.ACCEPTED
    
  
  def receive_message_callback(message):
    global RECEIVE_CALLBACKS
    message_buffer = message.get_bytearray()
    size = len(message_buffer)
    print ( "Received Message [%d]:" % counter )
    print ( "    Data: <<<%s>>> & Size=%d" % (message_buffer[:size].decode('utf-8'), size) )
    map_properties = message.properties()
    key_value_pair = map_properties.get_internals()
    
    print ( "    Properties: %s" % key_value_pair )
    counter += 1
    RECEIVE_CALLBACKS += 1
    print ( "    Total calls received: %d" % RECEIVE_CALLBACKS )
    return IoTHubMessageDispositionResult.ACCEPTED
  


  def move(self, message):
    self.head_display.display_image("/home/microshak/Pictures/Moving.png", False, 1.0) 
    
    print "MOVING!!!!!!!!!!!!!!!!!"
    print(message)
    position = ast.literal_eval(json.dumps(message['Cartisian']))
    speed = message['Speed']
    print(position)
    p =  position["position"]
    o = position["orientation"]
    pose_target = geometry_msgs.msg.Pose()
    pose_target.orientation.w = o["w"]
    pose_target.orientation.x =  o["x"]
    pose_target.orientation.y =  o["y"]
    pose_target.orientation.z = o["z"]
    pose_target.position.x = p["x"]
    pose_target.position.y = p["y"]
    pose_target.position.z = p["z"]


    if(speed == '' or speed == '1'):
      print pose_target
      group = moveit_commander.MoveGroupCommander("right_arm")
      group.set_pose_target(pose_target)
      plan2 = group.plan()
      group.go(wait=True)
    else:
      ik = IK.IK()
      hdr = Header(stamp=rospy.Time.now(), frame_id='base')
      pose_stamp = geometry_msgs.msg.PoseStamped()
      pose_stamp.pose = pose_target
      
      
      success,joints = ik.ik_service_client(pose_stamp,rospy)
      limb_joints = dict(zip(joints.joints[0].name, joints.joints[0].position))
      limb = intera_interface.Limb("right")
      limb.set_joint_position_speed(float(speed))
      limb.move_to_joint_positions(limb_joints, timeout=20.0,threshold=intera_interface.settings.JOINT_ANGLE_TOLERANCE)


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
