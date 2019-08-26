from deploy.support import Resource, Client


class EC2:

    def __init__(self, state_file_content):
        self.state_file_content = state_file_content
        self.ec2_resource = Resource.ec2()
        self.ec2_client = Client.ec2()

    def create_instance(self):
        user_data = open('deploy/data/user_data.sh', 'r').read()

        instance = self.ec2_resource.create_instances(
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

        self.old_instance_id = self.state_file_content['EC2']['InstanceId']
        self.old_instance_private_ip = self.state_file_content['EC2']['InstanceId']

        self.state_file_content['EC2']['Vpc']['PrivateIpAddress'] = instance[0].private_ip_address
        self.state_file_content['EC2']['InstanceId'] = instance[0].id
        self.state_file_content['EC2']['Vpc']['AssociatedElasticIp'] = {}

    def is_instance_ready(self):
        core_ec2_client = self.ec2_resource.meta.client
        new_instance_id = self.state_file_content['EC2']['InstanceId']

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

    def updated_state_file_content(self):
        return self.state_file_content
