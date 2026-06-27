# Terraform Stateless Application

Production-style Terraform that deploys a stateless containerized application
(the public NGINX hello demo, swappable) on AWS behind an Application Load
Balancer, with workloads isolated in private subnets across multiple
Availability Zones.

## Architecture

```
Internet
   │
   ▼
Application Load Balancer        (public subnets, multi-AZ)
   │   HTTP :80  ─ or ─  HTTPS :443 (+ HTTP→HTTPS redirect when a cert is set)
   ▼
Auto Scaling Group               (private subnets, multi-AZ)
   └─ Amazon Linux 2023 instances running the app container
        • IMDSv2 enforced, encrypted EBS, detailed monitoring
        • SSM Session Manager for admin access (no SSH, no public IPs)
        • Outbound via NAT Gateway(s)
```

See `diagrams/` for the generated diagram.

## What's in here

```
terraform-stateless-app/
├── versions.tf              # Terraform & provider constraints, optional S3 backend
├── providers.tf             # AWS provider + default_tags
├── variables.tf             # Typed, validated, documented inputs
├── locals.tf                # Naming prefix and common tags
├── main.tf                  # Module wiring
├── outputs.tf               # Outputs (app URL, VPC, subnets, ASG name, ...)
├── terraform.tfvars.example # Copy to terraform.tfvars and edit
├── .gitignore
├── modules/
│   ├── network/             # VPC, subnets, IGW, NAT, routes, flow logs
│   ├── security/            # ALB + EC2 security groups (standalone rules)
│   ├── load_balancer/       # ALB, target group, HTTP/HTTPS listeners
│   ├── compute/             # Launch template + ASG + scaling policy
│   └── identity/            # IAM role + instance profile (SSM)
└── diagrams/                # Architecture diagram (Python "diagrams")
```

## Prerequisites

- Terraform >= 1.5 (or OpenTofu >= 1.6)
- AWS credentials configured (`aws configure`, environment variables, or an
  assumed role)
- Permissions to create VPC, EC2/ASG, ELB, IAM, and CloudWatch resources

## Quick start

```bash
cp terraform.tfvars.example terraform.tfvars   # then edit values
terraform init
terraform fmt -check
terraform validate
terraform plan
terraform apply
```

When the apply finishes, open the `application_url` output in a browser.

```bash
terraform output application_url
```

Tear everything down with:

```bash
terraform destroy
```

## Configuration

All inputs are defined in `variables.tf` with types, validation, and defaults.
The common ones:

| Variable | Default | Purpose |
| --- | --- | --- |
| `project_name` / `environment` | `stateless-app` / `dev` | Naming and tags |
| `region` | `us-east-1` | AWS region |
| `vpc_cidr` | `10.0.0.0/16` | VPC address space |
| `az_count` | `2` | AZs / subnet pairs (HA) |
| `single_nat_gateway` | `false` | One shared NAT (cheaper) vs per-AZ (HA) |
| `instance_type` | `t3.micro` | App instance size |
| `asg_min/max/desired` | `2 / 4 / 2` | Auto Scaling Group bounds |
| `cpu_target_utilization` | `50` | Target-tracking CPU % |
| `container_image` | `nginxdemos/hello:latest` | App container |
| `certificate_arn` | `""` | Set to enable HTTPS + redirect |
| `enable_flow_logs` | `true` | VPC Flow Logs to CloudWatch |
| `enable_deletion_protection` | `false` | ALB deletion protection |

## Security design

- **No public compute.** Instances run in private subnets with no public IPs;
  the ALB is the only internet-facing component.
- **Least-privilege security groups.** The app SG accepts traffic only from the
  ALB SG. Rules are defined as standalone `aws_vpc_security_group_*_rule`
  resources to avoid the drift inline rules can cause.
- **No SSH.** Administrative access is via AWS Systems Manager Session Manager
  through an IAM instance profile — no key pairs, no inbound SSH.
- **IMDSv2 enforced** on the launch template to mitigate SSRF-based credential
  theft, with the hop limit pinned to 1.
- **Encrypted storage.** Root EBS volumes use gp3 with encryption enabled.
- **Network visibility.** VPC Flow Logs (toggleable) stream to CloudWatch.
- **TLS-ready.** Provide an ACM `certificate_arn` to get an HTTPS:443 listener
  with a modern TLS 1.3 policy and an automatic HTTP→HTTPS redirect.

### Production hardening to consider next

- AWS WAF on the ALB for Layer 7 / OWASP Top 10 protection
- ALB access logs to S3
- VPC interface endpoints (SSM, ECR, CloudWatch) to keep traffic off the NAT
- Remote state with locking (see the commented backend in `versions.tf`)
- A CI pipeline running `fmt`, `validate`, `tflint`, and a security scanner
  (e.g. `tfsec` / `checkov`)

## Notes on cost

NAT Gateways and the ALB bill hourly plus data processing. For non-production
experimentation, set `single_nat_gateway = true` to run one NAT instead of one
per AZ. Remember to `terraform destroy` when you're done.

## Notable changes from the original

- Fixed module source paths (`./modules/...`) to match directory names — the
  original mixed `Modules/Network` with `./modules/network`, which fails on
  case-sensitive filesystems.
- Replaced the Amazon Linux 2 AMI name-filter + `amazon-linux-extras` bootstrap
  with the latest **Amazon Linux 2023** AMI (resolved via SSM) and a dnf-based
  Docker install.
- Parameterized and validated all inputs; added consistent tagging via
  `default_tags`, version pinning, and an optional remote-state backend.
- Real autoscaling (target tracking, ELB health checks, instance refresh)
  instead of a fixed `min = max = 2` group.
- Added IMDSv2 enforcement, EBS encryption, detailed monitoring, VPC Flow Logs,
  and an optional HTTPS path.

---

Originally created by Enrique Gabriel; modernized to current Terraform/AWS
best practices.
