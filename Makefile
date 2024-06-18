# Variables
API_IMAGE_NAME := dic3-app
CONTAINER_NAME_LAYER := dependency_lambda_docker
IMAGE_NAME_LAYER := dependency_lambda_builder_image

AWS_CREDENTIALS_FILE=$(HOME)/.aws/credentials

.PHONY: build run build-layer

# Build the Docker image
build:
	docker build -t $(API_IMAGE_NAME) .

# Run the Docker container
run:
	docker run --rm -p 5001:5001 -v$(AWS_CREDENTIALS_FILE):/root/.aws/credentials:ro $(API_IMAGE_NAME)

# Build the dependency layer for AWS Lambda
build-layer:
	docker build -t $(IMAGE_NAME_LAYER) -f Dockerfile.layers .
	docker run -td --name=$(CONTAINER_NAME_LAYER) $(IMAGE_NAME_LAYER)
	docker cp ./layers-remote/requirements-layers.txt $(CONTAINER_NAME_LAYER):/
	
# install the dependencies and zip it up for AWS Lambda
	docker exec -i $(CONTAINER_NAME_LAYER) /bin/bash -c "virtualenv --python=/usr/bin/python3.9 python"
	docker exec -i $(CONTAINER_NAME_LAYER) /bin/bash -c	"source python/bin/activate"
	docker exec -i $(CONTAINER_NAME_LAYER) /bin/bash -c	"pip install -r requirements-layers.txt -t python/lib/python3.9/site-packages"
	docker exec -i $(CONTAINER_NAME_LAYER) /bin/bash -c	"zip -r9 python.zip python"

	docker cp $(CONTAINER_NAME_LAYER):/python.zip ./layers-remote/python.zip
	docker stop $(CONTAINER_NAME_LAYER)
	docker rm $(CONTAINER_NAME_LAYER)

