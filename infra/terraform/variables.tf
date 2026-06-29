variable "aws_region" {
  description = "AWS region to deploy to"
  default     = "us-east-1"
  type        = string
}

variable "app_name" {
  description = "Application name used for resource naming"
  default     = "djangoforge"
  type        = string
}

variable "environment" {
  description = "Environment name (production, staging)"
  default     = "production"
  type        = string
}

variable "db_instance_class" {
  description = "RDS instance class"
  default     = "db.t3.micro"
  type        = string
}

variable "ecs_cpu" {
  description = "ECS task CPU units (256, 512, 1024, 2048, 4096)"
  default     = 512
  type        = number
}

variable "ecs_memory" {
  description = "ECS task memory in MB"
  default     = 1024
  type        = number
}

variable "ecs_desired_count" {
  description = "Number of ECS tasks to run"
  default     = 2
  type        = number
}

variable "domain_name" {
  description = "Domain name for the application (e.g. djangoforge.dev)"
  type        = string
}
