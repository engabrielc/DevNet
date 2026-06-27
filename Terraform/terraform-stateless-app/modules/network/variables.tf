variable "name_prefix" {
  description = "Prefix for resource names and tags."
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
}

variable "az_count" {
  description = "Number of AZs to spread subnets across."
  type        = number
}

variable "single_nat_gateway" {
  description = "Use a single shared NAT Gateway instead of one per AZ."
  type        = bool
  default     = false
}

variable "enable_flow_logs" {
  description = "Enable VPC Flow Logs to CloudWatch."
  type        = bool
  default     = true
}

variable "flow_logs_retention_days" {
  description = "Retention period for the flow logs CloudWatch Log Group."
  type        = number
  default     = 30
}
