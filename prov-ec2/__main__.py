import pulumi
import pulumi_aws as aws

ami = aws.ec2.get_ami(
  most_recent=True,
  owners=["amazon"],
  filters=[{"name":"name","values":["amzn2-ami-hvm-*-x86_64-gp2"]}]
)

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

vpc = aws.ec2.get_vpc(default=True)
vpcSubnets = aws.ec2.get_subnets(filters=[{"name": "vpc-id", "values": [vpc.id]}])

loadBalancer = aws.lb.LoadBalancer(
  'loadbalancer',
  internal=False,
  security_groups=[group.id],
  subnets=vpcSubnets.ids,
  load_balancer_type='application'
)

targetGroup = aws.lb.TargetGroup('target-group', port=80, protocol='HTTP', target_type='ip', vpc_id=vpc.id)

listener = aws.lb.Listener("listener",
  load_balancer_arn=loadBalancer.arn,
  port=80,
  default_actions=[{
    "type": "forward",
    "target_group_arn": targetGroup.arn
  }]
)

ips = []
hostnames = []

for az in aws.get_availability_zones().names:
  if not az == 'us-west-2d':
    server = aws.ec2.Instance(
      f'web-server-{az}',
      instance_type="t2.micro",
      vpc_security_group_ids=[group.id],
      ami=ami.id,
      availability_zone=az,
      user_data="""#!/bin/bash
        echo \"Hello, World! -- from {}\" > index.html
        nohup python -m SimpleHTTPServer 80 &
        """.format(az),
      tags={
          "Name": "web-server",
      },
    )

    ips.append(server.public_ip)
    hostnames.append(server.public_dns)

    attachmennt = aws.lb.TargetGroupAttachment(
      f'web-server-{az}',
      target_group_arn=targetGroup.arn,
      target_id=server.private_ip,
      port=80
    )

pulumi.export('ips', ips)
pulumi.export('hostnames', hostnames)
pulumi.export('url', loadBalancer.dns_name)