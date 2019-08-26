import subprocess

from settings import SETTINGS
from deploy.support import Client


class ECR:
    ACCOUNT_ID = SETTINGS['account_id']
    REGION = SETTINGS['region']
    ECR_NAME = SETTINGS['ecr']['repo_name']
    ECR_IMAGE_NAME = SETTINGS['ecr']['image_name']
    ECR_URL = f"{ACCOUNT_ID}.dkr.ecr.{REGION}.amazonaws.com/{ECR_NAME}"

    def __init__(self, state_file_content):
        self.state_file_content = state_file_content

    def push_image(self):
        docker_build_command = f"docker build . -t {self.ECR_IMAGE_NAME}"
        docker_tag_command = f"docker tag {self.ECR_IMAGE_NAME} {self.ECR_URL}"
        ecr_login_command = f"aws ecr get-login --no-include-email --region {self.REGION} | /bin/bash"
        ecr_push_command = f"docker push {self.ECR_URL}"

        subprocess.Popen(docker_build_command, shell=True, stdout=subprocess.PIPE).stdout.read()
        subprocess.Popen(docker_tag_command, shell=True, stdout=subprocess.PIPE).stdout.read()
        subprocess.Popen(ecr_login_command, shell=True, stdout=subprocess.PIPE).stdout.read()
        subprocess.Popen(ecr_push_command, shell=True, stdout=subprocess.PIPE).stdout.read()

    def updated_state_file_content(self):
        return self.state_file_content

