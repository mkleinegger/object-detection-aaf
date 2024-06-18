import boto3
import base64
from yolo_model import setup, object_detection

# AWS
YOLO_CONFIG_BUCKET_NAME = "config-storage-e12041500"
YOLO_CONFIG = "/tmp/yolov3-tiny.cfg"
YOLO_WEIGHTS = "/tmp/yolov3-tiny.weights"
YOLO_CLASS_NAMES = "/tmp/coco.names"

# AWS
s3 = boto3.resource('s3')
dynamodb = boto3.client('dynamodb')

# YOLO
CLASSIFICATION_THRESHOLD = 0.5

def fetch_config():
    yolo_config_bucket = s3.Bucket(YOLO_CONFIG_BUCKET_NAME)
    for s3_object in yolo_config_bucket.objects.all():
        filename = f"/tmp/{s3_object.key}"
        s3.Bucket(YOLO_CONFIG_BUCKET_NAME).download_file(s3_object.key, filename)

def lambda_handler(event, context):
    fetch_config()
    net = setup(YOLO_CONFIG, YOLO_WEIGHTS, YOLO_CLASS_NAMES)
    
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]
    
    image = boto3.client('s3').get_object(
        Bucket=bucket,
        Key=key,
    )

    results = object_detection(net, base64.b64encode(image['Body'].read()), CLASSIFICATION_THRESHOLD)
    
    table_entry = {'image-url':{'S': key}}
    
    values = [(key, value) for key, value in results.items()]
    #for key, value in results.items():
    #    table_entry[key] = {'S': str(value)}
    
    table_entry['accuracy'] = {'S': str(values)}
    dynamodb.put_item(
        TableName='object-detection-12041500', 
        Item=table_entry)
    
    return { 'statusCode': 200 }
