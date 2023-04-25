variable "workers_roles" {
  type    = list(string)
  default = []
}

variable "role_groups_mapping" {
  type    = map(any)
  default = {}
}

variable "cluster_name" {
  type = string
}
