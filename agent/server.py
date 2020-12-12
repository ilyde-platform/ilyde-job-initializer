# encoding: utf-8
import json
import logging
from concurrent import futures
import grpc
from grpc_interceptor.exceptions import InvalidArgument
from agent.interceptors import ExceptionToStatusInterceptor
from protobuffers import agent_pb2, agent_pb2_grpc

import config
import utils
from job import Watcher


class JobAgentServicer(agent_pb2_grpc.JobAgentServicesServicer):

    def __init__(self, project_id, author, watcher: Watcher):
        super().__init__()
        self.project_id = project_id
        self.author = author
        self.watcher = watcher

    def Sync(self, request, context):

        if not request.revision:
            raise InvalidArgument("revision cannot be empty, please provide a valid revision.")

        utils.copy_project(self.project_id, request.revision)
        return agent_pb2.OperationStatus(status=200, message="Operation succeeded.")

    def Commit(self, request, context):
        # synchronize changes with Minio
        if not request.msg:
            raise InvalidArgument("msg cannot be empty, please provide a valid commit message.")

        changes = self.watcher.get_state()
        if changes is not None:
            utils.commit_project(self.project_id, request.msg, self.author, changes)

        return agent_pb2.OperationStatus(status=200, message="Operation succeeded.")

    def getChanges(self, request, context):

        changes = self.watcher.get_state()
        if changes is not None:
            return agent_pb2.ChangeResponse(total=len(changes), changes=changes)

        return agent_pb2.ChangeResponse(total=0, changes=[])


def serve(project, author, watcher):
    logging.basicConfig()
    interceptors = [ExceptionToStatusInterceptor()]

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), interceptors=interceptors)
    agent_pb2_grpc.add_JobAgentServicesServicer_to_server(
        JobAgentServicer(project, author, watcher), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()

