resource "aws_network_acl" "all" {
  vpc_id     = aws_vpc.this.id
  subnet_ids = concat(aws_subnet.public.*.id, aws_subnet.private.*.id)
  tags = {
    "Name" = "${var.environment}-all-nacl"
  }
}

resource "aws_network_acl_rule" "inbound" {
  network_acl_id = aws_network_acl.all.id
  rule_number    = 100
  protocol       = "all"
  rule_action    = "allow"
  egress         = false
  cidr_block     = "0.0.0.0/0"
  from_port      = 0
  to_port        = 65535
}

resource "aws_network_acl_rule" "outbound" {
  network_acl_id = aws_network_acl.all.id
  rule_number    = 100
  protocol       = "all"
  rule_action    = "allow"
  egress         = true
  cidr_block     = "0.0.0.0/0"
  from_port      = 0
  to_port        = 65535
}
