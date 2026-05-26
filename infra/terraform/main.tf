terraform {
  required_version = ">= 1.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

module "eks" {
  source = "./modules/eks"
  environment = var.environment
}

module "rds" {
  source = "./modules/rds"
  environment = var.environment
}

module "s3" {
  source = "./modules/s3"
  environment = var.environment
}
