#!/usr/bin/env python

import argparse
import sys

import rospy

from intera_interface import (
    Gripper,
    Lights,
    Cuff,
    RobotParams,
    Navigator,
)
import speech_recognition as sr
import pyttsx

class GripperConnect(object):
   

    def __init__(self, arm):
     
        rp = RobotParams()
 

def main():
 

    r = sr.Recognizer()
    with sr.Microphone() as source:
        print "Say something!"
        audio = r.listen(source)
    trans = r.recognize_sphinx(audio)
    print trans
    engine = pyttsx.init()
    engine.say(trans)
    engine.runAndWait()


    print("Press cuff buttons for gripper control. Spinning...")
    rospy.spin()
    print("Gripper Button Control Finished.")
    return 0

if __name__ == '__main__':
    sys.exit(main())
