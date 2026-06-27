output "load_balancer_sg_id" {
  description = "Security group ID for the load balancer."
  value       = aws_security_group.alb.id
}

output "ec2_sg_id" {
  description = "Security group ID for the application instances."
  value       = aws_security_group.ec2.id
}
