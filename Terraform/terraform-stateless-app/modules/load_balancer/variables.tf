variable "name_prefix" {
  description = "Prefix for resource names and tags."
  type        = string
}

variable "vpc_id" {
  description = "ID of the VPC."
  type        = string
}

variable "public_subnets" {
  description = "Public subnet IDs the ALB is placed in."
  type        = list(string)
}

variable "load_balancer_sg_id" {
  description = "Security group ID for the ALB."
  type        = string
}

variable "target_port" {
  description = "Port on the instances the target group forwards to."
  type        = number
  default     = 80
}

variable "health_check_path" {
  description = "HTTP path used for target health checks."
  type        = string
  default     = "/"
}

variable "certificate_arn" {
  description = "ACM certificate ARN. Empty string disables HTTPS."
  type        = string
  default     = ""
}

variable "enable_deletion_protection" {
  description = "Enable deletion protection on the ALB."
  type        = bool
  default     = false
}
