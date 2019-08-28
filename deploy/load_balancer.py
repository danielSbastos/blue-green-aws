from deploy.support import Resource, Client


class LoadBalancer:

    def __init__(self, state_file_content):
        self.state_file_content = state_file_content
        self.load_balancer_client = Client().load_balancer()

    def create(self):
        response = self.load_balancer_client.create_load_balancer(
            LoadBalancerName='daniel-test-lb',
            Listeners=[
                {
                    'Protocol': 'HTTP',
                    'LoadBalancerPort': 80,
                    'InstanceProtocol': 'HTTP',
                    'InstancePort': 80,
                },
            ],
            AvailabilityZones=[
                'us-east-1a',
                'us-east-1b'
            ],
        )
        self.state_file_content['LoadBalancer'] = {
            'Name': 'daniel-test-lb',
            'DNSName': response['DNSName']
        }

    def instances_healthy(self):
        response = self.load_balancer_client.describe_instance_health(
            LoadBalancerName=self.state_file_content['LoadBalancer']['Name']
        )
        while not all(s['State'] == 'InService' for s in response['InstanceStates']):
            return self.instances_healthy()
        return True

    def updated_state_file_content(self):
        return self.state_file_content
