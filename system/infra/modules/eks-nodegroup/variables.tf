variable "environment" {
  type = string
}

variable "name" {
  type = string
}

variable "region" {
  type = string
}

variable "kubernetes_version" {
  type    = string
  default = "1.22"
}

variable "subnet_ids" {
  type = list(string)
}

variable "node_groups" {
  type = any
  default = {
    on_demand = {
      disk_size         = 20
      instance_types    = ["t2.medium", "t3.medium", "t3a.medium"]
      capacity_type     = "SPOT"
      desired_capacity  = 1
      max_size          = 3
      min_size          = 1
      kubernetes_taints = []
    }
  }
}

variable "ami_type" {
  default = "AL2_x86_64"
  type    = string
}

variable "eks_cluster_sg" {
  type        = string
  description = "Security group attach to node group"
}

variable "eks_cluster_ca" {
  type        = string
  description = "Base64 encode of eks certificate authority"
}

variable "eks_cluster_api" {
  type        = string
  description = "The API URL of eks cluster"
}

variable "ebs_optimized" {
  description = "If true, the launched EC2 instance will be EBS-optimized"
  type        = bool
  default     = false
}

variable "image_id" {
  description = "The AMI from which to launch the instance. If not supplied, EKS will use its own default image"
  type        = string
  default     = ""
}

variable "block_device_mappings" {
  description = "Specify volumes to attach to the instance besides the volumes specified by the AMI"
  type        = any
  default = {
    xvda = {
      device_name = "/dev/xvda"
      ebs = {
        delete_on_termination = true
        volume_size           = 20
        volume_type           = "gp3"
      }
    }
  }
}
