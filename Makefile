# Variables
API_IMAGE_NAME := object-detection

AWS_IMAGE := object-detection-lambda
AWS_CREDENTIALS_FILE=$(HOME)/.aws/credentials
AWS_ACCOUNT_ID := $(shell test -f /tmp/aws-account-id.txt || aws sts get-caller-identity --query Account --output text > /tmp/aws-account-id.txt && cat /tmp/aws-account-id.txt)
AWS_REGION := us-east-1
AWS_REGISTRY := $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
AWS_IMAGE_BUCKET := image-bucket-group41
AWS_DETECTION_TABLE := object-detection-group41

.PHONY: build run lambda-setup lambda-teardown docker-aws-login create-aws-repository build-lambda push-lambda create-image-bucket create-detection-table create-lambda delete-repository delete-lambda delete-image-bucket delete-detection-table delete-lambda

# Build the Docker image
build:
	docker build -t $(API_IMAGE_NAME) .

# Run the Docker container
run:
	docker run --rm -p 5001:5001 -v$(AWS_CREDENTIALS_FILE):/root/.aws/credentials:ro $(API_IMAGE_NAME)

# Set up AWS infrastructure to run the lambda function
lambda-setup: docker-aws-login create-aws-repository build-lambda push-lambda create-image-bucket create-detection-table create-lambda

# Tear down AWS infrastructure
lambda-teardown: delete-lambda delete-image-bucket delete-detection-table delete-repository

# Log in to AWS ECR
docker-aws-login:
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(AWS_REGISTRY)

# Create AWS ECR repository
create-aws-repository:
	aws ecr create-repository --region $(AWS_REGION) --repository-name $(AWS_IMAGE) --no-cli-pager

# Build the Lambda Docker image
build-lambda:
	docker build -f Dockerfile.lambda -t $(AWS_IMAGE) .

# Push the Lambda Docker image to AWS ECR
push-lambda:
	docker tag $(AWS_IMAGE):latest $(AWS_REGISTRY)/$(AWS_IMAGE):latest
	docker push $(AWS_REGISTRY)/$(AWS_IMAGE):latest

# Create the S3 bucket for images
create-image-bucket:
	aws s3api create-bucket --region $(AWS_REGION) --bucket $(AWS_IMAGE_BUCKET) --no-cli-pager

# Create the DynamoDB table for detections
create-detection-table:
	aws dynamodb create-table --region $(AWS_REGION) --table-name $(AWS_DETECTION_TABLE) --attribute-definitions AttributeName=image-url,AttributeType=S --key-schema AttributeName=image-url,KeyType=HASH --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 --table-class STANDARD --no-cli-pager

# Create the Lambda function with the S3 trigger
create-lambda:
	aws lambda create-function --function-name object-detection --package-type Image --region $(AWS_REGION) --code ImageUri=$(AWS_REGISTRY)/$(AWS_IMAGE):latest --role arn:aws:iam::$(AWS_ACCOUNT_ID):role/LabRole --memory-size 512 --timeout 15 --no-cli-pager
	aws lambda wait function-active --function-name object-detection --region $(AWS_REGION)
	aws lambda add-permission --function-name object-detection --region $(AWS_REGION) --principal s3.amazonaws.com --statement-id s3invoke --action "lambda:InvokeFunction" --source-arn arn:aws:s3:::image-bucket-group41 --source-account $(AWS_ACCOUNT_ID) --no-cli-pager
	aws s3api put-bucket-notification-configuration --bucket $(AWS_IMAGE_BUCKET) --notification-configuration '{"LambdaFunctionConfigurations":[{"LambdaFunctionArn":"arn:aws:lambda:us-east-1:$(AWS_ACCOUNT_ID):function:object-detection","Events":["s3:ObjectCreated:*"]}]}' --no-cli-pager

# Delete the AWS ECR repository
delete-repository:
	-aws ecr delete-repository --region $(AWS_REGION) --repository-name $(AWS_IMAGE) --force --no-cli-pager

# Delete the S3 bucket for images
delete-image-bucket:
	-aws s3 rm s3://$(AWS_IMAGE_BUCKET) --recursive
	-aws s3api delete-bucket --region $(AWS_REGION) --bucket $(AWS_IMAGE_BUCKET)

# Delete the DynamoDB table for detections
delete-detection-table:
	-aws dynamodb delete-table --region $(AWS_REGION) --table-name $(AWS_DETECTION_TABLE) --no-cli-pager

# Delete the Lambda function
delete-lambda:
	-aws lambda delete-function --function-name object-detection --region $(AWS_REGION)