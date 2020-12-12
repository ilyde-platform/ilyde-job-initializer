# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from protobuffers import dataset_pb2 as dataset__pb2
from google.protobuf import struct_pb2 as google_dot_protobuf_dot_struct__pb2


class DatasetServicesStub(object):
  """The datasets service definition.
  """

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.RetrieveDataset = channel.unary_unary(
        '/datasets.DatasetServices/RetrieveDataset',
        request_serializer=dataset__pb2.ID.SerializeToString,
        response_deserializer=dataset__pb2.Dataset.FromString,
        )
    self.CreateDataset = channel.unary_unary(
        '/datasets.DatasetServices/CreateDataset',
        request_serializer=dataset__pb2.Dataset.SerializeToString,
        response_deserializer=dataset__pb2.Dataset.FromString,
        )
    self.UpdateDataset = channel.unary_unary(
        '/datasets.DatasetServices/UpdateDataset',
        request_serializer=dataset__pb2.Dataset.SerializeToString,
        response_deserializer=dataset__pb2.Dataset.FromString,
        )
    self.DeleteDataset = channel.unary_unary(
        '/datasets.DatasetServices/DeleteDataset',
        request_serializer=dataset__pb2.ID.SerializeToString,
        response_deserializer=dataset__pb2.OperationStatus.FromString,
        )
    self.SearchDatasets = channel.unary_unary(
        '/datasets.DatasetServices/SearchDatasets',
        request_serializer=dataset__pb2.SearchDatasetRequest.SerializeToString,
        response_deserializer=dataset__pb2.SearchDatasetResponse.FromString,
        )
    self.RetrieveDatasetVersion = channel.unary_unary(
        '/datasets.DatasetServices/RetrieveDatasetVersion',
        request_serializer=dataset__pb2.ID.SerializeToString,
        response_deserializer=dataset__pb2.Version.FromString,
        )
    self.CreateDatasetVersion = channel.unary_unary(
        '/datasets.DatasetServices/CreateDatasetVersion',
        request_serializer=google_dot_protobuf_dot_struct__pb2.Struct.SerializeToString,
        response_deserializer=dataset__pb2.Version.FromString,
        )
    self.SearchDatasetVersions = channel.unary_unary(
        '/datasets.DatasetServices/SearchDatasetVersions',
        request_serializer=dataset__pb2.SearchVersionRequest.SerializeToString,
        response_deserializer=dataset__pb2.SearchVersionResponse.FromString,
        )
    self.CreateBucket = channel.unary_unary(
        '/datasets.DatasetServices/CreateBucket',
        request_serializer=dataset__pb2.Bucket.SerializeToString,
        response_deserializer=dataset__pb2.Bucket.FromString,
        )


class DatasetServicesServicer(object):
  """The datasets service definition.
  """

  def RetrieveDataset(self, request, context):
    """Retrieve a dataset With ObjectID
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def CreateDataset(self, request, context):
    """Create a dataset using information
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def UpdateDataset(self, request, context):
    """Update a dataset using information
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def DeleteDataset(self, request, context):
    """Delete a dataset with ObjectID
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def SearchDatasets(self, request, context):
    """Search for datasets
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def RetrieveDatasetVersion(self, request, context):
    """Retrieve a dataset's version passing the version'ID
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def CreateDatasetVersion(self, request, context):
    """Create a dataset version passing a Dataset's ID for which to create a version
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def SearchDatasetVersions(self, request, context):
    """Search for dataset's versions
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def CreateBucket(self, request, context):
    """Create bucket
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_DatasetServicesServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'RetrieveDataset': grpc.unary_unary_rpc_method_handler(
          servicer.RetrieveDataset,
          request_deserializer=dataset__pb2.ID.FromString,
          response_serializer=dataset__pb2.Dataset.SerializeToString,
      ),
      'CreateDataset': grpc.unary_unary_rpc_method_handler(
          servicer.CreateDataset,
          request_deserializer=dataset__pb2.Dataset.FromString,
          response_serializer=dataset__pb2.Dataset.SerializeToString,
      ),
      'UpdateDataset': grpc.unary_unary_rpc_method_handler(
          servicer.UpdateDataset,
          request_deserializer=dataset__pb2.Dataset.FromString,
          response_serializer=dataset__pb2.Dataset.SerializeToString,
      ),
      'DeleteDataset': grpc.unary_unary_rpc_method_handler(
          servicer.DeleteDataset,
          request_deserializer=dataset__pb2.ID.FromString,
          response_serializer=dataset__pb2.OperationStatus.SerializeToString,
      ),
      'SearchDatasets': grpc.unary_unary_rpc_method_handler(
          servicer.SearchDatasets,
          request_deserializer=dataset__pb2.SearchDatasetRequest.FromString,
          response_serializer=dataset__pb2.SearchDatasetResponse.SerializeToString,
      ),
      'RetrieveDatasetVersion': grpc.unary_unary_rpc_method_handler(
          servicer.RetrieveDatasetVersion,
          request_deserializer=dataset__pb2.ID.FromString,
          response_serializer=dataset__pb2.Version.SerializeToString,
      ),
      'CreateDatasetVersion': grpc.unary_unary_rpc_method_handler(
          servicer.CreateDatasetVersion,
          request_deserializer=google_dot_protobuf_dot_struct__pb2.Struct.FromString,
          response_serializer=dataset__pb2.Version.SerializeToString,
      ),
      'SearchDatasetVersions': grpc.unary_unary_rpc_method_handler(
          servicer.SearchDatasetVersions,
          request_deserializer=dataset__pb2.SearchVersionRequest.FromString,
          response_serializer=dataset__pb2.SearchVersionResponse.SerializeToString,
      ),
      'CreateBucket': grpc.unary_unary_rpc_method_handler(
          servicer.CreateBucket,
          request_deserializer=dataset__pb2.Bucket.FromString,
          response_serializer=dataset__pb2.Bucket.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'datasets.DatasetServices', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))