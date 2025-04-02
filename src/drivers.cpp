#include <Arduino.h>
#include <Servo.h>
#include "settings.h"
#include "drivers.h"

Servo srv; // Инициализация сервопривода

void moveMtrOX(int vector) {  // Передвижение мотора по оси ОХ
  String u = Serial.readStringUntil('\n');
  int ku = u.toInt();
  if (vector == 1) {            // При коде 1 от Raspberry Pi двигаемся в одном направлении
    digitalWrite(MTROXB, HIGH); // Кратковременное включение моторов на максимальную мощность для начала движения
    analogWrite(MTROXP, LOW);
    delay(DEL);
    digitalWrite(MTROXB, HIGH);
    analogWrite(MTROXP, constrain(155 - ku, 0, 110));
  } else if (vector == 2) {  // При коде 2 от Raspberry Pi останавливаемся
    digitalWrite(MTROXB, HIGH);
    analogWrite(MTROXP, HIGH);
  } else if (vector == 3) {  // При коде 3 от Raspberry Pi двигаемся в обратном направлении
    digitalWrite(MTROXB, LOW);
    analogWrite(MTROXP, HIGH);
    delay(DEL);
    digitalWrite(MTROXB, LOW);
    analogWrite(MTROXP, constrain(ku + 100, 170, 255));
  }
}

void moveMtrOY(int vector) {  // Передвижение мотора по оси ОУ
  String u = Serial.readStringUntil('\n');
  int ku = u.toInt();
  if (vector == 4) {            // При коде 4 от Raspberry Pi двигаемся в одном направлении
    digitalWrite(MTROYB, HIGH);
    analogWrite(MTROYP, 0);
    delay(DEL);
    digitalWrite(MTROYB, HIGH);
    analogWrite(MTROYP, constrain(200 - ku, 0, 170));
  } else if (vector == 5) {  // При коде 5 от Raspberry Pi останавливаемся
    digitalWrite(MTROYB, HIGH);
    analogWrite(MTROYP, HIGH);
  } else if (vector == 6) {  // При коде 6 от Raspberry Pi двигаемся в обратном направлении
    digitalWrite(MTROYB, LOW);
    analogWrite(MTROYP, HIGH);
    delay(DEL);
    digitalWrite(MTROYB, LOW);
    analogWrite(MTROYP, constrain(ku + 55, 85, 255));
  }
}

void drop() {  // Функция забора и выброса семечка
  digitalWrite(MTROYB, LOW);
  analogWrite(MTROYP, 0);
  digitalWrite(MTROXB, LOW);
  analogWrite(MTROXP, 0);
  digitalWrite(AIN2, HIGH);  // Включаем насос
  digitalWrite(AIN1, LOW);
  analogWrite(PWMA, 255);
  for (int i = 2; i < 112; ++i) {  // Плавно опускаем сервопривод
    srv.write(i);
    delay(10);
  }
  delay(2000);
  for (int i = 111; i > 1; --i) {  // Плавно поднимаем сервопривод
    srv.write(i);
    delay(10);
  }
  delay(2000);
  digitalWrite(AIN2, LOW);  // Выключаем насос - семечко падает в отверстие
  digitalWrite(AIN1, LOW);
  analogWrite(PWMA, 255);
}

void initServo() {  // Инициализация сервопривода
  srv.attach(SRV);
  srv.write(2);
}
