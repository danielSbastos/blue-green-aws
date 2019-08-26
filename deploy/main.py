import os
import json
import subprocess

from deploy.ec2 import EC2
from deploy.ecr import ECR
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
    ACCOUNT_ID = SETTINGS['account_id']
    REGION = SETTINGS['region']

    def __init__(self):
        self.ec2_resource = Resource.ec2()
        self.ec2_client = Client.ec2()
        self.state_file = StateFile()

    def execute(self):
        self.state_file.download_to_tmp()
        print('State file successfully downloaded\n')

        self.__set_file_content()
        print('State file content successfully set to an in-memory hash\n')

        ecr = ECR(self.file_content)
        ecr.push_image()
        self.file_content = ecr.updated_state_file_content()
        print('Docker container image successfully uploaded to ERC\n')

        #ec2 = EC2(self.file_content)
        #self.ec2.create_instance()
        #self.file_content = self.ec2.updated_state_file_content()
        #print('Green instance successfully created. Now waiting for it to be ready\n')

        #if ec2.is_instance_ready():
            #print("DANIEL")
            #self.__alter_rds_sg_ingress()
            #self.__associate_elastic_ip()

        #rollback = input('Rollback? (y/n)')
        #if rollback == 'n':
        #    self.__terminate_old_instance()

        #self.__save_file_content()
        #self.state_file.upload_from_tmp()

    def __set_file_content(self):
        with open(StateFile.TMP_FILE_PATH, 'r') as state_file:
            self.file_content = json.loads(state_file.read())

    def __save_file_content(self):
        with open(StateFile.TMP_FILE_PATH, 'w') as state_file:
            json.dump(self.file_content, state_file)

    def __alter_rds_sg_ingress(self):
        self.ec2_client.authorize_security_group_ingress(
            IpProtocol='TCP',
            CidrIp=self.file_content['EC2']['Vpc']['PrivateIpAddress'] + '/32',
            FromPort=5432,
            ToPort=5432,
            GroupId=self.file_content['EC2']['Vpc']['SecurityGroups']['RDS']['GroupId']
        )

    def __allocate_elastic_ip(self):
        allocated_elastic_ip =  self.file_content['EC2']['Vpc']['AllocatedElasticIp']['AllocationId']
        if not allocated_elastic_ip:
            response = self.ec2_client.allocate_address(Domain='vpc')
            self.file_content['EC2']['Vpc']['AllocatedElasticIp'] = {}
            self.file_content['EC2']['Vpc']['AllocatedElasticIp']['PublicIp'] = response['PublicIp']
            self.file_content['EC2']['Vpc']['AllocatedElasticIp']['AllocationId'] = response['AllocationId']

            print('----> Allocated an elastic IP\n')
        else:
            print('----> An elastic IP already allocated\n')

    def __associate_elastic_ip(self):
        instance_id = self.file_content['EC2']['InstanceId']
        allocated_elastic_ip = self.file_content['EC2']['Vpc']['AllocatedElasticIp']['AllocationId']
        associated_elastic_ip = self.file_content['EC2']['Vpc']['AssociatedElasticIp'].get('AssociationId')

        if not associated_elastic_ip:
            if allocated_elastic_ip:
                response = self.ec2_client.associate_address(
                    AllocationId=allocated_elastic_ip,
                    InstanceId=instance_id,
                )
                self.file_content['EC2']['Vpc']['AssociatedElasticIp'] = {}
                self.file_content['EC2']['Vpc']['AssociatedElasticIp']['AssociationId'] = response['AssociationId']

                print('----> Attached an elastic ip\n')
            else:
                self.__allocate_elastic_ip()
                self.__associate_elastic_ip()

    def __terminate_old_instance(self):
        self.ec2_resource.instances.filter(InstanceIds=[self.old_instance_id]).terminate()
        print('----> Blue instance terminated\n')

    @staticmethod
    def __instance_is_initializing(instance_stauses_dict):
        return instance_stauses_dict['system_status'] == 'initializing' and \
                instance_stauses_dict['instance_status'] == 'initializing'

    @staticmethod
    def __fetch_instance_statuses(core_ec2_client, instance_id):
        return core_ec2_client.describe_instance_status(InstanceIds=[instance_id])

    @staticmethod
    def __parse_instances_statuses(instance_statuses):
        system_details = instance_statuses['InstanceStatuses'][0]['SystemStatus']['Details']
        instance_details = instance_statuses['InstanceStatuses'][0]['InstanceStatus']['Details']
        system_status = system_details[0]['Status']
        instance_status = instance_details[0]['Status']

        return { 'system_status': system_status, 'instance_status': instance_status }


if __name__ == "__main__":
    Deploy().execute()
