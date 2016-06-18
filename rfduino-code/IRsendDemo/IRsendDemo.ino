/*
 * IRremote: IRsendDemo - demonstrates sending IR codes with IRsend
 * An IR LED must be connected to Arduino PWM pin 3.
 * Version 0.1 July, 2009
 * Copyright 2009 Ken Shirriff
 * http://arcfn.com
 */

#include <IRremote.h>

IRsend irsend;

// works
unsigned char onstop[] = {
  0,1,0,1,0,1,0,1,0,1,0,1,1,0,1,0,1,1,1,1,0,0,1,1,0,0,0,0,1,0,0,0,0,1,0,1,1,0,0,1,1,0,0,0,1,1,1,1
};

//works
unsigned char cool[] = {
  0,1,0,1,0,1,0,1,0,1,0,1,1,0,1,0,1,1,1,1,0,0,1,1,0,0,0,0,1,0,0,0,0,0,0,1,1,1,0,1,1,0,0,0,1,1,1,1
};

//works
unsigned char fan[] = {
  0,1,0,1,0,1,0,1,0,1,0,1,1,0,1,0,1,1,1,1,0,0,1,1,0,0,0,0,1,0,0,0,0,1,0,1,1,1,0,1,1,0,0,0,1,0,1,1
};

//works
unsigned char tempup[] = {
  0,1,0,1,0,1,0,1,0,1,0,1,1,0,1,0,1,1,1,1,0,0,1,1,0,0,0,0,1,0,0,0,1,1,0,1,1,0,0,1,1,0,0,0,0,1,1,1
};

unsigned char tempdown[] = {
  0,1,0,1,0,1,0,1,0,1,0,1,1,0,1,0,1,1,1,1,0,0,1,1,0,0,0,0,1,0,0,0,0,0,0,1,1,0,0,1,1,0,0,0,1,0,1,1
};

unsigned char timeron[] = {
  0,1,0,1,0,1,0,1,0,1,0,1,1,0,1,0,1,1,1,1,0,0,1,1,0,0,0,0,1,0,0,0,1,1,0,1,0,1,0,1,1,0,0,0,1,0,1,1
};

unsigned char timeroff[] = {
  0,1,0,1,0,1,0,1,0,1,0,1,1,0,1,0,1,1,1,1,0,0,1,1,0,0,0,0,1,0,0,0,1,0,0,1,0,1,0,1,1,0,0,0,1,1,1,1
};

unsigned char hi[] = {
  0,1,0,1,0,1,0,1,0,1,0,1,1,0,1,0,1,1,1,1,0,0,1,1,0,0,0,0,1,0,0,0,1,1,0,1,1,1,0,1,1,0,0,0,0,0,1,1
};

unsigned char mid[] = {
  0,1,0,1,0,1,0,1,0,1,0,1,1,0,1,0,1,1,1,1,0,0,1,1,0,0,0,0,1,0,0,0,0,0,1,1,1,1,0,1,1,0,0,0,1,1,0,1
};

unsigned char low[] = {
  0,1,0,1,0,1,0,1,0,1,0,1,1,0,1,0,1,1,1,1,0,0,1,1,0,0,0,0,1,0,0,0,1,0,1,1,1,1,0,1,1,0,0,0,0,1,0,1
};

unsigned char sleep[] = {
  0,1,0,1,0,1,0,1,0,1,0,1,1,0,1,0,1,1,1,1,0,0,1,1,0,0,0,0,1,0,0,0,0,1,0,1,0,1,0,1,1,0,0,0,0,0,1,1
};

void setup()
{
}

void loop() {
  delay(5000);
  irsend.sendGEAC(onstop, 48);   delay(1000);
  irsend.sendGEAC(fan, 48);   delay(1000);
  irsend.sendGEAC(low, 48);   delay(1000);
  irsend.sendGEAC(mid, 48);   delay(1000);
  irsend.sendGEAC(hi, 48);   delay(1000);
  irsend.sendGEAC(low, 48);   delay(1000);
  irsend.sendGEAC(cool, 48);   delay(1000);
  
  for(int i=0; i < 5; i++) {
    irsend.sendGEAC(tempup, 48);   delay(1000); }

  for(int i=0; i < 5; i++) {
    irsend.sendGEAC(tempdown, 48);   delay(1000); }
    
  irsend.sendGEAC(timeron, 48);   delay(1000);
  irsend.sendGEAC(timeroff, 48);   delay(1000);
  irsend.sendGEAC(sleep, 48);   delay(1000);
  irsend.sendGEAC(sleep, 48);   delay(1000);
  irsend.sendGEAC(onstop, 48);   delay(1000);
}

//0x555AF308D897


