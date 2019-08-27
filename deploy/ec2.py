from deploy.support import Resource, Client


class EC2:

    def __init__(self, state_file_content):
        self.state_file_content = state_file_content
        self.ec2_resource = Resource.ec2()
        self.ec2_client = Client.ec2()

    def create_instance(self):
        user_data = open('sample-app/user_data.sh', 'r').read()
        response = self.ec2_resource.create_instances(
            ImageId='ami-035b3c7efe6d061d5',
            InstanceType='t2.micro',
            KeyName='daleponto',
            Monitoring={
                'Enabled': True
            },
            UserData=user_data,
            MaxCount=1,
            MinCount=1
        )
        self.__update_state_file_content(response)

    def is_instance_ready(self):
        core_ec2_client = self.ec2_resource.meta.client
        new_instance_id = self.state_file_content['Green']['EC2']['InstanceId']

        instance_statuses = self.__fetch_instance_statuses(core_ec2_client, new_instance_id)
        while instance_statuses['InstanceStatuses'] == []:
            instance_statuses = self.__fetch_instance_statuses(core_ec2_client, new_instance_id)

        instance_stauses_data = self.__parse_instances_statuses(instance_statuses)
        while self.__instance_is_initializing(instance_stauses_data):
            instance_statuses = self.__fetch_instance_statuses(core_ec2_client, new_instance_id)
            instance_stauses_data = self.__parse_instances_statuses(instance_statuses)
            print("----> Instance's system_status and instance_status are still 'initializing'\n")

        print("----> Instance's system_status and instance_status are now 'okay'\n")
        return True

    def terminate_instance(self, instance_mode):
        instance_id = self.state_file_content[instance_mode]['EC2']['InstanceId']
        self.ec2_resource.instances.filter(InstanceIds=[instance_id]).terminate()
        print(f"----> {instance_mode} instance terminated\n")

    def updated_state_file_content(self):
        return self.state_file_content

    def __update_state_file_content(self, created_instance_response):
        # TODO: Only for created instance
        green_content = self.state_file_content.get('Green')
        blue_content = self.state_file_content.get('Blue')

        self.state_file_content['Green'] = blue_content
        self.state_file_content['Blue'] = green_content

        green_content = self.state_file_content['Green']
        if green_content.get('EC2') is None:
            green_content['EC2'] = {}

        green_content['EC2']['InstanceId'] = created_instance_response[0].id

        if green_content['EC2'].get('VPC') is None:
            green_content['EC2']['VPC'] = {}

        green_content['EC2']['VPC']['PrivateIpAddress'] = created_instance_response[0].private_ip_address
        green_content['EC2']['VPC']['AssociatedElasticIp'] = {}
        self.state_file_content['Blue']['EC2']['VPC']['AssociatedElasticIp'] = {}

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
