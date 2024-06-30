import json
import time
import boto3
from yolo_model import load_image_as_base64, load_model, object_detection


s3_client = boto3.client("s3")
dynamodb_client = boto3.client("dynamodb")


def lambda_handler(event, context):
    # get bucket and key name
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]
    
    print("Load Image")
    # get object and read image
    response = s3_client.get_object(Bucket=bucket, Key=key)
    image_content = response["Body"].read()
    
    # convert image to base64
    img_data, file_uuid = load_image_as_base64(image_content)
    
    print("Load Model")
    net = load_model(s3_client)
    
    print("Do object detection")
    start = time.time()
    result = object_detection(file_uuid, img_data, net)
    end = time.time()
    
    print("Load into DynamoDB")
    objects = [{"label": label.strip(), "accuracy": value} for label, value in result.items() if value > 0.5]
    dynamodb_item = {
        "S3-URL": {"S": f"https://{bucket}.s3.amazonaws.com/{key}"},
        "Objects": {"S": json.dumps(objects)},
        "Inference-Time": {"N": str(end - start)}
    }
        
    print(dynamodb_item)
    table_name = 'e12239877-detected-objects'
    dynamodb_client.put_item(TableName=table_name, Item=dynamodb_item)

    
    print("Done")
    