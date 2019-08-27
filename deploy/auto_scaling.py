import time

from deploy.support import Client


class AutoScaling:

    def __init__(self, state_file_content):
        self.auto_scaling_client = Client.auto_scaling()
        self.state_file_content = state_file_content

    def delete_auto_scaling_group(self):
        self.auto_scaling_client.delete_auto_scaling_group(
            AutoScalingGroupName=self.state_file_content['AutoScaling']['GroupName'],
            ForceDelete=True
        )

    def create_auto_scaling_group(self):
        name = 'daniel-test-auto-scaling' + time.strftime('%d-%m-%y--%M-%H-%S')
        response = self.auto_scaling_client.create_auto_scaling_group(
            AutoScalingGroupName=name,
            LaunchConfigurationName=self.state_file_content['LaunchConfiguration']['Name'],
            MinSize=1,
            MaxSize=2,
            AvailabilityZones=['us-east-1a'],
            LoadBalancerNames=[
                self.state_file_content['LoadBalancer']['Name'],
            ],
        )
        self.state_file_content['AutoScaling'] = {'GroupName': name}

    def create_launch_configuration(self):
        user_data = open('sample-app/user_data.sh', 'r').read()
        response = self.auto_scaling_client.create_launch_configuration(
            LaunchConfigurationName='daniel-test-launch-configuration',
            ImageId='ami-035b3c7efe6d061d5',
            InstanceType='t2.micro',
            KeyName='daleponto',
            UserData=user_data
        )
        self.state_file_content['LaunchConfiguration'] = {
            'Name': 'daniel-test-launch-configuration'
        }

    def updated_state_file_content(self):
        return self.state_file_content
