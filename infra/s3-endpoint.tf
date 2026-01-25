resource "aws_vpc_endpoint" "s3" {
  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.ap-south-1.s3"

  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_vpc.main.main_route_table_id]
}
