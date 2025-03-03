# Object Detection as a Function

A report can be found under https://mkleinegger.github.io/object-detection-aaf/report.pdf.

## Execution

### Server

AWS credentials should be located in `~/.aws/credentials`, to make the remote execution work.

```{bash}
make build
make start
```

### Client: local execution

```{bash}
make execute
```

### Client: remote execution

```{bash}
make execute-remote
```

### Setup AWS infrastructure for remote execution

```{bash}
make lambda-setup
```

### Teardown of AWS infrastructure

*Deletes all resources created by `make lambda-setup`*

```{bash}
make lambda-teardown
```