###############################################################################
# Core / naming
###############################################################################

variable "project_name" {
  description = "Short project identifier used as a prefix for resource names and tags."
  type        = string
  default     = "stateless-app"

  validation {
    condition     = can(regex("^[a-z0-9-]{2,24}$", var.project_name))
    error_message = "project_name must be 2-24 chars, lowercase letters, digits, or hyphens."
  }
}

variable "environment" {
  description = "Deployment environment (e.g. dev, staging, prod). Used in naming and tags."
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be one of: dev, staging, prod."
  }
}

variable "region" {
  description = "AWS region to deploy into."
  type        = string
  default     = "us-east-1"
}

variable "tags" {
  description = "Additional tags merged into the default tag set on every resource."
  type        = map(string)
  default     = {}
}

###############################################################################
# Networking
###############################################################################

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.0.0.0/16"

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "vpc_cidr must be a valid IPv4 CIDR block."
  }
}

variable "az_count" {
  description = "Number of Availability Zones (and matching public/private subnet pairs) to spread across. 2+ recommended for HA."
  type        = number
  default     = 2

  validation {
    condition     = var.az_count >= 1 && var.az_count <= 4
    error_message = "az_count must be between 1 and 4."
  }
}

variable "single_nat_gateway" {
  description = "If true, create a single NAT Gateway shared by all private subnets (cheaper, lower HA). If false, one NAT Gateway per AZ (HA, higher cost)."
  type        = bool
  default     = false
}

variable "enable_flow_logs" {
  description = "Enable VPC Flow Logs to CloudWatch for network visibility and audit."
  type        = bool
  default     = true
}

variable "flow_logs_retention_days" {
  description = "CloudWatch Log Group retention for VPC Flow Logs, in days."
  type        = number
  default     = 30
}

###############################################################################
# Compute
###############################################################################

variable "instance_type" {
  description = "EC2 instance type for the application instances."
  type        = string
  default     = "t3.micro"
}

variable "asg_min_size" {
  description = "Minimum number of instances in the Auto Scaling Group."
  type        = number
  default     = 2
}

variable "asg_max_size" {
  description = "Maximum number of instances in the Auto Scaling Group."
  type        = number
  default     = 4
}

variable "asg_desired_capacity" {
  description = "Desired number of instances in the Auto Scaling Group."
  type        = number
  default     = 2
}

variable "cpu_target_utilization" {
  description = "Target average CPU utilization (%) for the ASG target-tracking scaling policy."
  type        = number
  default     = 50
}

variable "container_image" {
  description = "Container image the instances run on boot. Defaults to the public NGINX hello demo."
  type        = string
  default     = "nginxdemos/hello:latest"
}

variable "root_volume_size" {
  description = "Root EBS volume size in GiB for application instances."
  type        = number
  default     = 8
}

###############################################################################
# Load balancer / TLS
###############################################################################

variable "certificate_arn" {
  description = "ACM certificate ARN. If set, an HTTPS:443 listener is created and HTTP:80 redirects to HTTPS. If empty, traffic is served over plain HTTP:80 (demo only)."
  type        = string
  default     = ""
}

variable "enable_deletion_protection" {
  description = "Enable deletion protection on the load balancer (recommended for prod)."
  type        = bool
  default     = false
}

variable "health_check_path" {
  description = "HTTP path the target group uses for health checks."
  type        = string
  default     = "/"
}
