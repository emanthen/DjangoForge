variable "app_name" { type = string }
variable "environment" { type = string }
variable "ecr_repository_url" { type = string }
variable "vpc_id" { type = string }
variable "private_subnet_ids" { type = list(string) }
variable "target_group_arn" { type = string }
variable "secrets_arn" { type = string }
variable "ecs_cpu" { type = number; default = 512 }
variable "ecs_memory" { type = number; default = 1024 }
variable "ecs_desired_count" { type = number; default = 2 }
