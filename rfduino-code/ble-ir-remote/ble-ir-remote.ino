/*
* IRremote: IRsendDemo - demonstrates sending IR codes with IRsend
* An IR LED must be connected to Arduino PWM pin 3.
* Version 0.1 July, 2009
* Copyright 2009 Ken Shirriff
* http://arcfn.com
*/

#include <IRremote.h>
#include <IRCodes.h>

#include <RFduinoBLE.h>

IRsend irsend;



void setup()
{
	RFduinoBLE.advertisementInterval = 1000; //ms
	RFduinoBLE.deviceName = "ACRemote";
	RFduinoBLE.txPowerLevel = -20;  // minimum power tx
	RFduinoBLE.advertisementData = "INIT"

	//start BLE stack
	RFduinoBLE.begin();
}

void loop() {
	RFduino_ULPDelay(INFINITE);
}

void RFduinoBLE_onAdvertisement()
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
	/*	BLE comms prototcol

		The RFDuino is a dumb pipe - no state is maintained on the device; it simply exists to guarantee transmission of IR commands.
		
		The host will send two-byte messages, where 
			(unsigned char)data[0] is the IR command
			(unsigned char)data[1] is the number of times the IR command should be repeated

		commands list:
			0	Invalid
			1	on/stop
			2	
	
	*/
}


