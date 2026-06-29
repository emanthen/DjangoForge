resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.app_name}-${var.environment}"
  subnet_ids = var.private_subnet_ids
}

resource "aws_security_group" "redis" {
  name        = "${var.app_name}-redis-${var.environment}"
  description = "ElastiCache Redis security group"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [var.web_sg_id]
  }
}

resource "aws_elasticache_cluster" "main" {
  cluster_id           = "${var.app_name}-${var.environment}"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  engine_version       = "7.0"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [aws_security_group.redis.id]
}
