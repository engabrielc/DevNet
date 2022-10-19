#Provider

provider "aws" {
  region     = "us-east-1"

  #Use a Secrets Manager to provide your Access/Secret Keys .
  
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
  availability_zone = "us-east-1a"

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
    from_port        = 80
    to_port          = 80
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
  depends_on = [aws_internet_gateway.Production-igw]
  
}

#EC2 (WebServer)

resource "aws_instance" "WebServer" {
  ami           = "ami-026b57f3c383c2eec"
  instance_type = "t2.micro"
  availability_zone = "us-east-1a"
  key_name = "FortigateTest"

  network_interface {
    device_index = 0
    network_interface_id = aws_network_interface.Web_Server.id
  }

  user_data = <<-EOF
                #!/bin/bash
                sudo yum update -y
                sudo yum install httpd -y
                sudo systemctl start httpd
                sudo bash -c 'echo This is your Website > /var/www/html/index.html'
                EOF

        tags = {Name= "WebServer"}        
}


