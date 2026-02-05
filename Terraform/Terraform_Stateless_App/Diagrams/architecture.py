"""
Architecture Diagram — Terraform Stateless Application

This diagram represents:

- Internet-facing ALB in public subnets
- NAT Gateways for outbound traffic
- Private subnets hosting stateless EC2 container workloads
- Auto Scaling Group across AZs
- Zero-trust administrative access via AWS SSM (no SSH)

"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.network import VPC, PublicSubnet, PrivateSubnet, InternetGateway, NATGateway, ALB
from diagrams.aws.compute import EC2AutoScaling, EC2
from diagrams.aws.management import SystemsManager
from diagrams.onprem.network import Internet


# Diagram definition
with Diagram("Terraform Stateless App Architecture", show=False, direction="TB"):

    # External users accessing the system
    internet = Internet("Internet")

    # Core network container
    with Cluster("AWS VPC"):

        vpc = VPC("VPC")

        # Internet Gateway for public connectivity
        igw = InternetGateway("Internet Gateway")

        # Public Subnets Layer
        with Cluster("Public Subnets (Multi-AZ)"):
            public_subnet_1 = PublicSubnet("Public Subnet AZ1")
            public_subnet_2 = PublicSubnet("Public Subnet AZ2")

            # NAT Gateways provide outbound internet access for private workloads
            nat_1 = NATGateway("NAT Gateway AZ1")
            nat_2 = NATGateway("NAT Gateway AZ2")

            # Application Load Balancer exposed to internet
            alb = ALB("Application Load Balancer")

        # Private Subnets Layer
        with Cluster("Private Subnets (App Layer)"):
            private_subnet_1 = PrivateSubnet("Private Subnet AZ1")
            private_subnet_2 = PrivateSubnet("Private Subnet AZ2")

            # Auto Scaling group managing stateless EC2 container instances
            asg = EC2AutoScaling("Auto Scaling Group")

            ec2_instances = EC2("EC2 Container Instances\n(nginxdemos/hello)")

        # Management Layer
        ssm = SystemsManager("AWS SSM\n(No SSH Exposure)")

    # Traffic Flow Definitions

    # Internet to Load Balancer
    internet >> alb

    # ALB sits in public subnets
    alb >> public_subnet_1
    alb >> public_subnet_2

    # Public subnets connect through IGW
    public_subnet_1 >> igw
    public_subnet_2 >> igw

    # NAT gateways inside public subnets
    public_subnet_1 >> nat_1
    public_subnet_2 >> nat_2

    # NAT provides outbound for private subnets
    nat_1 >> private_subnet_1
    nat_2 >> private_subnet_2

    # ALB forwards traffic to application layer
    alb >> asg >> ec2_instances

    # EC2 instances live inside private subnets
    private_subnet_1 >> ec2_instances
    private_subnet_2 >> ec2_instances

    # Zero-trust admin access via SSM
    ssm >> Edge(style="dashed") >> ec2_instances
