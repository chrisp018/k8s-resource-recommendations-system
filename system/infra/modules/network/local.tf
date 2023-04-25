data "aws_availability_zones" "available" {
  state = "available"
}
data "aws_caller_identity" "current" {}

locals {
  account_id = data.aws_caller_identity.current.account_id
  azs        = data.aws_availability_zones.available.names
  max_subnet_length = max(
    length(var.private_subnets),
    length(var.public_subnets),
  )
  prefix      = [var.environment]
  name-prefix = join("-", compact(local.prefix))
}
