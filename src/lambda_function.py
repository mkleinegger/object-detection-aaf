import boto3
import base64
from yolo_model import setup, object_detection
import os

# AWS
YOLO_CONFIG = os.path.abspath("./yolo_configs/yolov3-tiny.cfg")
YOLO_WEIGHTS = os.path.abspath("./yolo_configs/yolov3-tiny.weights")
YOLO_CLASS_NAMES = os.path.abspath("./yolo_configs/coco.names")

DYNAMODB_TABLE = 'object-detection-group41'

# AWS
s3 = boto3.resource('s3')
dynamodb = boto3.client('dynamodb', region_name='us-east-1')

# YOLO
CLASSIFICATION_THRESHOLD = 0.5


def handler(event, context):
    net = setup(YOLO_CONFIG, YOLO_WEIGHTS, YOLO_CLASS_NAMES)
    
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]
    
    # fetch image
    obj = s3.Object(bucket, key)
    image = obj.get()

    results = object_detection(net, base64.b64encode(image['Body'].read()), CLASSIFICATION_THRESHOLD)
    
    # create key/value-pair with key: array of results
    # table_entry = {'image-url':{'S': key}, 'accuracy': {'S': [(key, value) for key, value in results.items()]}}
    
    # create key/value-pair where each class has its own col
    table_entry = {'image-url':{'S': f"https://{bucket}.s3.amazonaws.com/{key}"}}
    for key, value in results.items():
        table_entry[key] = {'S': str(value)}
    
    dynamodb.put_item(TableName=DYNAMODB_TABLE, Item=table_entry)
    
    return { 'statusCode': 200 }
