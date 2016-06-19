#!/usr/bin/env python
# Evan Fletcher - June 2016
# 
# Tests running commands on the BLE IR remote for the GE air conditioner.
# Functionality intended to eventually replace the LIRC stuff in the thermostat.
#

import pexpect
import sys
import time
from datetime import datetime
    
# Bluetooth address for the RFDuino.

RFDuinoAddr = "E8:2D:53:E1:47:3E"
    
def reconnect(tool):
    print "Reconnecting..."
    tool.sendline('connect')
    tool.expect('Connection successful.*\[LE\]>')

#Connect to all devices
tool = pexpect.spawn('gatttool -b ' + RFDuinoAddr + ' -t random --interactive')
tool.expect('\[LE\]>')
print "Connecting to RFDuino..."
tool.sendline('connect')
tool.expect('Connection successful.*\[LE\]>')
print "Connected."

time.sleep(10)

#Send a sequence of commands for testing

#cool
tool.sendline('char-write-cmd 0x0011 0201')
tool.expect('\[LE\]>')  
time.sleep(1)

#temp up 10
for i in range(10):
    tool.sendline('char-write-cmd 0x0011 0401')
    tool.expect('\[LE\]>')  
    time.sleep(0.5)
    
# temp down 10
for i in range(10):
    tool.sendline('char-write-cmd 0x0011 0501')
    tool.expect('\[LE\]>')  
    time.sleep(0.5)
    
tool.sendline('char-write-cmd 0x0011 0301')
tool.expect('\[LE\]>')  

tool.sendline('disconnect')
tool.expect('\[LE\]>')  
tool.sendline('exit')

