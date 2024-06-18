# Execution

## Server
AWS credentials should be located in `~/.aws/credentials`, to make the remote execution work.

    make build
    make run

## Client: local execution

    python src/client.py ./input_folder local http://localhost:5001/object-detection 

## Client: remote execution

    python src/client.py ./input_folder remote http://localhost:5001/object-detection-remote 