import cv2 as cv
import numpy as np
import base64

class_names = []

def setup(yolo_config, yolo_weights, yolo_class_names):
    global class_names

    # Load the COCO class labels
    with open(yolo_class_names, "r") as f:
        class_names = f.read().strip().split("\n")

    # Load the YOLOv3-tiny network
    net = cv.dnn.readNetFromDarknet(yolo_config, yolo_weights)
    net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)
    return net


def object_detection(net, image_data, classification_threshold):
    def convert_base64_to_image(image_data):
        nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
        image = cv.imdecode(nparr, cv.IMREAD_COLOR)
        return image

    def get_output_layer_names():
        layer_names = net.getLayerNames()
        unconnected_out_layers = net.getUnconnectedOutLayers()
        if len(unconnected_out_layers.shape) > 1:
            unconnected_out_layers = unconnected_out_layers.flatten()
        return [layer_names[i - 1] for i in unconnected_out_layers]

    image = convert_base64_to_image(image_data)
    (H, W) = image.shape[:2]

    output_layer_names = get_output_layer_names()

    blob = cv.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)

    net.setInput(blob)

    layer_outputs = net.forward(output_layer_names)

    # We still need to calculate boxes, to simply remove overlapps afterwards
    boxes, confidences, class_ids = [], [], []
    for output in layer_outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > classification_threshold:
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")

                x, y = int(centerX - (width / 2)), int(centerY - (height / 2))

                boxes.append([x, y, int(width), int(height)])

                confidences.append(float(confidence))
                class_ids.append(class_id)

    indices = cv.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    results = {}
    if len(indices) > 0:
        for i in indices.flatten():
            label, confidence = class_names[class_ids[i]], confidences[i]
            results[label] = confidence

    return results