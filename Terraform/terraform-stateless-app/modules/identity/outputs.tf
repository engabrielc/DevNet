output "instance_profile_name" {
  description = "Name of the IAM instance profile for the app instances."
  value       = aws_iam_instance_profile.ec2.name
}

output "role_arn" {
  description = "ARN of the EC2 IAM role."
  value       = aws_iam_role.ec2.arn
}
