output "target_group_arn" {
  description = "ARN of the target group instances register with."
  value       = aws_lb_target_group.this.arn
}

output "load_balancer_dns_name" {
  description = "Public DNS name of the load balancer."
  value       = aws_lb.this.dns_name
}

output "load_balancer_arn" {
  description = "ARN of the load balancer."
  value       = aws_lb.this.arn
}

output "load_balancer_zone_id" {
  description = "Hosted zone ID of the load balancer (for Route 53 alias records)."
  value       = aws_lb.this.zone_id
}
