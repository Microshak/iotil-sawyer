#!/usr/bin/env python

import argparse
import sys

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


class RecordMotion(object):

    def __init__(self, arm, name):
        uri = "mongodb://sawyer-mongo:xJENhr8tU9SnRzvn5DVXutJWDsaXBAm6urVHUT6zNirq2ycKx0BQwDbCz6lUqsyYrXc1ENnDIFb3YMTtlE6m5g==@sawyer-mongo.documents.azure.com:10255/?ssl=true"
        client = MongoClient(uri)
        self.db = client.SawyerDB
        self.collection = self.db.Commands
        self.commandName = name
        self.commandNumber = 0
        rp = RobotParams()
        self._lastJoin = {}        

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
     #   if not self._init_state:
     #       print("Disabling robot...")
        self._rs.disable()
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
        print "we cool"

    def _record_spot(self, value):
        print "spot record"
        self.headLight("red")
        self.commandNumber += 1
        posts = self.db.Command
        joints = {}
        names = self._limb.joint_names()
        for join in names :
           joints.update({join:self._limb.joint_angle(join)})
        if joints == self._lastJoin:
            return 0

        self._lastJoin = joints
        post = {"Name" : self.commandName, "Order" : self.commandNumber, "Action":"Move", "Joints": joints}
        
        posts.insert(post)
        print post
        
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
    
        self.headLight("red")
        if value and self._gripper.is_ready():
            rospy.logdebug("gripper close triggered")
            self._gripper.close()
            self.commandNumber += 1
            posts = self.db.Command
            post = {"Name" : self.commandName, "Order" : self.commandNumber, "Action": "Gripper","Open": False }
            posts.insert(post)
            self.headLight("green")            

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
    args = parser.parse_args(rospy.myargv()[1:])


    rospy.init_node("MIKERNODE21",log_level=rospy.ERROR)

    motion = RecordMotion('right', args.name)

    rospy.on_shutdown(motion.clean_shutdown)
    motion.record()
   
        


    
   
    return 0

if __name__ == '__main__':
    sys.exit(main())
INFO