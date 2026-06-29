resource "aws_secretsmanager_secret" "app" {
  name        = "${var.app_name}/${var.environment}/app"
  description = "DjangoForge application secrets"
}

resource "aws_secretsmanager_secret_version" "app" {
  secret_id = aws_secretsmanager_secret.app.id
  secret_string = jsonencode({
    SECRET_KEY              = "REPLACE_WITH_REAL_SECRET_KEY"
    DATABASE_URL            = "REPLACE_WITH_REAL_DATABASE_URL"
    REDIS_URL               = "REPLACE_WITH_REAL_REDIS_URL"
    STRIPE_SECRET_KEY       = "REPLACE_WITH_REAL_STRIPE_KEY"
    STRIPE_WEBHOOK_SECRET   = "REPLACE_WITH_REAL_WEBHOOK_SECRET"
    ANYMAIL_MAILGUN_API_KEY = "REPLACE_WITH_REAL_MAILGUN_KEY"
    SENTRY_DSN              = ""
  })

  lifecycle { ignore_changes = [secret_string] }
}
