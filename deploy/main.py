import os
import json
import subprocess

from deploy.ec2 import EC2
from deploy.ecr import ECR
from deploy.vpc import VPC
from deploy.load_balancer import LoadBalancer
from deploy.auto_scaling import AutoScaling
from deploy.support import Resource, Client
from settings import SETTINGS


class StateFile:
    AWS_BUCKET_NAME = SETTINGS['state_file']['bucket_name']
    FILE_NAME = 'state_file.json'
    TMP_FILE_PATH = f"/tmp/{FILE_NAME}"

    def __init__(self):
        self.s3_resource = Resource.s3()
        self.bucket = self.s3_resource.Bucket(self.AWS_BUCKET_NAME)

    def download_to_tmp(self):
        self.bucket.download_file(self.FILE_NAME, self.TMP_FILE_PATH)

    def upload_from_tmp(self):
        self.bucket.upload_file(self.TMP_FILE_PATH, self.FILE_NAME)


class Deploy:
    def __init__(self):
        self.ec2_resource = Resource.ec2()
        self.ec2_client = Client.ec2()
        self.state_file = StateFile()

    def execute(self):
        self.state_file.download_to_tmp()
        print('State file successfully downloaded\n')
        self.__set_file_content()

        ecr = ECR(self.file_content)
        ecr.push_image()
        self.file_content = ecr.updated_state_file_content()
        print('Docker container image successfully uploaded to ECR\n')

        self.create_launch_configuration()
        self.create_load_balancer()
        self.create_auto_caling_group()
        print('Auto scaling group successfully created. Now waiting for it to be ready\n')

        #if ec2.is_instance_ready():
        #    vpc = VPC(self.file_content)
        #    vpc.associate_elastic_ip('Green')
        #    self.file_content = vpc.updated_state_file_content()
        #    print('Elastic IP successfully associated to green instance.')

        #rollback = input('Rollback? (y/n) ')
        #if rollback == 'n':
        #    ec2.terminate_instance('Blue')
        #    del self.file_content['Blue']
        #    print('Deploy finished successfully\n')
        #else:
        #    self.rollback()

        self.__save_file_content()
        self.state_file.upload_from_tmp()
        print('State file successfully uploaded\n')

    def create_load_balancer(self):
        if not self.file_content.get('LoadBalancer'):
            load_balancer = LoadBalancer(self.file_content)
            load_balancer.create()
            self.file_content = load_balancer.updated_state_file_content()

    def create_launch_configuration(self):
        if not self.file_content.get('LaunchConfiguration'):
            launch_config = AutoScaling(self.file_content)
            launch_config.create_launch_configuration()
            self.file_content = launch_config.updated_state_file_content()

    def create_auto_caling_group(self):
        launch_config = AutoScaling(self.file_content)
        launch_config.create_auto_scaling_group()
        self.file_content = launch_config.updated_state_file_content()

    def rollback(self):
        print('Rollback in process...\n')
        print('Reattaching Elastic IP to Blue instance\n')
        self.file_content['Blue']['EC2']['VPC']['AssociatedElasticIp']['AssociationId'] = None
        vpc.associate_elastic_ip('Blue')
        self.file_content = vpc.updated_state_file_content()

        print('Terminating Green instance\n')
        ec2.terminate_instance('Green')
        self.file_content = ec2.updated_state_file_content()

        del self.file_content['Green']
        self.file_content['Green'] = self.file_content['Blue']
        del self.file_content['Blue']
        print('Rollback finished\n')

    def __set_file_content(self):
        with open(StateFile.TMP_FILE_PATH, 'r') as state_file:
            self.file_content = json.loads(state_file.read())

    def __save_file_content(self):
        with open(StateFile.TMP_FILE_PATH, 'w') as state_file:
            json.dump(self.file_content, state_file)
