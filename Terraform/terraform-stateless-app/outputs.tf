output "load_balancer_dns_name" {
  description = "Public DNS name of the application load balancer."
  value       = module.load_balancer.load_balancer_dns_name
}

output "application_url" {
  description = "URL to reach the application through the load balancer."
  value       = "${var.certificate_arn == "" ? "http" : "https"}://${module.load_balancer.load_balancer_dns_name}"
}

output "vpc_id" {
  description = "ID of the VPC."
  value       = module.network.vpc_id
}

output "public_subnet_ids" {
  description = "IDs of the public subnets."
  value       = module.network.public_subnets
}

output "private_subnet_ids" {
  description = "IDs of the private subnets."
  value       = module.network.private_subnets
}

output "autoscaling_group_name" {
  description = "Name of the Auto Scaling Group running the application."
  value       = module.compute.autoscaling_group_name
}
