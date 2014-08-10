import os

def toggleOnOff():
    os.system("irsend SEND_ONCE GE_AirConditioner on_stop")
    
def setCoolMode():
    os.system("irsend SEND_ONCE GE_AirConditioner cool")
    
def setFanMode():
    os.system("irsend SEND_ONCE GE_AirConditioner fan")
    
def setFanHi():
    os.system("irsend SEND_ONCE GE_AirConditioner hi")
    
def setFanMed():
    os.system("irsend SEND_ONCE GE_AirConditioner mid")
    
def setFanLow():
    os.system("irsend SEND_ONCE GE_AirConditioner low")
    
def tempInc(n=1):
    for i in range(0,n):
        os.system("irsend SEND_ONCE GE_AirConditioner tempup")

def tempDec(n=1):
    for i in range(0,n):
        os.system("irsend SEND_ONCE GE_AirConditioner tempdown")
    
def timerOn():
    os.system("irsend SEND_ONCE GE_AirConditioner timeron")
        
def timerOff():
    os.system("irsend SEND_ONCE GE_AirConditioner timeroff")

def sleep():
    os.system("irsend SEND_ONCE GE_AirConditioner sleep")