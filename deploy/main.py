import os
import json
import subprocess
import time

from deploy import ECR, LoadBalancer, AutoScaling, StateFile


class Deploy:
    def __init__(self):
        self.state_file = StateFile()

    def execute(self):
        self.state_file.download_to_tmp()
        print('State file successfully downloaded\n')
        self.__set_file_content()

        self.build_and_push_docker_image()

        self.create_launch_configuration()
        self.create_load_balancer()
        self.create_auto_scaling_group()
        print('Auto scaling group successfully created. Now waiting for it to be ready\n')

        time.sleep(100)

        lb = LoadBalancer(self.file_content)
        if lb.instances_healthy():
            auto_scaling = AutoScaling(self.file_content)
            instances_ids = auto_scaling.instances_ids('Blue')
            auto_scaling.decrease_min_size('Blue')
            auto_scaling.enter_standby(instances_ids, 'Blue')
            self.file_content = auto_scaling.updated_state_file_content()
            print('Green auto scaling group is now ready. Blue one has entered standby mode\n')

        rollback = input('Rollback? (y/n) ')
        if rollback == 'n':
            auto_scaling = AutoScaling(self.file_content)
            auto_scaling.delete_auto_scaling_group('Blue')
            del self.file_content['Blue']
            print('Deploy finished successfully\n')
        else:
            self.rollback()

        self.__save_file_content()
        self.state_file.upload_from_tmp()
        print('State file successfully uploaded\n')

    def rollback(self):
        print('Rollback in process...\n')
        auto_scaling = AutoScaling(self.file_content)
        standby_instaces_ids = self.file_content['Blue']['AutoScaling']['InstancesInStandBy']
        auto_scaling.exit_standby(standby_instaces_ids, 'Blue')
        auto_scaling.delete_auto_scaling_group('Green')
        self.file_content = auto_scaling.updated_state_file_content()

        del self.file_content['Green']
        blue = self.file_content['Blue']
        self.file_content['Green'] = blue
        del self.file_content['Blue']

        print('Rollback finished\n')

    def build_and_push_docker_image(self):
        ecr = ECR(self.file_content)
        ecr.push_image()
        self.file_content = ecr.updated_state_file_content()
        print('Docker container image successfully uploaded to ECR\n')

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

    def create_auto_scaling_group(self):
        launch_config = AutoScaling(self.file_content)
        launch_config.create_auto_scaling_group()

    def __set_file_content(self):
        with open(StateFile.TMP_FILE_PATH, 'r') as state_file:
            self.file_content = json.loads(state_file.read())

    def __save_file_content(self):
        with open(StateFile.TMP_FILE_PATH, 'w') as state_file:
            json.dump(self.file_content, state_file)
