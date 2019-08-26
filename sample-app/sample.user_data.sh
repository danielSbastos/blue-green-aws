#!/bin/bash

sudo yum update -y && sudo yum install -y docker
sudo usermod -aG docker $USER
sudo newgrp docker
sudo service docker start
sudo chkconfig docker on

export AWS_ACCESS_KEY_ID=<AWS_ACCESS_KEY_ID>
export AWS_SECRET_ACCESS_KEY=<AWS_SECRET_ACCESS_KEY>

aws ecr get-login --no-include-email --region us-east-1 | /bin/bash

docker run -p 80:5000 <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/<ECR_NAME>
