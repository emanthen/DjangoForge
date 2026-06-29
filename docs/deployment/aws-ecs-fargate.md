# AWS ECS Fargate Deployment Guide

Deploy DjangoForge to production on AWS ECS Fargate with a fully managed PostgreSQL (RDS), Redis (ElastiCache), and load balancer (ALB).

---

## Architecture

```
Internet
  │
  ▼
Route 53 (DNS)
  │
  ▼
ALB (Application Load Balancer)
  ├── HTTP → HTTPS redirect
  └── HTTPS → Target Group
                │
       ┌────────┴────────┐
       │                 │
  ECS Service        ECS Service
  (web)              (worker)
  Gunicorn           Celery
       │
  Secrets Manager ──── RDS PostgreSQL
  (env vars)           (private subnet)
       │
  ElastiCache Redis
  (private subnet)
       │
  S3 (user media / static files)
```

All compute runs as Fargate tasks (serverless containers — no EC2 instances to manage).

---

## Prerequisites

| Tool | Install |
|------|---------|
| AWS CLI v2 | [aws.amazon.com/cli](https://aws.amazon.com/cli/) |
| Terraform ≥ 1.7 | [developer.hashicorp.com/terraform](https://developer.hashicorp.com/terraform/install) |
| Docker | [docs.docker.com](https://docs.docker.com/get-docker/) |
| A domain in Route 53 | AWS Console → Route 53 |

Configure AWS CLI:
```bash
aws configure
# AWS Access Key ID: [your key]
# AWS Secret Access Key: [your secret]
# Default region: us-east-1
# Default output format: json
```

---

## Step 1: Create Terraform state bucket

Terraform state is stored remotely in S3 so the team can collaborate:

```bash
aws s3 mb s3://djangoforge-terraform-state --region us-east-1
aws s3api put-bucket-versioning \
  --bucket djangoforge-terraform-state \
  --versioning-configuration Status=Enabled
aws s3api put-bucket-encryption \
  --bucket djangoforge-terraform-state \
  --server-side-encryption-configuration \
  '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
```

---

## Step 2: Create IAM user for GitHub Actions

```bash
# Create user
aws iam create-user --user-name djangoforge-deployer

# Attach required policies
aws iam attach-user-policy \
  --user-name djangoforge-deployer \
  --policy-arn arn:aws:iam::aws:policy/AmazonECS_FullAccess
aws iam attach-user-policy \
  --user-name djangoforge-deployer \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess

# Create access key (save these — you won't see the secret again)
aws iam create-access-key --user-name djangoforge-deployer
```

---

## Step 3: Configure Terraform variables

Copy and edit the production tfvars:

```bash
cd infra/terraform
cp environments/production/terraform.tfvars.example environments/production/terraform.tfvars
```

Edit `terraform.tfvars`:

```hcl
aws_region      = "us-east-1"
project_name    = "djangoforge"
environment     = "production"
domain_name     = "yourdomain.com"

# RDS
db_instance_class = "db.t3.small"
db_name           = "djangoforge"
db_username       = "djangoforge"

# ElastiCache
redis_node_type = "cache.t3.micro"

# ECS
web_desired_count    = 2
worker_desired_count = 1
cpu                  = 512   # 0.5 vCPU
memory               = 1024  # 1 GB
```

---

## Step 4: Deploy infrastructure

```bash
cd infra/terraform
terraform init
terraform plan -var-file=environments/production/terraform.tfvars
terraform apply -var-file=environments/production/terraform.tfvars
```

This takes ~15 minutes. Note the outputs:

```
alb_dns_name       = "djangoforge-prod-alb-123456789.us-east-1.elb.amazonaws.com"
ecr_repository_url = "123456789.dkr.ecr.us-east-1.amazonaws.com/djangoforge"
rds_endpoint       = "djangoforge-prod.cluster-xxx.us-east-1.rds.amazonaws.com"
redis_endpoint     = "djangoforge-prod.xxx.ng.0001.use1.cache.amazonaws.com"
secrets_arn        = "arn:aws:secretsmanager:us-east-1:..."
```

---

## Step 5: Point your domain to the ALB

In Route 53, create an A record (Alias) for `yourdomain.com` pointing to `alb_dns_name` from the Terraform output.

Wait for DNS propagation (~5 minutes). Test:

```bash
nslookup yourdomain.com
# Should return the ALB IP
```

---

## Step 6: Set application secrets

```bash
# Get the database password from Terraform state
terraform output -raw db_password

# Update Secrets Manager with all required env vars
aws secretsmanager update-secret \
  --secret-id djangoforge/production/app \
  --secret-string '{
    "SECRET_KEY": "your-50-char-random-key",
    "DATABASE_URL": "postgres://djangoforge:<password>@<rds_endpoint>:5432/djangoforge?sslmode=require",
    "REDIS_URL": "redis://<redis_endpoint>:6379/0",
    "STRIPE_SECRET_KEY": "sk_live_...",
    "STRIPE_WEBHOOK_SECRET": "whsec_...",
    "STRIPE_LIVE_MODE": "True",
    "ANYMAIL_MAILGUN_API_KEY": "key-...",
    "ANYMAIL_MAILGUN_SENDER_DOMAIN": "mail.yourdomain.com",
    "SENTRY_DSN": "https://...",
    "ALLOWED_HOSTS": "yourdomain.com,www.yourdomain.com",
    "DJANGO_SETTINGS_MODULE": "config.settings.production"
  }'
```

---

## Step 7: Add GitHub Secrets

In your GitHub repo → Settings → Secrets → Actions:

| Secret | Value |
|--------|-------|
| `AWS_ACCESS_KEY_ID` | From Step 2 |
| `AWS_SECRET_ACCESS_KEY` | From Step 2 |
| `AWS_REGION` | `us-east-1` |
| `ECR_REPOSITORY` | From Terraform `ecr_repository_url` |
| `ECS_CLUSTER` | `djangoforge-production` |
| `ECS_SERVICE_WEB` | `djangoforge-production-web` |
| `ECS_SERVICE_WORKER` | `djangoforge-production-worker` |

---

## Step 8: First deployment

Push to the `main` branch to trigger the GitHub Actions deploy pipeline:

```bash
git push origin main
```

The pipeline:
1. Runs tests and linting
2. Builds Docker image and pushes to ECR
3. Runs `python manage.py migrate` as a one-off ECS task
4. Updates the ECS web service (rolling deploy — zero downtime)
5. Updates the ECS worker service
6. Waits for stability

Monitor in GitHub Actions → the deploy workflow. Total time: ~8 minutes.

---

## Step 9: Seed initial data (optional)

```bash
aws ecs run-task \
  --cluster djangoforge-production \
  --task-definition djangoforge-production-web \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[PRIVATE_SUBNET_ID],securityGroups=[WEB_SG_ID],assignPublicIp=DISABLED}" \
  --overrides '{"containerOverrides":[{"name":"djangoforge","command":["python","manage.py","seed_data"]}]}'
```

Get subnet and security group IDs from Terraform outputs.

---

## Step 10: Verify deployment

```bash
# Check services are running
aws ecs describe-services \
  --cluster djangoforge-production \
  --services djangoforge-production-web djangoforge-production-worker

# Should show "runningCount" matching "desiredCount"
```

Visit `https://yourdomain.com/api/health/` — should return `{"status": "ok"}`.

---

## Scaling

### Horizontal scaling (more tasks)

```bash
aws ecs update-service \
  --cluster djangoforge-production \
  --service djangoforge-production-web \
  --desired-count 4
```

Or update `web_desired_count` in `terraform.tfvars` and re-apply.

### Vertical scaling (more CPU/RAM)

Update `cpu` and `memory` in `terraform.tfvars` and re-apply. ECS will replace tasks with the new resource allocation.

### Auto-scaling

The Terraform module includes a CloudWatch-based auto-scaling policy that scales the web service between 2 and 10 tasks based on CPU utilization (target: 70%).

---

## Viewing logs

Logs are sent to CloudWatch Logs:

```bash
# Web service logs
aws logs tail /ecs/djangoforge-production/web --follow

# Worker service logs
aws logs tail /ecs/djangoforge-production/worker --follow
```

Or view in the AWS Console → CloudWatch → Log Groups.

---

## Running management commands

To run any Django management command in production:

```bash
aws ecs run-task \
  --cluster djangoforge-production \
  --task-definition djangoforge-production-web \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[PRIVATE_SUBNET_ID],securityGroups=[WEB_SG_ID],assignPublicIp=DISABLED}" \
  --overrides '{"containerOverrides":[{"name":"djangoforge","command":["python","manage.py","YOUR_COMMAND"]}]}'
```

---

## Updating application secrets

When you need to rotate a key (e.g., new Stripe key):

```bash
# Update the secret
aws secretsmanager update-secret \
  --secret-id djangoforge/production/app \
  --secret-string '{"STRIPE_SECRET_KEY": "sk_live_new..."}'

# Force a new deployment to pick up the new secret
aws ecs update-service \
  --cluster djangoforge-production \
  --service djangoforge-production-web \
  --force-new-deployment
```

---

## Destroying infrastructure

**WARNING: This deletes all data including the database.**

```bash
# First: disable RDS deletion protection
aws rds modify-db-instance \
  --db-instance-identifier djangoforge-production \
  --no-deletion-protection \
  --apply-immediately

# Then: destroy everything
terraform destroy -var-file=environments/production/terraform.tfvars
```

---

## Terraform modules

| Module | Resources |
|--------|-----------|
| `vpc` | VPC, public/private subnets, NAT Gateway, Internet Gateway |
| `ecr` | ECR repository with lifecycle policy |
| `rds` | RDS PostgreSQL 16, parameter group, subnet group, security group |
| `elasticache` | Redis 7, subnet group, security group |
| `alb` | ALB, HTTP→HTTPS redirect, HTTPS listener, ACM certificate |
| `ecs` | Cluster, task definitions, services, IAM roles, auto-scaling |
| `s3` | Media bucket, static bucket, CloudFront distribution |
| `secrets` | Secrets Manager secret, IAM policy |
| `cloudwatch` | Log groups, metric alarms, SNS alerts |

---

## Estimated AWS costs

For a small SaaS (~1000 active users):

| Service | Monthly cost |
|---------|-------------|
| ECS Fargate (2 web tasks, 1 worker) | ~$35 |
| RDS PostgreSQL db.t3.small | ~$28 |
| ElastiCache cache.t3.micro | ~$13 |
| ALB | ~$18 |
| NAT Gateway | ~$35 |
| S3 + CloudFront | ~$5 |
| Secrets Manager | ~$1 |
| CloudWatch | ~$3 |
| **Total** | **~$138/month** |

Costs scale with traffic and data volume. Use [AWS Pricing Calculator](https://calculator.aws/) for your specific usage.
