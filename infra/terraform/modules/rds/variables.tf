variable "app_name" { type = string }
variable "environment" { type = string }
variable "db_instance_class" { type = string; default = "db.t3.micro" }
variable "vpc_id" { type = string }
variable "private_subnet_ids" { type = list(string) }
variable "web_sg_id" { type = string }
variable "db_password" { type = string; sensitive = true; default = "" }
