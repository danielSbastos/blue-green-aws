import boto3

from settings import SETTINGS


class Resource:
    @staticmethod
    def ec2():
        return boto3.resource('ec2', region_name=SETTINGS['region'])

    @staticmethod
    def s3():
        return boto3.resource('s3', region_name=SETTINGS['region'])


class Client:
    @staticmethod
    def ec2():
        return boto3.client('ec2', region_name=SETTINGS['region'])

    @staticmethod
    def auto_scaling():
        return boto3.client('autoscaling', region_name=SETTINGS['region'])

    @staticmethod
    def load_balancer():
        return boto3.client('elb', region_name=SETTINGS['region'])
