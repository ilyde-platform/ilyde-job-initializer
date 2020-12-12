# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from protobuffers import agent_pb2 as agent__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


class JobAgentServicesStub(object):
  """The job agent service definition.
  """

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.Sync = channel.unary_unary(
        '/jobs.JobAgentServices/Sync',
        request_serializer=agent__pb2.SyncRequest.SerializeToString,
        response_deserializer=agent__pb2.OperationStatus.FromString,
        )
    self.Commit = channel.unary_unary(
        '/jobs.JobAgentServices/Commit',
        request_serializer=agent__pb2.CommitRequest.SerializeToString,
        response_deserializer=agent__pb2.OperationStatus.FromString,
        )
    self.getChanges = channel.unary_unary(
        '/jobs.JobAgentServices/getChanges',
        request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
        response_deserializer=agent__pb2.OperationStatus.FromString,
        )


class JobAgentServicesServicer(object):
  """The job agent service definition.
  """

  def Sync(self, request, context):
    """Pull changes in Ilyde working dir
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def Commit(self, request, context):
    """Commit changes in Ilyde working dir
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def getChanges(self, request, context):
    """Fetch changes in Ilyde working dir
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_JobAgentServicesServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'Sync': grpc.unary_unary_rpc_method_handler(
          servicer.Sync,
          request_deserializer=agent__pb2.SyncRequest.FromString,
          response_serializer=agent__pb2.OperationStatus.SerializeToString,
      ),
      'Commit': grpc.unary_unary_rpc_method_handler(
          servicer.Commit,
          request_deserializer=agent__pb2.CommitRequest.FromString,
          response_serializer=agent__pb2.OperationStatus.SerializeToString,
      ),
      'getChanges': grpc.unary_unary_rpc_method_handler(
          servicer.getChanges,
          request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
          response_serializer=agent__pb2.OperationStatus.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'jobs.JobAgentServices', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
