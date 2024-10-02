import pulumi
import pulumi_aws as aws
import json

cluster = aws.ecs.Cluster('cluster')

vpc = aws.ec2.get_vpc(default=True)
vpcSubnets = aws.ec2.get_subnets(filters=[{"name": "vpc-id", "values": [vpc.id]}])

group = aws.ec2.SecurityGroup(
  "web-secgrp",
  description='Enable HTTP access',
  ingress=[
      { 'protocol': 'icmp', 'from_port': 8, 'to_port': 0, 'cidr_blocks': ['0.0.0.0/0'] },
      { 'protocol': 'tcp', 'from_port': 80, 'to_port': 80, 'cidr_blocks': ['0.0.0.0/0'] },
  ],
  egress=[
    { 'protocol': 'tcp', 'from_port': 80, 'to_port': 80, 'cidr_blocks': ['0.0.0.0/0'] },
  ]
)

loadBalancer = aws.lb.LoadBalancer(
  'app-lb',
  internal=False,
  security_groups=[group.id],
  subnets=vpcSubnets.ids,
  load_balancer_type='application'
)

targetGroup = aws.lb.TargetGroup('app-tg', port=80, protocol='HTTP', target_type='ip', vpc_id=vpc.id)

listener = aws.lb.Listener(
  "web",
  load_balancer_arn=loadBalancer.arn,
  port=80,
  default_actions=[{
    "type": "forward",
    "target_group_arn": targetGroup.arn
  }]
)