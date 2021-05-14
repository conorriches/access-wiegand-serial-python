#include <Wiegand.h>

// Wiegand 
WIEGAND wg;
int buzzer = 5;
int green = 4;

// On board LEDs
int led = 12;
int error = 13;

// Detecting error with reader
int flag = 0; // Has there been an error
int flagThreshold = 100; // When to alarm
int flagReset = 103; // When to reset


void setup() {
  Serial.begin(9600);  
  wg.begin();

  pinMode(green, OUTPUT);
  pinMode(buzzer, OUTPUT);
  pinMode(led, OUTPUT);
  pinMode(error, OUTPUT);

  // For the Wiegand outputs, HIGH means off (ground wire for led)
  digitalWrite(green, HIGH); 
  digitalWrite(buzzer, HIGH);

  digitalWrite(led, HIGH);
  digitalWrite(error, HIGH);
  delay(500);
  digitalWrite(led, LOW);
  digitalWrite(error, LOW);
}

void loop() {
  if(wg.available())
  {
    String code = String(wg.getCode(), HEX);

    // The codes are in the wrong order, so flip them
    for (int i = 7; i >= 0; i-=2) {
      Serial.print(code[i-1]);
      Serial.print(code[i]);
    }
    Serial.println();

  } else{
      // Set green LED if both pins are high
      digitalWrite(led, digitalRead(2) == HIGH && digitalRead(3) == HIGH);
      
      // d0 and d1 are HIGH when there is no data i.e. normal
      if(digitalRead(2) == LOW || digitalRead(3) == LOW){
        if(flag >= flagThreshold) {
          if(flag == flagThreshold){
            Serial.println("READER_ERROR");
          }
          if(flag >= flagReset) {
            flag = flagThreshold - 1;
          }
          for(int i = 0 ; i < 3 ; i ++){
            digitalWrite(error, HIGH);
            delay(500);
            digitalWrite(error, LOW);
            delay(500);
          }
        }
        flag ++;
      } else {
        if(flag > flagThreshold) {
          Serial.println("READER_OK");
        }
        flag = 0;  
      }
  }

  // Check for messages from the Pi
  if(Serial.available() > 0){
    int incomingByte = Serial.read();
    if(incomingByte == 48 ){ // Chatacter 0, i.e. access denied
      for(int i=0 ; i < 3 ; i++){
        digitalWrite(buzzer, LOW);
        delay(500);
        digitalWrite(buzzer, HIGH);
        delay(500);
      }
      delay(1000);
    } else if( incomingByte == 49){ // Character 1, i.e. access granted
      digitalWrite(green, LOW);
      digitalWrite(buzzer, LOW);
      delay(200);
      digitalWrite(buzzer, HIGH);
      delay(3000);
      digitalWrite(green, HIGH);  
    }
  }
}