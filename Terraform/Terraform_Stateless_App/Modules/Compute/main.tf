variable "private_subnets" {}
variable "ec2_sg_id" {}
variable "target_group_arn" {}
variable "instance_profile_name" {}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*"]
  }
}

resource "aws_launch_template" "launch_template" {
  name          = "Demo-LT"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = "t3.micro"
  vpc_security_group_ids = [var.ec2_sg_id]
  iam_instance_profile {
    name = var.instance_profile_name
  }

  user_data = base64encode(<<EOF
#!/bin/bash
yum update -y
amazon-linux-extras install docker -y
systemctl start docker
docker run -d -p 80:80 nginxdemos/hello
EOF
)
}

resource "aws_autoscaling_group" "asg" {
  name                = "Demo-ASG"
  min_size            = 2
  max_size            = 2
  desired_capacity    = 2
  vpc_zone_identifier = var.private_subnets
  target_group_arns  = [var.target_group_arn]

  launch_template {
    id      = aws_launch_template.launch_template.id
    version = "$Latest"
  }
}
