#!/usr/bin/env python

import argparse
import sys
import uuid
import rospy
import intera_interface

from intera_interface import (
    Gripper,
    Lights,
    Cuff,
    RobotParams,
    Navigator,
)
import pymongo
from pymongo import MongoClient
import datetime

from intera_core_msgs.srv import (
    SolvePositionFK,
    SolvePositionFKRequest,
)

from std_msgs.msg import Header
from sensor_msgs.msg import JointState

import json, ast









class RecordMotion(object):


    def __init__(self, arm, name,start):

        #Mongo
        uri = "mongodb://sawyer-mongo:xJENhr8tU9SnRzvn5DVXutJWDsaXBAm6urVHUT6zNirq2ycKx0BQwDbCz6lUqsyYrXc1ENnDIFb3YMTtlE6m5g==@sawyer-mongo.documents.azure.com:10255/?ssl=true"
        client = MongoClient(uri)
        
        #Robot
        self.db = client.SawyerDB
        self.collection = self.db.Commands
        self.commandName = name
        self.commandNumber = start
        rp = RobotParams()
        self._lastJoin = {}        
        self.lastButtonPress = datetime.datetime.now()
  
        
        self._rs = intera_interface.RobotEnable()
        self._init_state = self._rs.state().enabled
        print("Enabling robot... ")
        self._rs.enable()
        self._navigator_io = intera_interface.Navigator()

        head_display = intera_interface.HeadDisplay()
        head_display.display_image("/home/microshak/Pictures/Sawyer_Navigator_Main.png", False, 1.0)
    
        valid_limbs = rp.get_limb_names()
        self._arm = rp.get_limb_names()[0]
        self._limb = intera_interface.Limb(arm)
        
        if start == None:
            limb = intera_interface.Limb("right")
            limb.move_to_neutral() 
        
        print(self._arm)
        # inputs
        self._cuff = Cuff(limb='right')
        self._navigator = Navigator()
        # connect callback fns to signals
        self._lights = None
        self._lights = Lights()
        self._cuff.register_callback(self._light_action,'{0}_cuff'.format('right'))
        try:
            self._gripper = Gripper(self._arm)
            #if not (self._gripper.is_calibrated() or self._gripper.calibrate() == True):
            #  rospy.logerr("({0}_gripper) calibration failed.".format(self._gripper.name))
            #  raise
        
            
        except:
            self._gripper = None
            msg = ("{0} Gripper is not connected to the robot."
                   " Running cuff-light connection only.").format(arm.capitalize())
            rospy.logwarn(msg)

     

    def clean_shutdown(self):
        print("\nExiting example...")
        if not self._init_state:
            print("Disabling robot...")
       # self._rs.disable()
        return True
   
    def record(self):


     


      self._cuff.register_callback(self._close_action,'{0}_button_upper'.format(self._arm))
      self._cuff.register_callback(self._open_action,'{0}_button_lower'.format(self._arm))
      print "Registering COntrols"
      ok_id = self._navigator.register_callback(self._record_spot, 'right_button_ok')# The circular button in the middle of the navigator.
      circle_id = self._navigator.register_callback(self._record_OK, 'right_button_circle')#The button above the OK button, typically with a 'Back' arrow symbol. 
      show_id = self._navigator.register_callback(self._record_start, 'right_button_show')#The "Rethink Button", is above the OK button, next to back button and typically is labeled with the Rethink logo. 

      while not rospy.is_shutdown():
          rospy.sleep(0.1)

      self._navigator.deregister_callback(ok_id)
      self._navigator.deregister_callback(circle_id)
      self._navigator.deregister_callback(show_id)

    def _record_start(self, value):
        self.headLight("green")

    def _record_OK (self, value):
        self.headLight("red")
        print "recording"

    def _record_spot(self, value):
        time = (datetime.datetime.now() - self.lastButtonPress  ).seconds
        print time
        print "Redording"
        if time < 2:
          #print "time to bail"
          return
        
        self.lastButtonPress  =datetime.datetime.now() 
        print "spot record"
        self.headLight("red")
        self.commandNumber += 1
       
        posts = self.db.Command
        joints = {}
        names = self._limb.joint_names()
        jointpos = JointState()
        jointpos.name = []
        jointpos.position = []
   
        for join in names :
          joints.update({join:self._limb.joint_angle(join)})
          jointpos.name.append(join)
          jointpos.position.append(self._limb.joint_angle(join))
       # if joints == self._lastJoin:
       #     return 0
        cartisian = self.fk_service_client(jointpos).pose_stamp[0].pose
        
        z = cartisian.position.z  - .004377
        carobj = {
            "position":{ 
  "x": cartisian.position.x,
  "y": cartisian.position.y,
  "z": z},
"orientation":{ 
  "x": cartisian.orientation.x,
  "y":  cartisian.orientation.y,
  "z":  cartisian.orientation.z,
  "w": cartisian.orientation.w
    }
        }
        print(carobj)  




        self._lastJoin = joints
        post = {"Name" : self.commandName, "Order" : self.commandNumber, "Action":"Move",  "Cartisian":carobj}
        
        posts.insert(post)
        
        self.headLight("green")

    def _open_action(self, value):
        self.headLight("red")
        if value and self._gripper.is_ready():
            self._gripper.open()
            self.commandNumber += 1
            posts = self.db.Command
            post = {"Name" : self.commandName, "Order" : self.commandNumber, "Action": "Gripper","Open": True }
            posts.insert(post)
            self.headLight("green")

    def _close_action(self, value):
        rospy.logdebug("gripper close triggered")
        
        self.headLight("red")
        if value and self._gripper.is_ready():
            rospy.logdebug("gripper close triggered")
            self._gripper.close()
            self.commandNumber += 1
            posts = self.db.Command
            post = {"Name" : self.commandName, "Order" : self.commandNumber, "Action": "Gripper","Open": False }
            posts.insert(post)
            self.headLight("green")            

    def fk_service_client(self,joints):
        ns = "ExternalTools/right/PositionKinematicsNode/FKService"
        fksvc = rospy.ServiceProxy(ns, SolvePositionFK)
        fkreq = SolvePositionFKRequest()
         # Add desired pose for forward kinematics
        fkreq.configuration.append(joints)
        # Request forward kinematics from base to "right_hand" link
        fkreq.tip_names.append('right_hand')

        try:
            rospy.wait_for_service(ns, 5.0)
            resp = fksvc(fkreq)
            return resp
        except (rospy.ServiceException, rospy.ROSException), e:
            rospy.logerr("Service call failed: %s" % (e,))
            return geometry_msgs.msg.PoseStamped()

    # Check if result valid
        if (resp.isValid[0]):
            rospy.loginfo("SUCCESS - Valid Cartesian Solution Found")
            rospy.loginfo("\nFK Cartesian Solution:\n")
            rospy.loginfo("------------------")
            rospy.loginfo("Response Message:\n%s", resp)
        else:
            rospy.logerr("INVALID JOINTS - No Cartesian Solution Found.")
            return {}
        return resp


    def _light_action(self, value):
        if value:
            rospy.logdebug("cuff grasp triggered")
        else:
            rospy.logdebug("cuff release triggered")
        if self._lights:
            self._set_lights('red', False)
            self._set_lights('green', False)
            self._set_lights('blue', value)

    def _set_lights(self, color, value):
        
        self._lights.set_light_state('head_{0}_light'.format(color), on=bool(value))
        self._lights.set_light_state('{0}_hand_{1}_light'.format(self._arm, color), on=bool(value))
    
    def headLight(self,value):
        colors = ["red","blue","green"]
        for color in colors:
            self._lights.set_light_state('head_{0}_light'.format(color), on=bool(value == color))

    def finalize(self):
        print "ENDING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"



def main():
    rp = RobotParams()
    valid_limbs = rp.get_limb_names()
    if not valid_limbs:
        rp.log_message(("Cannot detect any limb parameters on this robot. "
                        "Exiting."), "ERROR")
        return

    arg_fmt = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(formatter_class=arg_fmt,
                                     description=main.__doc__)
    
    parser.add_argument('-n', '--name', dest='name')
   # args = parser.parse_args(rospy.myargv()[1:])
    parser.add_argument('-s', '--start', dest='start', type=int)
    args = parser.parse_args(rospy.myargv()[1:])


    rospy.init_node("Record" + str(uuid.uuid4().hex),log_level=rospy.ERROR)
    print "Record" + str(uuid.uuid4().hex)
    if args.start == None:
       args.start = 0

    motion = RecordMotion('right', args.name, args.start)

    rospy.on_shutdown(motion.clean_shutdown)
    motion.record()
   
        


    
   
    return 0

if __name__ == '__main__':
    sys.exit(main())
