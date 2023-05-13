variable "environment" {
  description = "Environment"
  type        = string
}

variable "region" {
  description = "Region"
  type        = string
}

variable "vpc_cidr_block" {
  type        = string
  description = "VPC's CIDR block"
}

variable "public_subnets" {
  type        = list(string)
  description = "List of CIDR ranges for public subnets"
}

variable "private_subnets" {
  type        = list(string)
  description = "List of CIDR ranges for private subnets"
}

variable "eks_nodegroup_subnets" {
  type        = list(string)
  description = "List of CIDR ranges for private subnets dedicated for EKS nodegroups"
  default     = []
}

variable "protected_subnets" {
  type        = list(string)
  description = "List of CIDR ranges for protected subnets"
}

variable "eks_cluster_name" {
  type    = string
  default = "app"
}

variable "node_groups" {
  type = any
  default = {
    on_demand = {
      disk_size        = 20
      instance_types   = ["m5.2xlarge", "m5a.2xlarge"]
      capacity_type    = "SPOT"
      desired_capacity = 1
      max_size         = 3
      min_size         = 1
    }
    # system = {
    #   disk_size        = 20
    #   instance_types   = ["m5.2xlarge", "m5a.2xlarge"]
    #   capacity_type    = "SPOT"
    #   desired_capacity = 1
    #   max_size         = 3
    #   min_size         = 1
    # }
  }
}


variable "stage" {
  type    = string
  default = "thesis"
}

variable "public_domain" {
  type    = string
  default = "clphan.com"
}

variable "use_custom_launch_template" {
  description = "Determines whether to create a launch template or not. If set to `false`, EKS will use its own default launch template"
  type        = bool
  default     = false
}

variable "metadata_options" {
  description = "Customize the metadata options for the instance"
  type        = map(any)
  default     = {}
}
