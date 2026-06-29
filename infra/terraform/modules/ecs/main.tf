data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.app_name}-${var.environment}"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# IAM — ECS Task Execution Role
resource "aws_iam_role" "ecs_execution" {
  name = "${var.app_name}-ecs-execution-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_policy" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy" "ecs_execution_secrets" {
  name = "${var.app_name}-secrets-access"
  role = aws_iam_role.ecs_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = [var.secrets_arn]
    }]
  })
}

# IAM — ECS Task Role
resource "aws_iam_role" "ecs_task" {
  name = "${var.app_name}-ecs-task-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "ecs_task_s3" {
  name = "${var.app_name}-s3-access"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:ListBucket"]
      Resource = ["arn:aws:s3:::${var.app_name}-media-*", "arn:aws:s3:::${var.app_name}-media-*/*"]
    }]
  })
}

# Security Group
resource "aws_security_group" "web" {
  name        = "${var.app_name}-web-${var.environment}"
  description = "ECS web task security group"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "web" {
  name              = "/${var.app_name}/web"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "worker" {
  name              = "/${var.app_name}/worker"
  retention_in_days = 30
}

# ECS Task Definition — Web
resource "aws_ecs_task_definition" "web" {
  family                   = "${var.app_name}-web"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.ecs_cpu
  memory                   = var.ecs_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name  = var.app_name
    image = "${var.ecr_repository_url}:latest"
    portMappings = [{ containerPort = 8000, protocol = "tcp" }]
    secrets = [{
      name      = "DJANGO_SECRETS"
      valueFrom = var.secrets_arn
    }]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/${var.app_name}/web"
        "awslogs-region"        = data.aws_region.current.name
        "awslogs-stream-prefix" = "web"
      }
    }
    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://localhost:8000/api/health/ || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 60
    }
  }])
}

# ECS Task Definition — Worker
resource "aws_ecs_task_definition" "worker" {
  family                   = "${var.app_name}-worker"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.ecs_cpu
  memory                   = var.ecs_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name    = var.app_name
    image   = "${var.ecr_repository_url}:latest"
    command = ["celery", "-A", "config", "worker", "-l", "info"]
    secrets = [{
      name      = "DJANGO_SECRETS"
      valueFrom = var.secrets_arn
    }]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/${var.app_name}/worker"
        "awslogs-region"        = data.aws_region.current.name
        "awslogs-stream-prefix" = "worker"
      }
    }
  }])
}

# ECS Task Definition — Migrate (one-off)
resource "aws_ecs_task_definition" "migrate" {
  family                   = "${var.app_name}-migrate"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name    = var.app_name
    image   = "${var.ecr_repository_url}:latest"
    command = ["python", "manage.py", "migrate", "--no-input"]
    secrets = [{
      name      = "DJANGO_SECRETS"
      valueFrom = var.secrets_arn
    }]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/${var.app_name}/web"
        "awslogs-region"        = data.aws_region.current.name
        "awslogs-stream-prefix" = "migrate"
      }
    }
  }])
}

# ECS Service — Web
resource "aws_ecs_service" "web" {
  name            = "${var.app_name}-web"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.web.arn
  desired_count   = var.ecs_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [aws_security_group.web.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = var.target_group_arn
    container_name   = var.app_name
    container_port   = 8000
  }

  deployment_minimum_healthy_percent = 50
  deployment_maximum_percent         = 200

  lifecycle {
    ignore_changes = [task_definition, desired_count]
  }
}

# ECS Service — Worker
resource "aws_ecs_service" "worker" {
  name            = "${var.app_name}-worker"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.worker.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [aws_security_group.web.id]
    assign_public_ip = false
  }

  lifecycle {
    ignore_changes = [task_definition]
  }
}
