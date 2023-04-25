variable "environment" {
  type = string
}

variable "name" {
  type = string
}

variable "kubernetes_version" {
  type    = string
  default = "1.21"
}

variable "subnet_ids" {
  type = list(string)
}

variable "thumbprint_list" {
  type    = list(string)
  default = ["9e99a48a9960b14926bb7f3b02e22da2b0ab7280"]
}

variable "vpc_id" {
  type = string
}

variable "cluster_encryption_key" {
  type    = list(any)
  default = []
}

variable "eks_cluster_name" {
  type    = string
  default = "app"
}