#include <Arduino.h> // Импортируем библиотеки
#include <Servo.h> 
#include "settings.h"
#include "drivers.h"


void setup() {
  initServo();
  pinMode(MTROXP, OUTPUT);
  pinMode(MTROXB, OUTPUT);
  pinMode(MTROYP, OUTPUT);
  pinMode(MTROYB, OUTPUT);
  pinMode(STBY, OUTPUT);
  pinMode(AIN1, OUTPUT);
  pinMode(AIN2, OUTPUT);
  pinMode(PWMA, OUTPUT);
  digitalWrite(STBY, HIGH);  // Включаем драйвер для насоса
  Serial.begin(9600);        // Инициализируем сериал-порт для коммуникации с Raspberry Pi
  while (!Serial);  // Код не будет выполняться, пока сериал порт не активируется на Raspberry Pi
}

void loop() {

  if (Serial.available() > 0) {
    String message = Serial.readStringUntil('\n');  // Получаем код от Raspberry Pi когда он появляется
    int now_action = message.toInt();
    // В зависипомти от кода выполняем одно из 7 возможных действий
    if (now_action < 4) {  // Движение мотора, отвечающего за ось ОХ
      moveMtrOX(now_action);               
    } else if (now_action < 7) {  // Движение мотора, отвечающего за ось ОУ
      moveMtrOY(now_action);
    } else if (now_action == 7) {
      drop();
    }
  }
}
