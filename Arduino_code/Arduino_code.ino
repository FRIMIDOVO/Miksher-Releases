#include <HID-Project.h>

const int threshold = 10;
const unsigned long debounceTime = 25;

const int buttonPins[] = {2,3,4,5,6,7};
int buttonStates[6]={HIGH,HIGH,HIGH,HIGH,HIGH,HIGH};
unsigned long lastPressTime[6]={0,0,0,0,0,0};

const int potPins[] = {A0,A1,A3,A2};
int lastRaw[4]={-1,-1,-1,-1};
int lastMapped[4]={-1,-1,-1,-1};
int potMapMax[4]={103,-3,-3,-3};
int potMapMin[4]={-3,103,103,103};

const int ledMutePin=9;
const int ledMPin=8;

String serialBuffer = "";

void setup(){
    Serial.begin(9600);
    Consumer.begin();
    for(int i=0;i<6;i++) pinMode(buttonPins[i],INPUT_PULLUP);
    pinMode(ledMutePin,OUTPUT);
    pinMode(ledMPin,OUTPUT);
    digitalWrite(ledMutePin,LOW);
    digitalWrite(ledMPin,LOW);
}

void loop(){
    handleButtonSerial(2,'P');
    handleButtonSerial(3,'S');
    handleButtonSerial(4,'N');
    handleButtonSerial(5,'K');

    handleLEDButtonSend(0,'V');
    handleLEDButtonSend(1,'M');

    handlePotValues();

    handleLEDButtonReceive();
}

void handleButton(int index,int code){
    int state=digitalRead(buttonPins[index]);
    unsigned long now=millis();
    if(state!=buttonStates[index]&&state==LOW&&(now-lastPressTime[index]>debounceTime)){
        Consumer.write(code);
        lastPressTime[index]=now;
    }
    buttonStates[index]=state;
}

void handleButtonSerial(int index,char msg){
    int state=digitalRead(buttonPins[index]);
    unsigned long now=millis();
    if(state!=buttonStates[index]&&state==LOW&&(now-lastPressTime[index]>debounceTime)){
        Serial.println(msg);
        lastPressTime[index]=now;
    }
    buttonStates[index]=state;
}

void handleLEDButtonSend(int index,char msg){
    int state=digitalRead(buttonPins[index]);
    unsigned long now=millis();
    if(state!=buttonStates[index]&&state==LOW&&(now-lastPressTime[index]>debounceTime)){
        Serial.println(msg);
        lastPressTime[index]=now;
    }
    buttonStates[index]=state;
}

void handleLEDButtonReceive(){
    while(Serial.available()){
        char c = Serial.read();
        if(c=='\n'){
            serialBuffer.trim();
            if(serialBuffer=="V1") digitalWrite(ledMutePin,HIGH);
            else if(serialBuffer=="V0") digitalWrite(ledMutePin,LOW);
            else if(serialBuffer=="M1") digitalWrite(ledMPin,HIGH);
            else if(serialBuffer=="M0") digitalWrite(ledMPin,LOW);
            serialBuffer="";
        } else serialBuffer += c;
    }
}

void handlePotValues(){
    for(int i=0;i<4;i++){
        int raw= 
        if(lastRaw[i]==-1) lastRaw[i]=raw;
        if(abs(raw-lastRaw[i])>threshold){
            int mapped=map(raw,0,1023,potMapMin[i],potMapMax[i]);
            if(mapped!=lastMapped[i]){
                Serial.print((char)('A'+i));
                Serial.println(mapped/100.0);
                lastMapped[i]=mapped;
            }
            lastRaw[i]=raw;
        }
    }
}
