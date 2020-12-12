## gRPC Service for Job Agent

Questo progetto implementaun servizio gRPC per job agent:

1. A riga di commando, eseguire il commando:

    ```shell script
    python ./server.py 
    ```
2. Compilando il Docker file:

    ```shell script
    docker build -t jobagent-services:latest .
    docker run -d -p 50051:50051 -n jobagent-services jobagent-services:latest
    ```
   
3. Generare gRPC code

    ```shell script
     python -m grpc_tools.protoc -I./protobuffers --python_out=./protobuffers --grpc_python_out=./protobuffers ./protobuffers/service.proto
    ```
    