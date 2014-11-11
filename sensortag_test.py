#!/usr/bin/env python
# Michael Saunby. April 2013   
# 
# Read temperature from the TMP006 sensor in the TI SensorTag 
# It's a BLE (Bluetooth low energy) device so using gatttool to
# read and write values. 
#
# Usage.
# sensortag_test.py BLUETOOTH_ADR
#
# To find the address of your SensorTag run 'sudo hcitool lescan'
# You'll need to press the side button to enable discovery.
#
# Notes.
# pexpect uses regular expression so characters that have special meaning
# in regular expressions, e.g. [ and ] must be escaped with a backslash.
#

import pexpect
import sys
import time

def floatfromhex(h):
    t = float.fromhex(h)
    if t > float.fromhex('7FFF'):
        t = -(float.fromhex('FFFF') - t)
        pass
    return t
    
# Bluetooth addresses for SensorTags located around the apartment.
# System will connect to and poll all of these.  

sensorTagAddrs = {
    "LivingRoom" :  "B4:99:4C:64:BA:B6"#,
    #"Kitchen"    :  "B4:99:4C:64:AF:9F",
    #"Bedroom"    :  "B4:99:4C:64:26:80"
}

# This algorithm borrowed from 
# http://processors.wiki.ti.com/index.php/SensorTag_User_Guide#Gatt_Server
# which most likely took it from the datasheet.  I've not checked it, other
# than noted that the temperature values I got seemed reasonable.
#
def calcTmpTarget(objT, ambT):
    m_tmpAmb = ambT/128.0
    Vobj2 = objT * 0.00000015625
    Tdie2 = m_tmpAmb + 273.15
    S0 = 6.4E-14            # Calibration factor
    a1 = 1.75E-3
    a2 = -1.678E-5
    b0 = -2.94E-5
    b1 = -5.7E-7
    b2 = 4.63E-9
    c2 = 13.4
    Tref = 298.15
    S = S0*(1+a1*(Tdie2 - Tref)+a2*pow((Tdie2 - Tref),2))
    Vos = b0 + b1*(Tdie2 - Tref) + b2*pow((Tdie2 - Tref),2)
    fObj = (Vobj2 - Vos) + c2*pow((Vobj2 - Vos),2)
    tObj = pow(pow(Tdie2,4) + (fObj/S),.25)
    tObj = (tObj - 273.15)+3.98744  #Offset because this makes no sense at all
    #print "%.2f C" % tObj
    return (m_tmpAmb, tObj)

#Connect to all devices
sensorTagConns = {}
for tag in sensorTagAddrs:
    tool = pexpect.spawn('gatttool -b ' + sensorTagAddrs[tag] + ' --interactive')
    tool.expect('\[LE\]>')
    print "Preparing to connect to", tag, ".  You might need to press the side button..."
    tool.sendline('connect')
    tool.expect('Connection successful.*\[LE\]>')
    sensorTagConns[tag] = tool
    
while True:
    
    for tag in sensorTagConns:
        tool = sensorTagConns[tag]
        
        # Enable sensor and wait for a bit for it to turn on
        tool.sendline('char-write-cmd 0x29 01')
        tool.expect('\[LE\]>')  
        
    time.sleep(0.25)
        
    for tag in sensorTagConns:
        tool = sensorTagConns[tag]
        retry = True
        while retry:        
            # Take reading
            tool.sendline('char-read-hnd 0x25')
            i = tool.expect(['descriptor: .*', 'Disconnected'])
            if i == 0:
                rval = tool.after.split()
                objT = floatfromhex(rval[2] + rval[1])
                ambT = floatfromhex(rval[4] + rval[3])
                print objT, ambT
                #print rval
                #(calcAmbT, calcObjT) = calcTmpTarget(objT, ambT)
                #print tag, "\tamb=", calcAmbT*9/5+32, "\tIR=", calcObjT*9/5+32
            else:
                print "Reconnecting to", tag, "..."
                tool.sendline('connect')
                tool.expect('Connection successful.*\[LE\]>')
                retry = True
                continue
            retry = False;
            
    for tag in sensorTagConns:
        tool = sensorTagConns[tag]
        # Disable sensor (save power)
        tool.sendline('char-write-cmd 0x29 00')
        tool.expect('\[LE\]>')
        retry = False
        
    print
    
    # Wait
    #time.sleep(10)


