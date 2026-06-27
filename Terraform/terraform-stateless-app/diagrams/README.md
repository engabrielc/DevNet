# Architecture Diagram

Architecture diagram for the Terraform stateless application, generated with
the Python [Diagrams](https://github.com/mingrammer/diagrams) library so the
picture stays traceable to the actual Terraform resources.

## What it shows

- VPC boundary with public and private subnets across multiple AZs
- Internet Gateway and NAT Gateway(s) for ingress/egress separation
- Application Load Balancer as the single public entry point
- Auto Scaling Group of Amazon Linux 2023 container instances in private subnets
- IMDSv2-enforced instances with encrypted EBS volumes
- VPC Flow Logs to CloudWatch
- Zero-trust admin access via AWS SSM Session Manager (no SSH)

## Regenerate

```bash
pip install diagrams graphviz   # also install the graphviz system package
python architecture.py          # writes terraform_stateless_app_architecture.png
```
