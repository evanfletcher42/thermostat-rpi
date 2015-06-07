import os, time

__CMD_RECV_DELAY = 0.3

def toggleOnOff():
    os.system("irsend SEND_ONCE GE_AirConditioner on_stop")
    time.sleep(__CMD_RECV_DELAY)
    
def setCoolMode():
    os.system("irsend SEND_ONCE GE_AirConditioner cool")
    time.sleep(__CMD_RECV_DELAY)
    
def setFanMode():
    os.system("irsend SEND_ONCE GE_AirConditioner fan")
    time.sleep(__CMD_RECV_DELAY)
    
def setFanHi():
    os.system("irsend SEND_ONCE GE_AirConditioner hi")
    time.sleep(__CMD_RECV_DELAY)
    
def setFanMed():
    os.system("irsend SEND_ONCE GE_AirConditioner mid")
    time.sleep(__CMD_RECV_DELAY)
    
def setFanLow():
    os.system("irsend SEND_ONCE GE_AirConditioner low")
    time.sleep(__CMD_RECV_DELAY)
    
def tempInc(n=1):
    for i in range(0,n):
        os.system("irsend SEND_ONCE GE_AirConditioner tempup")
        time.sleep(__CMD_RECV_DELAY)

def tempDec(n=1):
    for i in range(0,n):
        os.system("irsend SEND_ONCE GE_AirConditioner tempdown")
        time.sleep(__CMD_RECV_DELAY)
    
def timerOn():
    os.system("irsend SEND_ONCE GE_AirConditioner timeron")
    time.sleep(__CMD_RECV_DELAY)
        
def timerOff():
    os.system("irsend SEND_ONCE GE_AirConditioner timeroff")
    time.sleep(__CMD_RECV_DELAY)

def sleep():
    os.system("irsend SEND_ONCE GE_AirConditioner sleep")
    time.sleep(__CMD_RECV_DELAY)