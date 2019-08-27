from deploy.support import Client


class AutoScaling:

    def __init__(self, state_file_content):
        self.auto_scaling_client = Client.auto_scaling()
        self.state_file_content = state_file_content

    def create_auto_scaling_group(self):
        if not self.state_file_content.get('AutoScaling'):
            response = self.auto_scaling_client.create_auto_scaling_group(
                AutoScalingGroupName='daniel-test-auto-scaling',
                LaunchConfigurationName=self.state_file_content['LaunchConfiguration']['Name'],
                MinSize=1,
                MaxSize=2,
                AvailabilityZones=['us-east-1a']
            )
            self.state_file_content['AutoScaling'] = {
                'GroupName': 'daniel-test-auto-scaling'
            }

    def create_launch_configuration(self):
        if not self.state_file_content.get('LaunchConfiguration'):
            user_data = open('sample-app/user_data.sh', 'r').read()
            response = self.auto_scaling_client.create_launch_configuration(
                LaunchConfigurationName='daniel-test-launch-configuration',
                ImageId='ami-035b3c7efe6d061d5',
                InstanceType='t2.micro',
                KeyName='daleponto',
            )
            self.state_file_content['LaunchConfiguration'] = {
                'Name': 'daniel-test-launch-configuration'
            }

    def updated_state_file_content(self):
        return self.state_file_content
