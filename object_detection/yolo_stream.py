import cv2
import numpy as np
from django.http import StreamingHttpResponse

# Шляхи к YOLO
WEIGHTS_PATH = r"C:\Users\Dovgal Dima\Desktop\esp32cam_video_stream_on_web_server\CameraWebServer\yolov3.weights"
CFG_PATH = r"C:\Users\Dovgal Dima\Desktop\esp32cam_video_stream_on_web_server\CameraWebServer\yolov3.cfg"
NAMES_PATH = r"C:\Users\Dovgal Dima\Desktop\esp32cam_video_stream_on_web_server\CameraWebServer\coco.names"

# Завантаження YOLO моделі
net = cv2.dnn.readNet(WEIGHTS_PATH, CFG_PATH)
with open(NAMES_PATH, "r") as f:
    classes = [line.strip() for line in f.readlines()]
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

# Відеопотік ESP32
VIDEO_URL = "http://192.168.88.233:81/stream"

# Генератор кадрів для відеопотоку
def yolo_stream():
    cap = cv2.VideoCapture(VIDEO_URL)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Передобробка кадру
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        net.setInput(blob)
        outs = net.forward(output_layers)

        # Обробка виходів
        class_ids, confidences, boxes = [], [], []
        height, width, _ = frame.shape

        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    center_x, center_y, w, h = (int(detection[0] * width), int(detection[1] * height),
                                                int(detection[2] * width), int(detection[3] * height))
                    x, y = int(center_x - w / 2), int(center_y - h / 2)
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

        for i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            confidence = confidences[i]
            color = (0, 255, 0)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, f"{label} {int(confidence * 100)}%", (x, y - 10), cv2.FONT_HERSHEY_PLAIN, 1, color, 2)

        # Кодуємо кадр у формат JPEG для надсилання в потік
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()
