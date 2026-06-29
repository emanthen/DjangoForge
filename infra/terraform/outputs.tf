output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = module.alb.alb_dns_name
}

output "ecr_repository_url" {
  description = "ECR repository URL for pushing images"
  value       = module.ecr.repository_url
}

output "rds_endpoint" {
  description = "RDS database endpoint"
  value       = module.rds.endpoint
  sensitive   = true
}

output "elasticache_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = module.elasticache.endpoint
  sensitive   = true
}

output "secrets_manager_arn" {
  description = "ARN of the Secrets Manager secret"
  value       = module.secrets.secret_arn
}
