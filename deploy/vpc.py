from deploy.support import Client


class VPC:

    def __init__(self, state_file_content):
        self.state_file_content = state_file_content
        self.ec2_client = Client.ec2()

    def associate_elastic_ip(self):
        instance_id = self.state_file_content['Green']['EC2']['InstanceId']

        vpc_key = self.state_file_content['Green']['EC2']['VPC']
        allocated_elastic_ip = vpc_key.get('AllocatedElasticIp', {}).get('AllocationId')
        associated_elastic_ip = vpc_key.get('AssociatedElasticIp', {}).get('AssociationId')

        if not associated_elastic_ip:
            if allocated_elastic_ip:
                response = self.ec2_client.associate_address(
                    AllocationId=allocated_elastic_ip,
                    InstanceId=instance_id,
                )
                vpc_key['AssociatedElasticIp'] = {}
                vpc_key['AssociatedElasticIp']['AssociationId'] = response['AssociationId']

                print('----> Attached an elastic IP\n')
            else:
                self.__allocate_elastic_ip()
                self.associate_elastic_ip()

    def updated_state_file_content(self):
        return self.state_file_content

    def __allocate_elastic_ip(self):
        vpc_key = self.state_file_content['Green']['EC2']['VPC']
        allocated_elastic_ip = vpc_key.get('AllocatedElasticIp', {}).get('AllocationId')

        if not allocated_elastic_ip:
            response = self.ec2_client.allocate_address(Domain='vpc')
            vpc_key['AllocatedElasticIp'] = {}
            vpc_key['AllocatedElasticIp']['PublicIp'] = response['PublicIp']
            vpc_key['AllocatedElasticIp']['AllocationId'] = response['AllocationId']

            print('----> Allocated an elastic IP\n')
        else:
            print('----> An elastic IP already allocated\n')
