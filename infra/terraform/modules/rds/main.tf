resource "aws_db_subnet_group" "main" {
  name       = "${var.app_name}-${var.environment}"
  subnet_ids = var.private_subnet_ids
}

resource "aws_security_group" "rds" {
  name        = "${var.app_name}-rds-${var.environment}"
  description = "RDS security group"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.web_sg_id]
  }
}

resource "aws_db_instance" "main" {
  identifier        = "${var.app_name}-${var.environment}"
  engine            = "postgres"
  engine_version    = "16"
  instance_class    = var.db_instance_class
  allocated_storage = 20
  storage_encrypted = true

  db_name  = "djangoforge"
  username = "djangoforge"
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false
  multi_az               = false

  backup_retention_period = 7
  backup_window           = "03:00-04:00"
  maintenance_window      = "Mon:04:00-Mon:05:00"

  deletion_protection     = true
  skip_final_snapshot     = false
  final_snapshot_identifier = "${var.app_name}-final-snapshot"

  performance_insights_enabled = true
}
