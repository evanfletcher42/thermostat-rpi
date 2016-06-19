/*
* IRremote: IRsendDemo - demonstrates sending IR codes with IRsend
* An IR LED must be connected to Arduino PWM pin 3.
* Version 0.1 July, 2009
* Copyright 2009 Ken Shirriff
* http://arcfn.com
*/

#include "IRCodes.h"
#include "IRremote.h"
#include <RFduinoBLE.h>

IRsend irsend;

// must be an even number!  commands are 2 bytes
#define CMD_BUFFER_SIZE 128
uint8_t cmdBuffer[CMD_BUFFER_SIZE];
int cbWritePtr = 0;
int cbReadPtr = 0;

void setup()
{
  //Serial.begin(9600);
	RFduinoBLE.advertisementInterval = 500; //ms
	RFduinoBLE.deviceName = "ACRemote";

	//start BLE stack
	RFduinoBLE.begin();
}

void loop() {
  if(cbWritePtr != cbReadPtr)
  {
    if (cmdBuffer[cbReadPtr] > INVALID && cmdBuffer[cbReadPtr] < CMD_END)
    {
      uint8_t command = cmdBuffer[cbReadPtr];
      uint8_t repeats = cmdBuffer[cbReadPtr+1];
      cbReadPtr = (cbReadPtr + 2) % CMD_BUFFER_SIZE;
      
      for (int i = 0; i < repeats; i++)
        sendIR((int)command);
  
    }
  }
}

void RFduinoBLE_onAdvertisement(bool start)
{
}

void RFduinoBLE_onConnect()
{
}

void RFduinoBLE_onDisconnect()
{
}

void RFduinoBLE_onReceive(char* data, int len)
{
	// Note - this is an interrupt and IR commands may take a "long" time.  
	// Should really buffer commands + process in main loop

	/*	BLE comms prototcol

		The RFDuino is a dumb pipe - no state is maintained on the device; it simply exists to guarantee transmission of IR commands.
		
		The host will send two-byte messages, where 
			(unsigned char)data[0] is the IR command
			(unsigned char)data[1] is the number of times the IR command should be repeated

		The IRCommands enum in IRCodes.h contains the list of commands.
	*/

  cmdBuffer[cbWritePtr] = (uint8_t)data[0];
  cmdBuffer[cbWritePtr+1] = (uint8_t)data[1];
  cbWritePtr = (cbWritePtr + 2) % CMD_BUFFER_SIZE;
}


