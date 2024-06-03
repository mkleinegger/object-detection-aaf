import base64
import json
import os
import time
import cv2 as cv
import numpy as np
from flask import Flask, request

app = Flask(__name__)
net = None

class_names = []

YOLO_CONFIG = os.path.abspath("./yolo_configs/yolov3-tiny.cfg")
YOLO_WEIGHTS = os.path.abspath("./yolo_configs/yolov3-tiny.weights")
YOLO_CLASS_NAMES = os.path.abspath("./yolo_configs/coco.names")

# ---------------------------------------------------------------------
# -----------------------------functions-------------------------------
# ---------------------------------------------------------------------

def setup():
    global class_names, net
    # Load the COCO class labels
    with open(YOLO_CLASS_NAMES, 'r') as f:
        class_names = f.read().strip().split('\n')

    # Load the YOLOv3-tiny network
    net = cv.dnn.readNetFromDarknet(YOLO_CONFIG, YOLO_WEIGHTS)
    net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)

def object_detection(id, image_data):
    def convert_base64_to_image(image_data):
        nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
        image = cv.imdecode(nparr, cv.IMREAD_COLOR)
        return image

    image = convert_base64_to_image(image_data)
    (H, W) = image.shape[:2]

    layer_names = net.getLayerNames()
    unconnected_out_layers = net.getUnconnectedOutLayers()
    if len(unconnected_out_layers.shape) > 1:
        unconnected_out_layers = unconnected_out_layers.flatten()

    output_layer_names = [layer_names[i - 1] for i in unconnected_out_layers]

    blob = cv.dnn.blobFromImage(image, 1/255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    layer_outputs = net.forward(output_layer_names)

    boxes = []
    confidences = []
    class_ids = []

    for output in layer_outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > 0.5:
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype('int')

                # Use the center (x, y)-coordinates to derive the top-left corner of the bounding box
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))

                # Update the lists of bounding box coordinates, confidences, and class IDs
                boxes.append([x, y, int(width), int(height)])

                confidences.append(float(confidence))
                class_ids.append(class_id)

    # Apply non-maxima suppression to suppress weak, overlapping bounding boxes
    indices = cv.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    results = {}
    if len(indices) > 0:
        for i in indices.flatten():
            label = class_names[class_ids[i]]
            confidence = confidences[i]

            results[label] =  confidence

    # Print the results
    print("-"*50)
    for label, score in results.items():
        print(f"Object: {label}, Confidence: {score:.4f}")
    print("-"*50)


# ---------------------------------------------------------------------
# --------------------------------API----------------------------------
# ---------------------------------------------------------------------


@app.route("/object-detection", methods=["POST"])
def json_response():
    body = json.loads(request.get_json())
    id, image_data = body['id'], body['image_data']
    
    object_detection(id, image_data)

    return json.dumps(
        {
            "id": "2b7082f5-d31a-54b7-a46e-5e4889bf69bd",
            "objects": [
                {"label": "table", "accuracy": 0.790481352806091},
                {"label": "person", "accuracy": 0.7877481352806091},
            ],
        }
    )


@app.route("/")
def hello():
    return "Hello, World!"


if __name__ == "__main__":
    setup()
    app.run(debug=True, port=8000)
