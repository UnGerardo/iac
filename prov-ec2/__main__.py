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
  ]
)

vpc = aws.ec2.get_vpc(default=True)

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

pulumi.export('ips', ips)
pulumi.export('hostnames', hostnames)