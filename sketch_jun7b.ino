void setup() {
}

byte duty;

void loop() {
  analogWrite(10, duty);
  duty++;
  if (duty < 254) {
    delay(100);
  } else {
    delay(5000);
  }
}