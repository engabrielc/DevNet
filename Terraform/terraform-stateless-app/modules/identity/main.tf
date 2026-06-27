###############################################################################
# Identity module
#
# IAM role + instance profile granting the app instances SSM access (for
# Session Manager / no-SSH administration) without any inbound access.
###############################################################################

data "aws_iam_policy_document" "ec2_assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ec2" {
  name_prefix           = "${var.name_prefix}-ec2-"
  assume_role_policy    = data.aws_iam_policy_document.ec2_assume.json
  force_detach_policies = true

  tags = {
    Name = "${var.name_prefix}-ec2-role"
  }
}

# AWS-managed policy enabling SSM Session Manager (zero-trust admin, no SSH).
resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.ec2.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "ec2" {
  name_prefix = "${var.name_prefix}-ec2-"
  role        = aws_iam_role.ec2.name

  lifecycle {
    create_before_destroy = true
  }
}
