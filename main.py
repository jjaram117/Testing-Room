#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile

from pybricks.iodevices import AnalogSensor, UARTDevice
import urequests as requests
import time
import ubinascii, ujson, urequests, utime


# Write your program here
ev3 = EV3Brick()
ev3.speaker.beep()


#----------------------------SYSTEMLINK SETUP----------------------------#    
#Key = 'Fho3wifQ4jSl4P6c_8pp0-UmJgXTDfysc3LTTGbpMk'
Key = 'bvd8X9LweQY9o2eP1NYL-p8mLL9wMAk6YYOnYSiIo0'

# Functions for Tags
def SL_setup():
     urlBase = "https://api.systemlinkcloud.com/nitag/v2/tags/"
     headers = {"Accept":"application/json","x-ni-api-key":Key}
     return urlBase, headers
     
def Put_SL(Tag, Type, Value):
     urlBase, headers = SL_setup()
     urlValue = urlBase + Tag + "/values/current"
     propValue = {"value":{"type":Type,"value":Value}}
     try:
          reply = urequests.put(urlValue,headers=headers,json=propValue).text
     except Exception as e:
          print(e)         
          reply = 'failed'
     return reply

def Get_SL(Tag):
     urlBase, headers = SL_setup()
     urlValue = urlBase + Tag + "/values/current"
     try:
          value = urequests.get(urlValue,headers=headers).text
          data = ujson.loads(value)
          #print(data)
          result = data.get("value").get("value")
     except Exception as e:
          print(e)
          result = 'failed'
     return result
     
def Create_SL(Tag, Type):
     urlBase, headers = SL_setup()
     urlTag = urlBase + Tag
     propName={"type":Type,"path":Tag}
     try:
          urequests.put(urlTag,headers=headers,json=propName).text
     except Exception as e:
          print(e)

#Setting Mine and Next person's "StartXX" tag to "false"
Put_SL('Start02','BOOLEAN','false')
Put_SL('Start03','BOOLEAN','false')  

#Communication Tags with Pycharm
Put_SL('TakePicture','BOOLEAN','false')
Put_SL('FoundTarget','BOOLEAN','false')

#----------------------------EV3 SETUP----------------------------#
#ClawBot Movement Functions
def Not_Target():
     ev3.speaker.beep()
     Wheel_Motor.run_angle(600, WheelAngle)
     Wheel_Motor.stop(Stop.BRAKE)    
     print('Wrong Target')
     wait(800)

def Is_Target():
     Belt_Motor.run_angle(beltSpeed, beltAngle) #Elevator moves down
     Belt_Motor.stop(Stop.BRAKE)
     wait(600)
     
     Claw_Motor.run_angle(500,-clawAngle) #Claw closes
     Claw_Motor.stop(Stop.BRAKE)
     wait(600)

     Belt_Motor.run_angle(beltSpeed, -beltAngle) #Claw comes back up
     wait(600)

     Wheel_Motor.run_angle(600, (NumItems-counter)*WheelAngle) #Bot moves to target, accounting for current position
     wait(600)   
     Claw_Motor.run_angle(1000,clawAngle) #Claw opens

     wait(500)          
     Wheel_Motor.run_angle(1000, -(NumItems-1)*WheelAngle) #Bot moves back to the starting point
     
     Put_SL('Start02','BOOLEAN','false')  #Reseting my Start02 tag to false
     Put_SL('Start03','BOOLEAN','true') #Updates tag to start up next persons bot


#Setting up physical components 
Belt_Motor = Motor(Port.C)
Claw_Motor = Motor(Port.D)
Wheel_Motor = Motor(Port.B)
GoButton = TouchSensor(Port.S1)

#Variables used for components
beltSpeed = 300
beltAngle = 230
WheelAngle = -500
clawAngle = 1050
NumItems = 5
counter = 1  #counter keeps track of how many pallets have been passed over
waitTime = 8000

#----------------------------MAIN CODE----------------------------#
while True:
     #Waiting for the input from Systemlink
     if Get_SL('Start02') == 'true':    
          Put_SL('TakePicture','BOOLEAN','true') #Tell Pycharm to take picture
          Put_SL('FoundTarget','BOOLEAN','false') #Resets tag just to be safe
          ev3.speaker.beep()


          # #Need intermediary tag to wait until running next part?
          # wait(31000)  #I'll just try experimenting w/ this number

          # #Actions based on whether we've found target or not
          # if Get_SL('FoundTarget') == 'true': #if the correct target is scanned
          #      Put_SL('FoundTarget','BOOLEAN','false') #Resets the FoundTarget tag
          #      Is_Target()
          #      counter = 1  #Resets pallet count so program can be rerun

          # else:
          #      Not_Target()
          #      counter = counter + 1  #Increases the pallet count
          #      continue  #Run through loop until target is found



          for n in range(1):
               wait(waitTime)
               Not_Target()
               counter = counter + 1

          wait(waitTime)
          Is_Target()
          counter = 1

          Put_SL('Start02','BOOLEAN','false')  #Reseting my Start02 tag to false
          Put_SL('Start03','BOOLEAN','true')