###############################################################################
# Root module: wires the building blocks together.
#
# Dependency flow:
#   network  ->  security  ->  load_balancer  ->  compute
#   identity (standalone) ----------------------^
###############################################################################

module "network" {
  source = "./modules/network"

  name_prefix              = local.name_prefix
  vpc_cidr                 = var.vpc_cidr
  az_count                 = var.az_count
  single_nat_gateway       = var.single_nat_gateway
  enable_flow_logs         = var.enable_flow_logs
  flow_logs_retention_days = var.flow_logs_retention_days
}

module "security" {
  source = "./modules/security"

  name_prefix = local.name_prefix
  vpc_id      = module.network.vpc_id
  https_port  = 443
  http_port   = 80
}

module "identity" {
  source = "./modules/identity"

  name_prefix = local.name_prefix
}

module "load_balancer" {
  source = "./modules/load_balancer"

  name_prefix                = local.name_prefix
  vpc_id                     = module.network.vpc_id
  public_subnets             = module.network.public_subnets
  load_balancer_sg_id        = module.security.load_balancer_sg_id
  certificate_arn            = var.certificate_arn
  enable_deletion_protection = var.enable_deletion_protection
  health_check_path          = var.health_check_path
}

module "compute" {
  source = "./modules/compute"

  name_prefix            = local.name_prefix
  private_subnets        = module.network.private_subnets
  ec2_sg_id              = module.security.ec2_sg_id
  target_group_arn       = module.load_balancer.target_group_arn
  instance_profile_name  = module.identity.instance_profile_name
  instance_type          = var.instance_type
  min_size               = var.asg_min_size
  max_size               = var.asg_max_size
  desired_capacity       = var.asg_desired_capacity
  cpu_target_utilization = var.cpu_target_utilization
  container_image        = var.container_image
  root_volume_size       = var.root_volume_size
}
