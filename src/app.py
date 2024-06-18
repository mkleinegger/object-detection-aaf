import base64
import json
import os
import time

import boto3
from flask import Flask, request
from yolo_model import setup, object_detection

app = Flask(__name__)

# AWS
s3 = boto3.resource('s3')
BUCKET_NAME = "image-storage-e12041500"

# YOLO
net = None

CLASSIFICATION_THRESHOLD = 0.5

YOLO_CONFIG = os.path.abspath("./yolo_configs/yolov3-tiny.cfg")
YOLO_WEIGHTS = os.path.abspath("./yolo_configs/yolov3-tiny.weights")
YOLO_CLASS_NAMES = os.path.abspath("./yolo_configs/coco.names")

# ---------------------------------------------------------------------
# -----------------------------functions-------------------------------
# ---------------------------------------------------------------------

def upload_image_to_bucket(id, image_data):
    file_name = f"{id}.jpg"
    obj = s3.Object(BUCKET_NAME, file_name)
    obj.put(Body=base64.b64decode(image_data))
    
    return "https://%s.s3.amazonaws.com/%s" % (BUCKET_NAME, file_name)

# ---------------------------------------------------------------------
# --------------------------------API----------------------------------
# ---------------------------------------------------------------------


@app.route("/object-detection", methods=["POST"])
def object_detection_local():
    request_body = json.loads(request.get_json())

    start_time = time.time_ns() // 1_000_000
    result = object_detection(net, request_body["image_data"], CLASSIFICATION_THRESHOLD)
    end_time = time.time_ns() // 1_000_000

    return json.dumps(
        {
            "id": request_body["id"],
            "objects": [
                {"label": label, "accuracy": accuracy}
                for label, accuracy in result.items()
            ],
            "inference_time":  end_time - start_time
        }
    )

@app.route("/object-detection-remote", methods=["POST"])
def object_detection_remote():
    body = json.loads(request.get_json())
    
    start_time = time.time_ns() // 1_000_000
    s3_url = upload_image_to_bucket(body["id"], body["image_data"])
    end_time = time.time_ns() // 1_000_000

    return json.dumps(
        {
            "id": body["id"],
            "s3_url": s3_url,
            "inference_time": end_time - start_time,
        }
    )


# basic route to ensure API is live
@app.route("/")
def hello():
    return "Hello, World!"


if __name__ == "__main__":
    net = setup(YOLO_CONFIG, YOLO_WEIGHTS, YOLO_CLASS_NAMES)
    app.run(host="0.0.0.0", port=5001, debug=True)
