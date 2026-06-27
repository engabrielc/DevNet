output "autoscaling_group_name" {
  description = "Name of the Auto Scaling Group."
  value       = aws_autoscaling_group.this.name
}

output "launch_template_id" {
  description = "ID of the launch template."
  value       = aws_launch_template.this.id
}

output "ami_id" {
  description = "Resolved Amazon Linux 2023 AMI ID in use."
  value       = data.aws_ssm_parameter.al2023_ami.value
}
