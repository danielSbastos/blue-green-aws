import time

from deploy.support import Client


class AutoScaling:

    def __init__(self, state_file_content):
        self.auto_scaling_client = Client.auto_scaling()
        self.state_file_content = state_file_content

    def enter_standby(self, instances_ids, green_blue):
        if not self.state_file_content[green_blue].get('AutoScaling'):
            return

        response = self.auto_scaling_client.enter_standby(
            AutoScalingGroupName=self.state_file_content[green_blue]['AutoScaling']['GroupName'],
            InstanceIds=instances_ids,
            ShouldDecrementDesiredCapacity=True
        )
        self.state_file_content[green_blue]['AutoScaling']['InstancesInStandBy'] = instances_ids

    def exit_standby(self, instances_ids, green_blue):
       if not self.state_file_content[green_blue].get('AutoScaling'):
            return

       response = self.auto_scaling_client.exit_standby(
           AutoScalingGroupName=self.state_file_content[green_blue]['AutoScaling']['GroupName'],
           InstanceIds=instances_ids,
           ShouldDecrementDesiredCapacity=False
       )
       self.state_file_content[green_blue]['AutoScaling']['InstancesInStandBy'] = []

    def delete_auto_scaling_group(self, green_blue):
        self.auto_scaling_client.delete_auto_scaling_group(
            AutoScalingGroupName=self.state_file_content[green_blue]['AutoScaling']['GroupName'],
            ForceDelete=True
        )

    def instances_ids(self, green_blue):
        response = self.auto_scaling_client.describe_auto_scaling_groups(
            AutoScalingGroupNames=[self.state_file_content[green_blue]['AutoScaling']['GroupName']]
        )

        return list(map(lambda i: i['InstanceId'], response['AutoScalingGroups'][0]['Instances']))

    def create_auto_scaling_group(self):
        name = 'daniel-test-auto-scaling' + time.strftime('%d-%m-%y--%H-%M-%S')
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
        self.state_file_content['Blue'] = self.state_file_content.get('Green', {})
        self.state_file_content['Green'] = {}
        self.state_file_content['Green']['AutoScaling'] = {'GroupName': name}

    def decrease_min_size(self, green_blue):
        self.auto_scaling_client.update_auto_scaling_group(
            AutoScalingGroupName=self.state_file_content[green_blue]['AutoScaling']['GroupName'],
            MinSize=0
        )

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
