
#Provider

provider "aws" {
  region     = "ap-south-1"
  access_key = var.access_key
  secret_key = var.secret_key
}

#Variables to access the AWS Account
variable "access_key" {
  description = "Access Key"
}
variable "secret_key" {
  description= "Secret Key"
}

#VPC

resource "aws_vpc" "Production" {
  cidr_block = "10.200.0.0/16"

  tags = {
    Name = "Production"
  }
}

#Internet Gateway

resource "aws_internet_gateway" "Production-igw" {
  vpc_id = aws_vpc.Production.id

  tags = {
    Name = "Production-igw"
  }
}

#Custom Route Table

resource "aws_route_table" "Production" {
  vpc_id = aws_vpc.Production.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.Production-igw.id
  }
}

#Subnet

resource "aws_subnet" "Public" {
  vpc_id     = aws_vpc.Production.id
  cidr_block = "10.200.0.0/24"
  availability_zone = "ap-south-1a"

  tags = {
    Name = "Public"
  }
}

#Route Table Association

resource "aws_route_table_association" "Public" {
  subnet_id      = aws_subnet.Public.id
  route_table_id = aws_route_table.Production.id
}

#Security Group

resource "aws_security_group" "allow_all" {
  name        = "allow_all"
  description = "Allows all traffic "
  vpc_id      = aws_vpc.Production.id

ingress {
    description      = "Web"
    from_port        = 443
    to_port          = 443
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
    
  }

  ingress {
    description      = "SSH"
    from_port        = 22
    to_port          = 22
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
    
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
   
  }

  tags = {
    Name = "allow_all"
  }
}

#ENI

resource "aws_network_interface" "Web_Server" {
  subnet_id       = aws_subnet.Public.id
  private_ips     = ["10.200.0.7"]
  security_groups = [aws_security_group.allow_all.id]

}

#EIP

resource "aws_eip" "Public" {
  vpc                       = true
  network_interface         = aws_network_interface.Web_Server.id
  associate_with_private_ip = "10.200.0.7"
  depends_on = [aws_internet_gateway.Production-igw, aws_instance.WebServer ]
  
  
}

#EC2 (WebServer)

resource "aws_instance" "WebServer" {
  ami           = "ami-02f3189a4ec9e039e"
  instance_type = "c6i.xlarge"
  availability_zone = "ap-south-1a"
  key_name = "ztna-key"

  network_interface {
    device_index = 0
    network_interface_id = aws_network_interface.Web_Server.id
  }

#   user_data = <<-EOF
#                 #!/bin/bash
#                 sudo yum update -y
#                 sudo yum install httpd -y
#                 sudo systemctl start httpd
#                 sudo bash -c 'echo This is your Website > /var/www/html/index.html'
#                 EOF

#         tags = {Name= "WebServer"}        
}

#Output

output "WebServer_EC2_ID" {
  value = aws_instance.WebServer.id
  
}
