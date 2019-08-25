#!/bin/bash

sudo yum update -y && sudo yum install -y docker jq
sudo usermod -aG docker $USER
sudo newgrp docker
sudo service docker start
sudo chkconfig docker on

export AWS_ACCOUNT_ID=daniel

aws ssm get-parameters \
  --region us-east-1 \
  --names \
    POSTGRESQL_HOST \
    POSTGRESQL_PASSWORD \
    POSTGRESQL_DATABASE \
    POSTGRESQL_USERNAME \
  --query "Parameters[*].{Name:Name,Value:Value}" | \
    for i in $(jq -c '.[]'); do
       _jq() {
         echo ${i} | jq -r ${1}
      }
      psql_env_name=$(_jq '.Name')
      psql_env_value=$(_jq '.Value')

      echo export $psql_env_name=$psql_env_value >> .env
    done

source .env
aws ecr get-login --no-include-email --region us-east-1 | /bin/bash

docker pull $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ecr-daniel-test
docker run --name daleponto \
           -d \
           -p 80:3000 \
           -e POSTGRESQL_HOST=$POSTGRESQL_HOST \
           -e POSTGRESQL_USERNAME=$POSTGRESQL_USERNAME \
           -e POSTGRESQL_PASSWORD=$POSTGRESQL_PASSWORD \
           -e POSTGRESQL_DATABASE=$POSTGRESQL_DATABASE \
           $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ecr-daniel-test
