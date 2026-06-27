variable "name_prefix" {
  description = "Prefix for resource names and tags."
  type        = string
}

variable "vpc_id" {
  description = "ID of the VPC the security groups belong to."
  type        = string
}

variable "http_port" {
  description = "HTTP port the ALB listens on."
  type        = number
  default     = 80
}

variable "https_port" {
  description = "HTTPS port the ALB listens on."
  type        = number
  default     = 443
}

variable "app_port" {
  description = "Port the application listens on inside each instance."
  type        = number
  default     = 80
}
