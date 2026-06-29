terraform {
  required_version = ">= 1.7"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket = "djangoforge-terraform-state"
    key    = "production/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project     = var.app_name
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

module "vpc" {
  source      = "./modules/vpc"
  app_name    = var.app_name
  environment = var.environment
}

module "ecr" {
  source      = "./modules/ecr"
  app_name    = var.app_name
  environment = var.environment
}

module "s3" {
  source      = "./modules/s3"
  app_name    = var.app_name
  environment = var.environment
}

module "secrets" {
  source      = "./modules/secrets"
  app_name    = var.app_name
  environment = var.environment
}

module "rds" {
  source            = "./modules/rds"
  app_name          = var.app_name
  environment       = var.environment
  db_instance_class = var.db_instance_class
  vpc_id            = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  web_sg_id         = module.ecs.web_sg_id
}

module "elasticache" {
  source             = "./modules/elasticache"
  app_name           = var.app_name
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  web_sg_id          = module.ecs.web_sg_id
}

module "alb" {
  source            = "./modules/alb"
  app_name          = var.app_name
  environment       = var.environment
  vpc_id            = module.vpc.vpc_id
  public_subnet_ids = module.vpc.public_subnet_ids
  domain_name       = var.domain_name
}

module "cloudwatch" {
  source      = "./modules/cloudwatch"
  app_name    = var.app_name
  environment = var.environment
  alb_arn_suffix = module.alb.alb_arn_suffix
  ecs_cluster = var.app_name
}

module "ecs" {
  source             = "./modules/ecs"
  app_name           = var.app_name
  environment        = var.environment
  ecr_repository_url = module.ecr.repository_url
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  target_group_arn   = module.alb.target_group_arn
  secrets_arn        = module.secrets.secret_arn
  ecs_cpu            = var.ecs_cpu
  ecs_memory         = var.ecs_memory
  ecs_desired_count  = var.ecs_desired_count
}
