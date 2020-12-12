# coding: utf-8
import logging
import mimetypes
import os
import subprocess
import time

from protobuffers import dataset_pb2, dataset_pb2_grpc
from protobuffers import project_pb2, project_pb2_grpc
import grpc

import config
from minio import Minio
from google.protobuf import json_format, struct_pb2
import etcd3


def extract_label(label_name: str, data: dict):
    # extract label from data dict representation of ilyde metadata resource
    for label in data.get("labels"):
        if label_name == label['name']:
            return label['value']

    return None


def get_minio_client():
    # minio client
    client = Minio(config.MINIO_HOST, access_key=config.AWS_ACCESS_KEY_ID,
                   secret_key=config.AWS_SECRET_ACCESS_KEY, secure=False)
    return client


def run_command(command):
    process = subprocess.run(command, shell=True, check=True, universal_newlines=True)
    return process


def initialize_mc_client():
    command = "mc alias set minio {minio_endpoint} {minio_access_id} {minio_access_key}".format(
        minio_endpoint=config.MINIO_ENDPOINT, minio_access_id=config.AWS_ACCESS_KEY_ID,
        minio_access_key=config.AWS_SECRET_ACCESS_KEY
    )
    run_command(command)


def create_s3fs_credentials():
    path = "/home/ubuntu/.miniocredentials"
    command = "echo {minio_access_id}:{minio_access_key} > {path}  && sudo chmod 600 {path}".format(
        minio_access_id=config.AWS_ACCESS_KEY_ID,
        minio_access_key=config.AWS_SECRET_ACCESS_KEY,
        path=path
    )
    run_command(command)

    return path


def copy_project(project_id, revision_id):
    channel = grpc.insecure_channel(config.PROJECTS_SERVICES_ENDPOINT)
    stub = project_pb2_grpc.ProjectServicesStub(channel=channel)

    project = stub.Retrieve(project_pb2.ID(id=project_id))
    revision = stub.RetrieveRevision(project_pb2.ID(id=revision_id))

    repo_bucket = extract_label('repo_bucket', json_format.MessageToDict(project, preserving_proto_field_name=True,
                                                                         including_default_value_fields=True))
    # get minio client
    minio_client = get_minio_client()
    for file in revision.file_tree:
        destination = os.path.join(config.ILYDE_WORKING_DIR, file.name)
        obj = minio_client.fget_object(bucket_name=repo_bucket, object_name=file.name, file_path=destination, version_id=file.version)

        # add modification time
        os.utime(destination, (time.mktime(time.localtime()), time.mktime(obj.last_modified)))


def mount_dataset(dataset_name, related_bucket, credentials_file, writeable=False):

    dirname = os.path.join(config.ILYDE_WORKING_DIR, "datasets")
    if not os.path.exists(dirname):
        os.mkdir(dirname)

    cache = '/tmp/s3fs'
    if not os.path.exists(cache):
        os.mkdir(cache)

    if not writeable:
        mount_point = os.path.join(dirname, dataset_name)
        cache_dir = os.path.join(cache, dataset_name)
        os.mkdir(mount_point)
        os.mkdir(cache_dir)
        command = "s3fs {minio_bucket} {mount_point} -o passwd_file={credentials_file}" \
                  " -o url={minio_endpoint} -o use_path_request_style -o ro -o" \
                  " use_cache={cache_dir} -o umask=022".format(minio_endpoint=config.MINIO_ENDPOINT,
                                                               minio_bucket=related_bucket,
                                                               mount_point=mount_point,
                                                               cache_dir=cache_dir,
                                                               credentials_file=credentials_file
        )

    else:
        # just create a dir and then we will create a version from
        mount_point = os.path.join(dirname, 'output', dataset_name)
        os.makedirs(mount_point, exist_ok=True)
        command = "s3fs {minio_bucket} {mount_point} -o passwd_file={credentials_file}" \
                  " -o url={minio_endpoint} -o use_path_request_style -o rw -o umask=022"\
            .format(minio_endpoint=config.MINIO_ENDPOINT,
                    minio_bucket=related_bucket,
                    mount_point=mount_point,
                    credentials_file=credentials_file)

    run_command(command)


def commit_project(project_id, message, author, changes):
    channel = grpc.insecure_channel(config.PROJECTS_SERVICES_ENDPOINT)
    stub = project_pb2_grpc.ProjectServicesStub(channel=channel)

    project = stub.Retrieve(project_pb2.ID(id=project_id))
    repo_bucket = extract_label('repo_bucket', json_format.MessageToDict(project, preserving_proto_field_name=True,
                                                                         including_default_value_fields=True))
    etcd = etcd3.client(host=config.ETCD_HOST, port=config.ETCD_PORT)

    # acquire lock
    with etcd.lock(project_id, ttl=1800) as lock:
        # copy data to repo_bucket
        minio_client = get_minio_client()
        for change in changes:
            key = os.path.relpath(change["path"], config.ILYDE_WORKING_DIR).replace('\\', '/')
            if change['action'] == "deleted":
                minio_client.remove_object(bucket_name=repo_bucket, object_name=key)
            else:
                file_type, _ = mimetypes.guess_type(change["path"])
                if file_type is None:
                    file_type = 'application/octet-stream'
                minio_client.fput_object(repo_bucket, key, change["path"], content_type=file_type)

        # create new revision
        payload = struct_pb2.Struct()
        payload.update({'project': project_id, 'commit': message, 'author': author})
        stub.CreateRevision(payload)


def create_dataset_version(dataset_id, related_bucket):
    channel = grpc.insecure_channel(config.DATASETS_SERVICES_ENDPOINT)
    stub = dataset_pb2_grpc.DatasetServicesStub(channel=channel)

    # create new revision
    payload = struct_pb2.Struct()
    payload.update({'dataset': dataset_id, 'related_bucket': related_bucket})
    stub.CreateDatasetVersion(payload)


def create_dataset_bucket():
    channel = grpc.insecure_channel(config.DATASETS_SERVICES_ENDPOINT)
    stub = dataset_pb2_grpc.DatasetServicesStub(channel=channel)

    bucket = stub.CreateBucket(dataset_pb2.Bucket())
    return bucket.name
