output "load_balancer_sg_id" {
  value = aws_security_group.load_balancer_sg.id
}

output "ec2_sg_id" {
  value = aws_security_group.ec2_sg.id
}