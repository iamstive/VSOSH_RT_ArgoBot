import cv2  # Импортируем библиотеки
import numpy as np
from picamera2 import Picamera2
from datetime import datetime
from time import sleep, time


def write_image(image):  # Функция отправки сообщения на медиа сервер
    global start
    out.write(image)
    now = time()
    diff = (1 / fps) - now - start
    if diff > 0:
        sleep(diff)
    start = now


picam2 = Picamera2()  # Инициализация камеры
picam2.preview_configuration.main.size = (1920,1080)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

fps = 15
width = 1920
height = 1080
colors = {'RED': (0, 255, 0)}

cam_data = 'appsrc ! videoconvert' + \
    ' ! video/x-raw,format=I420' + \
    ' ! x264enc speed-preset=ultrafast bitrate=600 key-int-max=' + str(fps * 2) + \
    ' ! video/x-h264,profile=baseline' + \
    ' ! rtspclientsink location=rtsp://localhost:8554/mystream'
out = cv2.VideoWriter(cam_data, cv2.CAP_GSTREAMER, 0, fps, (width, height), True)


start = time()
if not out.isOpened():  # Проверяем, открыт ли медиа-сервер
    raise Exception("can't open video writer")

t1 = time()
while True:
    frame = picam2.capture_array()  # Получааем изображение, обрабатываем его
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (17, 17), 17)
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT, 1.8	, 100, param1=16, param2=78, minRadius=100, maxRadius=140)
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            cv2.circle(frame, (int(x), int(y)), int(r), (0, 255, 0), 4)
            cv2.circle(frame, (int(x), int(y)), 3, (0, 0, 255), 3)
    write_image(frame)  # Отправляем изображение на медиа-сервер
    t2 = time()
    t1 = time()
