resource "aws_ecr_repository" "train" {
  name = "${var.project}-train"
}

resource "aws_ecr_repository" "infer" {
  name = "${var.project}-infer"
}

resource "aws_ecr_repository" "base" {
  name = "${var.project}-base"
}
