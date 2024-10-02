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

server = aws.ec2.Instance(
  'web-server',
  instance_type="t2.micro",
  vpc_security_group_ids=[group.id],
  ami=ami.id,
  user_data="""#!/bin/bash
    echo \"Hello, World!\" > index.html
    nohup python -m SimpleHTTPServer 80 &
    """,
  tags={
      "Name": "web-server",
  },
)

pulumi.export('ip', server.public_ip)
pulumi.export('hostname', server.public_dns)