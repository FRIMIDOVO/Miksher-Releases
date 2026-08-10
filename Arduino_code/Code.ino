#include <HID-Project.h>
#include <MIDIUSB.h>

const short threshold = 10;

const short ButtPins[11] = {2, 3, 4, 5, 6, 7, 8, 9, 16, 14, 15};
const char ButtCommands[11] = {'P', 'S', 'N', 'K', 'A', 'B', 'U', 'D', 'R', 'L', 'C'};
const byte ButtNotes[11] = {60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70};
short ButtState[11] = {HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH};
unsigned long lastPressTime[11] = {0};

const short LedPin = 10;

const short PotPins[4] = {A0, A1, A3, A2};
const char PotCommands[4] = {'a', 'b', 'c', 'd'};
const byte PotCC[4] = {7, 10, 11, 12};
const short PotMidiMax[4] = {127, 127,127, 127};
const short PotMidiMin[4] = {0};
const short PotMax[4]={103,-3,-3,-3};
const short PotMin[4]={-3,103,103,103};
short PotLastVal[4] = {0};

String serialBuffer = "";

bool IsMidi = false;

void setup() {
  Serial.begin(9600);
  for(int i = 0; i < 11; i++) pinMode(ButtPins[i], INPUT_PULLUP);
  pinMode(LedPin, OUTPUT);
  digitalWrite(LedPin, HIGH);
  waitConnect();
}

void loop() {
  if (!IsMidi) {
    handleButt();
    handlePot();
  } else {
    MidiButt();
    MidiPot();
  }
  readSerial();
  handleSerial();
}

void handleSerial() {

}

void readSerial() {
  if (Serial.available())
    serialBuffer += (char)Serial.read();
}

void MidiButt() {
  short state = HIGH;
  unsigned long nowTime = 0;
  for (short i = 0; i < 11; i++) {
    state = digitalRead(ButtPins[i]);
    nowTime = millis();
    if (state != ButtState[i] && (nowTime - lastPressTime[i]) > threshold) {
      if (state == LOW)
        MIDI.sendNoteOn(ButtNotes[i], 127, 1);
      else
        MIDI.sendNoteOff(ButtNotes[i], 0, 1);
      lastPressTime[i] = nowTime;
      ButtState[i] = state;
  }
}

void MidiPot() {
  short raw = 0;
  short val = 0;
  for (short i = 0; i < 4; i++) {
    raw = analogRead(PotPins[i]);
    val = map(raw, 0, 1023, PotMidiMin[i], PotMidiMax[i]);
    if (val != PotLastVal[i]) {
      MIDI.sendControlChange(PotCC[i], val, 1);
      PotLastVal[i] = val;
    }
  }
}

void handlePot() {
  short raw = 0;
  short val = 0;
  for (short i = 0; i < 4; i++) {
      raw = analogRead(PotPins[i]);
      val = map(raw, 0, 1023, PotMin[i], PotMax[i]);
      if (val != PotLastVal[i]) {
        Serial.print(PotCommands[i]);
        Serial.println(val);
        PotLastVal[i] = val;
      }
  }
}

void handleButt() {
  short state = HIGH;
  unsigned long nowTime = 0;
  for (short i = 0; i < 11; i++) {
    state = digitalRead(ButtPins[i]);
    nowTime = millis();
    if (nowTime - lastPressTime[i] > threshold && state == LOW && state != ButtState[i]) {
      Serial.println(ButtCommands[i]);
      blink(100);
      lastPressTime[i] = nowTime;
      ButtState[i] = state;
    } else if(state != ButtState[i])
      ButtState[i] = state;
  }
}

void waitConnect() {
  bool connected = false;
  digitalWrite(LedPin, LOW);
  do {
    if(Serial.available()) {
      digitalWrite(LedPin, HIGH);
      serialBuffer += (char)Serial.read();
      if (serialBuffer.startsWith("C"))
        connected = true;
        serialBuffer.remove(0, 1);
      delay(700);
      digitalWrite(LedPin, LOW);
    }
  } while (!connected);
  delay(1000);
  blink(350);
}

void blink(short time, short n = 1) {
  for (short i = 0; i < n; i++){
    digitalWrite(LedPin, HIGH);
    delay(time);
    digitalWrite(LedPin, LOW);
    if (i < n - 1) delay(time);
  }
}
