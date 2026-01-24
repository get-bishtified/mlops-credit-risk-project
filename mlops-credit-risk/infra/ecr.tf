resource "aws_ecr_repository" "train" {
  name = "credit-ml-train"
}

resource "aws_ecr_repository" "infer" {
  name = "credit-ml-infer"
}
