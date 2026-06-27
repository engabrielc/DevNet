"""
Architecture Diagram - Terraform Stateless Application

Represents the deployed infrastructure:
- Internet-facing ALB in public subnets (HTTP, or HTTPS when an ACM cert is set)
- NAT Gateway(s) for private-subnet egress (per-AZ for HA, or single shared)
- Private subnets hosting stateless container workloads on Amazon Linux 2023
- Auto Scaling Group across AZs with CPU target-tracking and ELB health checks
- IMDSv2-enforced instances, encrypted EBS, VPC Flow Logs to CloudWatch
- Zero-trust administrative access via AWS SSM Session Manager (no SSH)

Generate with:
    pip install diagrams graphviz
    python architecture.py
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.network import (
    VPC,
    PublicSubnet,
    PrivateSubnet,
    InternetGateway,
    NATGateway,
    ALB,
)
from diagrams.aws.compute import EC2AutoScaling, EC2
from diagrams.aws.management import SystemsManager, Cloudwatch
from diagrams.aws.security import IAMRole
from diagrams.onprem.network import Internet

with Diagram("Terraform Stateless App Architecture", show=False, direction="TB"):
    internet = Internet("Internet")

    with Cluster("AWS VPC (10.0.0.0/16)"):
        igw = InternetGateway("Internet Gateway")
        flow_logs = Cloudwatch("VPC Flow Logs")

        with Cluster("Public Subnets (Multi-AZ)"):
            public_az1 = PublicSubnet("Public Subnet AZ1")
            public_az2 = PublicSubnet("Public Subnet AZ2")
            nat_1 = NATGateway("NAT Gateway AZ1")
            nat_2 = NATGateway("NAT Gateway AZ2")
            alb = ALB("Application\nLoad Balancer")

        with Cluster("Private Subnets (App Layer)"):
            private_az1 = PrivateSubnet("Private Subnet AZ1")
            private_az2 = PrivateSubnet("Private Subnet AZ2")
            asg = EC2AutoScaling("Auto Scaling Group\n(CPU target tracking)")
            ec2_instances = EC2("AL2023 instances\n(container: nginxdemos/hello)\nIMDSv2 + encrypted EBS")

        iam = IAMRole("EC2 IAM Role\n(SSM)")
        ssm = SystemsManager("AWS SSM\n(no SSH)")

    # Ingress
    internet >> alb
    alb >> Edge(label="public subnets") >> [public_az1, public_az2]
    [public_az1, public_az2] >> igw

    # Egress for private workloads
    public_az1 >> nat_1
    public_az2 >> nat_2
    nat_1 >> private_az1
    nat_2 >> private_az2

    # App layer
    alb >> Edge(label="HTTP :80") >> asg >> ec2_instances
    [private_az1, private_az2] >> ec2_instances

    # Cross-cutting
    iam >> Edge(style="dotted") >> ec2_instances
    ssm >> Edge(style="dashed", label="Session Manager") >> ec2_instances
    ec2_instances >> Edge(style="dotted") >> flow_logs
