from django.shortcuts import render
from django.http import StreamingHttpResponse
from .yolo_stream import yolo_stream

# Генератор для передачі відеопотоку
def video_feed(request):
    return StreamingHttpResponse(yolo_stream(), content_type='multipart/x-mixed-replace; boundary=frame')

# Представлення для завантаження HTML сторінки з потоком
def esp32_stream(request):
    context = {'camera_url': '/object_detection/video_feed/'}
    return render(request, 'esp32_stream.html', context)

