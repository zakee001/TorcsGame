from cProfile import label
from inspect import ClassFoundException
from xmlrpc.client import boolean
import msgParser
import carState
import carControl
import keyboard
import pandas as pd
import os.path
from sklearn import tree
import numpy as np



import numpy as np

class Driver(object):
    '''
    A driver object for the SCRC
    '''
    


    def __init__(self, stage):
        '''Constructor'''
        self.WARM_UP = 0
        self.QUALIFYING = 1
        self.RACE = 2
        self.UNKNOWN = 3
        self.stage = stage
        
        self.parser = msgParser.MsgParser()
        
        self.state = carState.CarState()
        
        self.control = carControl.CarControl()
        self.filecontent = []
        self.keys = [0,0,0,0]
        self.steer_lock = 0.785398
        self.max_speed = 100
        self.prev_rpm = None

        dataset = pd.read_csv('Testing.csv')
        dataset = dataset.sample(frac=1)
        dataset = dataset.dropna()

        self.rem=['Clutch','Focus','Meta','Damage','Distance Raced','Fuel','RPM']
        for i in self.rem:
            del dataset[i]
        train = dataset.iloc[:,0:78-7]
        labeled =dataset.iloc[:,78-7:]
        self.model = tree.DecisionTreeClassifier()
        self.model = self.model.fit(train,labeled)

    
    def init(self):
        '''Return init string with rangefinder angles'''
        self.angles = [0 for x in range(19)]
        
        for i in range(5):
            self.angles[i] = -90 + i * 15
            self.angles[18 - i] = 90 - i * 15
        
        for i in range(5, 9):
            self.angles[i] = -20 + (i-5) * 5
            self.angles[18 - i] = 20 - (i-5) * 5
        
        return self.parser.stringify({'init': self.angles})
    
    def drive(self, msg):
        self.state.setFromMsg(msg)
        self.write()
        self.steer()
        
        self.gear()
        
        self.speed()


        #self.getData()
        
        return self.control.toMsg()
    def write(self):
        head=["Accel","Brake","Steer","Clutch","Focus","Meta","Angle","Current Lap Time","Damage","Distance from Start","Distance Raced","Fuel","Race Position","RPM","SpeedX","Track Position","SpeedY","Z","SpeedZ","WheelSpinVel 1","WheelSpinVel 2","WheelSpinVel 3","WheelSpinVel 4","Opponent1","Oponent2","Oponent3","Oponent4","Oponent5","Oponent6","Oponent7","Oponent8","Oponent9","Oponent10","Oponent11","Oponent12","Oponent13","Oponent14","Oponent15","Oponent16","Oponent17","Oponent18","Oponent19","Oponent20","Oponent21","Oponent22","Oponent23","Oponent24","Oponent25","Oponent26","Oponent27","Oponent28","Oponent29","Oponent30","Oponent31","Oponent32","Oponent33","Oponent34","Oponent35","Oponent36","track1","track2","track3","track4","track5","track6","track7","track8","track9","track10","track11","track12","track13","track14","track15","track16","track17","track18","track19"]

        filecontent = []
        filecontent.append(self.control.accel)
        filecontent.append(self.control.brake)
        filecontent.append(self.control.steer)
        filecontent.append(self.control.clutch)
        filecontent.append(self.control.focus)
        filecontent.append(self.control.meta)
        filecontent.append(self.state.angle)
        filecontent.append(self.state.curLapTime)
        filecontent.append(self.state.damage)
        filecontent.append(self.state.distFromStart)
        filecontent.append(self.state.distRaced)
        filecontent.append(self.state.fuel)
        filecontent.append(self.state.racePos)
        filecontent.append(self.state.rpm)
        filecontent.append(self.state.speedX)
        filecontent.append(self.state.trackPos)
        filecontent.append(self.state.speedY)
        filecontent.append(self.state.z)
        filecontent.append(self.state.speedZ)
        filecontent.extend(self.state.wheelSpinVel)
        filecontent.extend(self.state.opponents)
        filecontent.extend(self.state.track)
        df = pd.DataFrame([filecontent],columns=head)
        for i in self.rem:
            del df[i]
        pred = self.model.predict(df)
        if pred[0][0]==1:
            self.keys[0]=1
        if pred[0][1]==1:
            self.keys[1]=1
        if pred[0][2]==1:
            self.keys[2]=1
        if pred[0][3]==1:
            self.keys[3]=1

        #print(pred)
        #filecontent.append()
        #self.filecontent.append(filecontent)
        #print(filecontent)
        #with open ('Testing.csv','a') as filehanle:
        #    for items in filecontent:
        #       filehanle.write(str(items)+str(','))
        #    for i in range (0,4):
        #        self.keys[i] =0
               
            

            #filehanle.write('\n')
    def steer(self):
        if self.keys[0]==1:
            angle = self.state.angle
            dist = self.state.trackPos
            self.control.setSteer((angle + 0.33)/self.steer_lock)
            
            

        elif self.keys[1]==1:
            angle = self.state.angle
            dist = self.state.trackPos
            self.control.setSteer((angle - 0.33)/self.steer_lock)
            
            
        else:
            self.control.setSteer(0) 
            angle = self.state.angle
            dist = self.state.trackPos
            
            

        
    
    def gear(self):
        rpm = self.state.getRpm()
        gear = self.state.getGear()
        
        if self.prev_rpm == None:
            up = True
        else:
            if (self.prev_rpm - rpm) < 0:
                up = True
            else:
                up = False
        
        if up and rpm > 7000:
            gear += 1
        
        if not up and rpm < 1000:
            gear -= 1
        
        self.control.setGear(gear)
    
    def speed(self):
        speed = self.state.getSpeedX()
        accel = self.control.getAccel()
        

        #if speed < self.max_speed:
        if self.keys[2]==1:
            accel += 0.1
            if accel > 1:
                accel = 1.0
        if self.keys[3]==1:
                self.control.setBrake(1)
        
        self.control.setAccel(accel)

                
    def getData(self):
        self.state.getGear
        
    def onShutDown(self):
        pass
    
    def onRestart(self):
        pass
        