# modules/s3/main.tf

resource "aws_s3_bucket" "event_lake" {
  bucket = "crm-event-lake-${var.environment}-${random_id.bucket_suffix.hex}"
  acl    = "private"

  lifecycle_rule {
    id      = "archive"
    enabled = true

    transition {
      days          = 30
      storage_class = "GLACIER"
    }

    expiration {
      days = 365
    }
  }
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}
