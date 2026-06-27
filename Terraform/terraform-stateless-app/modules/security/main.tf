###############################################################################
# Security module
#
# Two security groups:
#   - ALB SG: accepts inbound web traffic from the internet, forwards to EC2.
#   - EC2 SG: accepts traffic only from the ALB SG (no public exposure).
#
# Uses standalone aws_vpc_security_group_*_rule resources (the modern,
# drift-free pattern) and name_prefix to avoid name-collision on replace.
###############################################################################

resource "aws_security_group" "alb" {
  name_prefix = "${var.name_prefix}-alb-"
  description = "ALB ingress from the internet; egress to app instances."
  vpc_id      = var.vpc_id

  tags = {
    Name = "${var.name_prefix}-alb-sg"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group" "ec2" {
  name_prefix = "${var.name_prefix}-ec2-"
  description = "App instances; ingress only from the ALB."
  vpc_id      = var.vpc_id

  tags = {
    Name = "${var.name_prefix}-ec2-sg"
  }

  lifecycle {
    create_before_destroy = true
  }
}

###############################################################################
# ALB rules
###############################################################################

resource "aws_vpc_security_group_ingress_rule" "alb_http" {
  security_group_id = aws_security_group.alb.id
  description       = "HTTP from internet"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = var.http_port
  to_port           = var.http_port
}

resource "aws_vpc_security_group_ingress_rule" "alb_https" {
  security_group_id = aws_security_group.alb.id
  description       = "HTTPS from internet"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = var.https_port
  to_port           = var.https_port
}

# ALB only needs to reach the app instances on the app port.
resource "aws_vpc_security_group_egress_rule" "alb_to_ec2" {
  security_group_id            = aws_security_group.alb.id
  description                  = "Forward to app instances"
  referenced_security_group_id = aws_security_group.ec2.id
  ip_protocol                  = "tcp"
  from_port                    = var.app_port
  to_port                      = var.app_port
}

###############################################################################
# EC2 (app) rules
###############################################################################

resource "aws_vpc_security_group_ingress_rule" "ec2_from_alb" {
  security_group_id            = aws_security_group.ec2.id
  description                  = "App traffic from ALB only"
  referenced_security_group_id = aws_security_group.alb.id
  ip_protocol                  = "tcp"
  from_port                    = var.app_port
  to_port                      = var.app_port
}

# Outbound is open so instances can pull OS packages and container images
# through the NAT Gateway. Lock this down further with VPC endpoints in prod.
resource "aws_vpc_security_group_egress_rule" "ec2_all" {
  security_group_id = aws_security_group.ec2.id
  description       = "Outbound for package and image pulls (via NAT)"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}
