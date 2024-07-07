# Execution

## Server

AWS credentials should be located in `~/.aws/credentials`, to make the remote execution work.

```{bash}
make build
make run
```

## Client: local execution

```{bash}
python src/client.py ./input_folder local http://localhost:5001/object-detection
```

## Client: remote execution

```{bash}
python src/client.py ./input_folder remote http://localhost:5001/object-detection-remote
```

## Setup AWS infrastructure for remote execution

```{bash}
make lambda-setup
```

## Teardown of AWS infrastructure

*Deletes all resources created by `make lambda-setup`*

```{bash}
make lambda-teardown
```