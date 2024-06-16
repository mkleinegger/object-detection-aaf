import json
import boto3
from yolo_model import load_image_as_base64, load_model, object_detection


s3_client = boto3.client("s3")


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
    result = object_detection(file_uuid, img_data, net)
    
    output = {
            "S3 URL": f"https://{bucket}.s3.amazonaws.com/{key}",
            "objects": [{"label": key, "accuracy": value} for key, value in result.items()]
        }
        
    print(output)
    
    ## TODO: Store to DynamoDB
    
    print("Done")
    