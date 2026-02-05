terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

module "network" {
  source = "./modules/network"
}

module "security" {
  source = "./modules/security"
  vpc_id = module.network.vpc_id
}

module "load_balancer" {
  source = "./modules/load_balancer"
  vpc_id = module.network.vpc_id
  public_subnets = module.network.public_subnets
  load_balancer_sg_id = module.security.load_balancer_sg_id
}

module "compute" {
  source           = "./modules/compute"
  private_subnets  = module.network.private_subnets
  ec2_sg_id        = module.security.ec2_sg_id
  target_group_arn = module.load_balancer.target_group_arn
  instance_profile_name = module.identity.instance_profile_name
}

module "identity" {
  source = "./modules/identity"
}