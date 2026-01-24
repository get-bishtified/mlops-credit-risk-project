resource "aws_s3_bucket" "raw" {
  bucket = "${var.project}-raw-data"
}

resource "aws_s3_bucket" "models" {
  bucket = "${var.project}-models"
}
