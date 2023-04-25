output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.this.id
}

output "vpc_cidr_block" {
  description = "The CIDR block of the VPC"
  value       = aws_vpc.this.cidr_block
}

output "private_subnets_ids" {
  description = "List of IDs of private subnets"
  value       = aws_subnet.private.*.id
}

output "public_subnets_ids" {
  description = "List of IDs of public subnets"
  value       = aws_subnet.public.*.id
}

output "azs" {
  description = "A list of availability zones specified as argument to this module"
  value       = local.azs
}

output "private_subnets_cidr_blocks" {
  description = "List of cidr_blocks of private subnets"
  value       = aws_subnet.private.*.cidr_block
}

output "private_route_table_ids" {
  description = "List of IDs of private subnets"
  value       = aws_route_table.private.*.id
}

output "public_route_table_ids" {
  description = "List of IDs of public subnets"
  value       = aws_route_table.public.*.id
}
