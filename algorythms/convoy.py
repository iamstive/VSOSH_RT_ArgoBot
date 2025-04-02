import cv2  # Импортируем бибилотеки
import numpy as np
import serial
from picamera2 import Picamera2
from time import sleep, time


def write_to_Arduino(number):  # Функция для отправки сигнала на Arduino
    ser.write((str(number) + "\n").encode("utf-8"))
    print(number)
    sleep(0.01)


def stop_motors():  # Функция остановки всех моторов
    write_to_Arduino(2)
    write_to_Arduino(0)
    write_to_Arduino(5)
    write_to_Arduino(0)


def write_image(image):  # Отправка изображения на медиа-сервер
    global start
    out.write(image)
    now = time()
    diff = (1 / fps) - now - start
    if diff > 0:
        sleep(diff)
    start = now


try:  # Устанавливаем соединение с Arduino
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1.0)
except:
    ser = serial.Serial('/dev/ttyUSB1', 9600, timeout=1.0)

sleep(3)
ser.reset_input_buffer()

picam2 = Picamera2()  # Инициализация камеры
picam2.preview_configuration.main.size = (800, 600)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

fps = 20
width = 800
height = 600
cam_data = 'appsrc ! videoconvert' + \
           ' ! video/x-raw,format=I420' + \
           ' ! x264enc speed-preset=ultrafast bitrate=600 key-int-max=' + str(fps * 2) + \
           ' ! video/x-h264,profile=baseline' + \
           ' ! rtspclientsink location=rtsp://localhost:8554/mystream'
out = cv2.VideoWriter(cam_data, cv2.CAP_GSTREAMER, 0, fps, (width, height), True)

start = time()
if not out.isOpened():
    raise Exception("can't open video writer")

try:
    while True:
        frame = picam2.capture_array()  # Получаем кадр, обрабатываем его
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (9, 9), 13)
        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT, 2.5, 100, param1=35, param2=85, minRadius=80, maxRadius=115)
        if circles is not None:  #
            circles = np.round(circles[0, :]).astype("int")
            pos_x = circles[0][0]
            pos_y = circles[0][1]
            print(pos_x, pos_y)
            cv2.circle(frame, (int(pos_x), int(pos_y)), int(circles[0][2]), (0, 255, 0), 4)
            cv2.circle(frame, (int(pos_x), int(pos_y)), 3, (0, 0, 255), 3)
            ux = (400 - pos_x) * 0.7  # Рассчитываем скорости при помощи пропорционального ПИД-регулятора
            uy = (300 - pos_y) * 0.7

            if pos_y < 250:  #  В зависммости от положения куба, выбираем действие
                write_to_Arduino(1)
                write_to_Arduino(uy)
            elif pos_y > 350:
                write_to_Arduino(3)
                write_to_Arduino(-uy)
            else:
                write_to_Arduino(2)
                write_to_Arduino(uy)
            if pos_x < 350:
                write_to_Arduino(6)
                write_to_Arduino(ux)
            elif pos_x > 450:
                write_to_Arduino(4)
                write_to_Arduino(-ux)
            else:
                write_to_Arduino(5)
                write_to_Arduino(ux)
        else:
            stop_motors()
        write_image(frame)
except KeyboardInterrupt:  # Закрываем сериал-порт
    stop_motors()
    print('cls')
    ser.close()
