variable "vpc_id" {}
variable "public_subnets" {}
variable "load_balancer_sg_id" {}

resource "aws_lb" "load_balancer" {
  name = "Demo-LB"
  load_balancer_type = "application"
  security_groups    = [var.load_balancer_sg_id]
  subnets            = var.public_subnets

  tags = {
    Name = "Demo_Load_Balancer"
  }
}

resource "aws_lb_target_group" "target_group" {
  name = "Demo-TG"
  port     = 80
  protocol = "HTTP"
  vpc_id   = var.vpc_id

  health_check {
    path = "/"
  }

  tags = {
    Name = "Demo_Target_Group"
  }
    
 

}

resource "aws_lb_listener" "listener" {
  load_balancer_arn = aws_lb.load_balancer.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.target_group.arn
  }
}

