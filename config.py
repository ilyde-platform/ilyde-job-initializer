# coding: utf-8

from decouple import config
import os

BASE_DIR = os.path.dirname(__file__)
DEBUG = config('DEBUG', default=False, cast=bool)

MINIO_ENDPOINT = config('MINIO_ENDPOINT')
MINIO_HOST = config('MINIO_HOST')

ILYDE_WORKING_DIR = config('ILYDE_WORKING_DIR')
ILYDE_JOB_ID = config('ILYDE_JOB_ID')
ILYDE_WORKING_DIR_CHANGELOG = '/home/ubuntu/.ilyde-working-dir.log'

DATASETS_SERVICES_ENDPOINT = config('DATASETS_SERVICES_ENDPOINT')
PROJECTS_SERVICES_ENDPOINT = config('PROJECTS_SERVICES_ENDPOINT')

ETCD_PORT = 2379
ETCD_HOST = config('ETCD_HOST')

AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
