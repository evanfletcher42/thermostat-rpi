import os, time

# Delay in seconds after sending a set of commands, before sending the next.
__CMD_RECV_DELAY = 0.25

# Number of times a command should be sent in quick succession prior to delay.  Increases odds of reception.
# Does not apply to commands which have state (i.e on_stop)
__N_SEND = 5;

def toggleOnOff():
    os.system("irsend SEND_ONCE GE_AirConditioner on_stop")
    time.sleep(__CMD_RECV_DELAY)
    
def setCoolMode():
    for x in range(0, __N_SEND):
        os.system("irsend SEND_ONCE GE_AirConditioner cool")
    time.sleep(__CMD_RECV_DELAY)
    
def setFanMode():
    for x in range(0, __N_SEND):
        os.system("irsend SEND_ONCE GE_AirConditioner fan")
    time.sleep(__CMD_RECV_DELAY)
    
def setFanHi():
    for x in range(0, __N_SEND):
        os.system("irsend SEND_ONCE GE_AirConditioner hi")
    time.sleep(__CMD_RECV_DELAY)
    
def setFanMed():
    for x in range(0, __N_SEND):
        os.system("irsend SEND_ONCE GE_AirConditioner mid")
    time.sleep(__CMD_RECV_DELAY)
    
def setFanLow():
    for x in range(0, __N_SEND):
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