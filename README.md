# Scripts in Python to achieve blue/green deploy in AWS

This repo implements an approach for blue/green deploy in AWS described on this AWS [whitepaper](https://d1.awsstatic.com/whitepapers/AWS_Blue_Green_Deployments.pdf), which is the "Swap the Auto Scaling Group Behind Elastic Load Balancer"


There's a sample app which is used as our deployed application. Here's the following steps 

1) Build the sample app docker image and push it to AWS ECR;
2) Download the state file (based on [Terraform's approch](https://www.terraform.io/docs/state/index.html) from AWS S3 and set its content to a instance variable;
3) Create a launch configuration if there isn't one already created;
4) Create a classic load balancer if there isn't one already created;
5) Create a new autoscaling group
  - This autoscaling group will contain at max 2 instances. The [user-data file](https://github.com/danielSbastos/blue-green-aws/blob/master/sample-app/sample.user_data.sh) will pull the lastest app docker image.
6) Set the old autoscaling group max count to 0 and set its state to "standy by", which means that the load balancer won't send any requests to them, and will be "invisible" for it. Now, the new autoscaling group instances will receive traffic.
7) Ask if rollback is necessary
8) If yes, increase the min count of the old autoscaling group back to 1 and leave the standby state. For last, delete the new autoscaling group
9) If no, simply delete the old autoscaling group
10) Upload the updated state file back to AWS S3.
