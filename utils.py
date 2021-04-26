# coding: utf-8
#
# Copyright (c) 2020-2021 Hopenly srl.
#
# This file is part of Ilyde.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import logging
import mimetypes
import os
import subprocess
import time

from protos import dataset_pb2, dataset_pb2_grpc
from protos import project_pb2, project_pb2_grpc
import grpc

import config
from minio import Minio
from minio.error import MinioError
import etcd3


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

    # get minio client
    minio_client = get_minio_client()
    for file in revision.file_tree:
        destination = os.path.join(config.ILYDE_WORKING_DIR, file.name)
        try:
            obj = minio_client.fget_object(bucket_name=project.repo_bucket, object_name=file.name, file_path=destination, version_id=file.version)
            # add modification time
            os.utime(destination, (time.mktime(time.localtime()), time.mktime(obj.last_modified)))
        except MinioError as e:
            pass
        except Exception as e:
            pass


def mount_dataset(dataset_id, version, credentials_file, mount_output=False):
    # retrieve dataset version
    dataset_detail = retrieve_dataset(dataset_id)
    dataset_bucket = None
    dirname = os.path.join(config.ILYDE_WORKING_DIR, "datasets")
    if not os.path.exists(dirname):
        os.mkdir(dirname)

    cache = '/tmp/s3fs'
    if not os.path.exists(cache):
        os.mkdir(cache)

    version_detail = search_dataset_version(dataset_id, version)
    if version_detail is None:
        return dataset_bucket, None

    dataset_bucket = version_detail.related_bucket
    mount_point = os.path.join(dirname, dataset_detail.name)
    cache_dir = os.path.join(cache, dataset_detail.name)
    os.makedirs(mount_point, exist_ok=True)
    os.mkdir(cache_dir)
    command = "s3fs {minio_bucket} {mount_point} -o passwd_file={credentials_file}" \
              " -o url={minio_endpoint} -o use_path_request_style -o ro -o" \
              " use_cache={cache_dir} -o umask=022".format(minio_endpoint=config.MINIO_ENDPOINT,
                                                           minio_bucket=dataset_bucket,
                                                           mount_point=mount_point,
                                                           cache_dir=cache_dir,
                                                           credentials_file=credentials_file)

    if mount_output:
        # just create a dir and then we will create a version from
        dataset_bucket = create_dataset_bucket()
        mount_point = os.path.join(dirname, 'output', dataset_detail.name)
        os.makedirs(mount_point, exist_ok=True)
        command = "s3fs {minio_bucket} {mount_point} -o passwd_file={credentials_file}" \
                  " -o url={minio_endpoint} -o use_path_request_style -o rw -o umask=022"\
            .format(minio_endpoint=config.MINIO_ENDPOINT,
                    minio_bucket=dataset_bucket,
                    mount_point=mount_point,
                    credentials_file=credentials_file)

        run_command(command)

    run_command(command)

    return dataset_bucket, dataset_detail.name


def commit_project(project_id, message, author, changes):
    channel = grpc.insecure_channel(config.PROJECTS_SERVICES_ENDPOINT)
    stub = project_pb2_grpc.ProjectServicesStub(channel=channel)

    project = stub.Retrieve(project_pb2.ID(id=project_id))

    etcd = etcd3.client(host=config.ETCD_HOST, port=config.ETCD_PORT)

    # acquire lock
    with etcd.lock(project_id, ttl=1800) as lock:
        # copy data to repo_bucket
        minio_client = get_minio_client()
        for change in changes:
            key = os.path.relpath(change["path"], config.ILYDE_WORKING_DIR).replace('\\', '/')
            if change['action'] == "deleted":
                minio_client.remove_object(bucket_name=project.repo_bucket, object_name=key)
            else:
                file_type, _ = mimetypes.guess_type(change["path"])
                if file_type is None:
                    file_type = 'application/octet-stream'
                minio_client.fput_object(project.repo_bucket, key, change["path"], content_type=file_type)

        # create new revision
        payload = {'project': project_id, 'commit': message, 'author': author}
        response = stub.CreateRevision(project_pb2.Revision(**payload))
        return response


def create_dataset_version(dataset_id, related_bucket, author):
    channel = grpc.insecure_channel(config.DATASETS_SERVICES_ENDPOINT)
    stub = dataset_pb2_grpc.DatasetServicesStub(channel=channel)
    payload = {'dataset': dataset_id, 'related_bucket': related_bucket, "author": author}
    stub.CreateVersion(dataset_pb2.Version(**payload))


def create_dataset_bucket():
    channel = grpc.insecure_channel(config.DATASETS_SERVICES_ENDPOINT)
    stub = dataset_pb2_grpc.DatasetServicesStub(channel=channel)

    bucket = stub.CreateBucket(dataset_pb2.Bucket())
    return bucket.name


def retrieve_dataset_version(version_id):
    channel = grpc.insecure_channel(config.DATASETS_SERVICES_ENDPOINT)
    stub = dataset_pb2_grpc.DatasetServicesStub(channel=channel)
    return stub.RetrieveVersion(dataset_pb2.ID(id=version_id))


def search_dataset_version(dataset_id, version_name):
    channel = grpc.insecure_channel(config.DATASETS_SERVICES_ENDPOINT)
    stub = dataset_pb2_grpc.DatasetServicesStub(channel=channel)
    if version_name != "latest":
        query = {"name": version_name, "dataset": dataset_id}
    else:
        query = {"dataset": dataset_id}

    response = stub.SearchVersions(dataset_pb2.SearchVersionRequest(query=query))
    return response.data[0] if response.data else None


def retrieve_dataset(dataset_id):
    channel = grpc.insecure_channel(config.DATASETS_SERVICES_ENDPOINT)
    stub = dataset_pb2_grpc.DatasetServicesStub(channel=channel)
    return stub.RetrieveDataset(dataset_pb2.ID(id=dataset_id))


def last_project_revision(project_id):
    channel = grpc.insecure_channel(config.PROJECTS_SERVICES_ENDPOINT)
    stub = project_pb2_grpc.ProjectServicesStub(channel=channel)

    query = {"project": project_id}

    response = stub.SearchRevision(project_pb2.SearchRevisionRequest(query=query))
    return response.data[0]


def retrieve_project_revision(revision_id):
    channel = grpc.insecure_channel(config.PROJECTS_SERVICES_ENDPOINT)
    stub = project_pb2_grpc.ProjectServicesStub(channel=channel)

    return stub.RetrieveRevision(project_pb2.ID(id=revision_id))
