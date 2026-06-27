variable "name_prefix" {
  description = "Prefix for resource names and tags."
  type        = string
}

variable "private_subnets" {
  description = "Private subnet IDs the instances launch into."
  type        = list(string)
}

variable "ec2_sg_id" {
  description = "Security group ID applied to the instances."
  type        = string
}

variable "target_group_arn" {
  description = "ALB target group ARN the ASG registers with."
  type        = string
}

variable "instance_profile_name" {
  description = "IAM instance profile name attached to the instances."
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type."
  type        = string
  default     = "t3.micro"
}

variable "min_size" {
  description = "Minimum ASG size."
  type        = number
  default     = 2
}

variable "max_size" {
  description = "Maximum ASG size."
  type        = number
  default     = 4
}

variable "desired_capacity" {
  description = "Desired ASG capacity."
  type        = number
  default     = 2
}

variable "cpu_target_utilization" {
  description = "Target average CPU utilization (%) for scaling."
  type        = number
  default     = 50
}

variable "container_image" {
  description = "Container image to run on each instance."
  type        = string
  default     = "nginxdemos/hello:latest"
}

variable "app_port" {
  description = "Host port the container is published on."
  type        = number
  default     = 80
}

variable "root_volume_size" {
  description = "Root EBS volume size in GiB."
  type        = number
  default     = 8
}
