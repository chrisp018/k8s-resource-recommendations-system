resource "aws_eip" "nat" {
  count = var.enable_nat_gateway ? 1 : 0
  vpc   = true
}

resource "aws_nat_gateway" "this" {
  count = var.enable_nat_gateway ? 1 : 0

  allocation_id = aws_eip.nat[0].id

  subnet_id = element(
    aws_subnet.public.*.id, 0
  )

  tags = {
    "Name" = "${var.environment}-nat-gateway"
  }

  depends_on = [aws_internet_gateway.igw]
}