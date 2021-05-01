int serialPin = 2;
int errorPin = 13;

void setup() {
  pinMode(serialPin, OUTPUT);
  pinMode(errorPin, OUTPUT);
  Serial.begin(9600);

  // Test
  digitalWrite(errorPin, HIGH);
  digitalWrite(serialPin, HIGH);
  delay(500);

  // Wait for serial
  do {
    digitalWrite(errorPin, HIGH);
    digitalWrite(serialPin, LOW);
    delay(200);
  } while (!Serial);
  
  // Clear
  digitalWrite(errorPin, LOW);
  digitalWrite(serialPin, HIGH);
}

void loop() {
  digitalWrite(serialPin, HIGH);
  Serial.println("XYZ987");
  delay(1000);
}