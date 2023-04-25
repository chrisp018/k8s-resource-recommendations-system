variable "cidr_block" {
  type        = string
  description = "VPC cidr_block"
}

variable "environment" {
  type        = string
  description = "environment"
}

variable "eks_cluster_name" {
  type        = string
  description = "EKS cluster name"
}
variable "private_subnets" {
  type        = list(string)
  description = "A list of CIDR for private subnets inside the VPC"
}

variable "public_subnets" {
  type        = list(string)
  description = "A list of CIDR for public subnets inside the VPC"
}

variable "protected_subnets" {
  type        = list(string)
  description = "A list of CIDR for protected subnets inside the VPC"
}

variable "enable_nat_gateway" {
  type        = bool
  description = "Should be true if you want to provision NAT Gateways"
}
