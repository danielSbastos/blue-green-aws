import boto3

from ..configuration import CONFIGURATION


class Resource:
    @staticmethod
    def ec2():
        return boto3.resource('ec2', region_name=CONFIGURATION['region'])

    @staticmethod
    def s3():
        return boto3.resource('s3', region_name=CONFIGURATION['region'])


class Client:
    @staticmethod
    def ec2():
        return boto3.client('ec2', region_name=CONFIGURATION['region'])

