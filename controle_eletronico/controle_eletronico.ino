#include <Servo.h>

Servo myservo;

char leitura;

void setup() {
  Serial.begin(9600);
  myservo.attach(9);
  myservo.write(0);
}

void loop() {
   if (Serial.available() > 0) {
      leitura = Serial.read();
      if(leitura == 'V') {
         myservo.write(90);
         delay(2500);
         myservo.write(0);
      } else if(leitura == 'F') {
        digitalWrite(4, HIGH);
        myservo.write(0);
        delay(1500);
        digitalWrite(4, LOW);
      }
      else Serial.end();
   }
} 
