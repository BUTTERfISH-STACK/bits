# modules/rds/main.tf

resource "aws_db_instance" "postgres" {
  identifier = "crm-postgres-${var.environment}"
  engine     = "postgres"
  engine_version = "15"
  instance_class = var.instance_class
  allocated_storage = 100
  username = var.username
  password = var.password
  skip_final_snapshot = true
  multi_az = true
}
