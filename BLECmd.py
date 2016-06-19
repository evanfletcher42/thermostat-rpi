#!/usr/bin/env python
# Evan Fletcher - June 2016
# 
# Manage communication with RFduino for AC unit control.
import pexpect
import sys
import time
    
# Bluetooth address for the RFDuino.
RFduinoAddr = "E8:2D:53:E1:47:3E"

# Delay in seconds after sending a set of commands, before sending the next.
__CMD_RECV_DELAY = 0.25

# The pexpect instance used for gatttool
tool = None
    
def connect():
    global tool
    print "Connecting to RFduino..."
    tool.sendline('connect')
    tool.expect('Connection successful.*\[LE\]>')
    print "Connected."
    
    
def initRF():
    global tool
    tool = pexpect.spawn('gatttool -b ' + RFduinoAddr + ' -t random --interactive')
    tool.expect('\[LE\]>')
    connect()
    
def disconnectRF():
    global tool
    tool.sendline('disconnect')
    tool.expect('\[LE\]>')  
    
# ------ Command defs, to be called by syscontrol ------
# TODO: Handle disconnect/reconnect

def toggleOnOff():
    global tool
    tool.sendline('char-write-cmd 0x0011 0101')
    tool.expect('\[LE\]>')  
    time.sleep(__CMD_RECV_DELAY)
    
def setCoolMode():
    global tool
    tool.sendline('char-write-cmd 0x0011 0201')
    tool.expect('\[LE\]>')  
    time.sleep(__CMD_RECV_DELAY)
    
def setFanMode():
    global tool
    tool.sendline('char-write-cmd 0x0011 0301')
    tool.expect('\[LE\]>')  
    time.sleep(__CMD_RECV_DELAY)
    
def setFanHi():
    global tool
    tool.sendline('char-write-cmd 0x0011 0801')
    tool.expect('\[LE\]>')  
    time.sleep(__CMD_RECV_DELAY)
    
def setFanMed():
    global tool
    tool.sendline('char-write-cmd 0x0011 0901')
    tool.expect('\[LE\]>')  
    time.sleep(__CMD_RECV_DELAY)
    
def setFanLow():
    global tool
    tool.sendline('char-write-cmd 0x0011 0A01')
    tool.expect('\[LE\]>')  
    time.sleep(__CMD_RECV_DELAY)
    
def tempInc(n=1):
    global tool
    for i in range(n):
        tool.sendline('char-write-cmd 0x0011 0401')
        tool.expect('\[LE\]>')  
        time.sleep(__CMD_RECV_DELAY)

def tempDec(n=1):
    global tool
    for i in range(n):
        tool.sendline('char-write-cmd 0x0011 0501')
        tool.expect('\[LE\]>')  
        time.sleep(__CMD_RECV_DELAY)
    
def timerOn():
    global tool
    tool.sendline('char-write-cmd 0x0011 0601')
    tool.expect('\[LE\]>')  
    time.sleep(__CMD_RECV_DELAY)
        
def timerOff():
    global tool
    tool.sendline('char-write-cmd 0x0011 0701')
    tool.expect('\[LE\]>')  
    time.sleep(__CMD_RECV_DELAY)

def sleep():
    global tool
    tool.sendline('char-write-cmd 0x0011 0B01')
    tool.expect('\[LE\]>')  
    time.sleep(__CMD_RECV_DELAY)