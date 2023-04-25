data "aws_caller_identity" "this" {}

locals {
  account_id = data.aws_caller_identity.this.account_id

  eks_node_roles = [
    for role in var.workers_roles : {
      rolearn  = "arn:aws:iam::${local.account_id}:role/${role}"
      username = "system:node:{{EC2PrivateDNSName}}"
      groups   = ["system:nodes", "system:bootstrappers"]
    }
  ]
  aws_account_roles = [
    for role, groups in var.role_groups_mapping : {
      rolearn  = "arn:aws:iam::${local.account_id}:role/${role}"
      username = "${local.account_id}-${role}"
      groups   = groups
    }
  ]
  # Below sample roles, subject to adjust once RBAC will be finalized
  aws_staff_roles = concat(
    [
      {
        rolearn  = "arn:aws:iam::${local.account_id}:role/staff-eks-${var.cluster_name}-cluster-admin-role"
        username = "staff-eks-${var.cluster_name}-cluster-admin-role"
        groups   = ["system:masters"]
      },
      {
        rolearn  = "arn:aws:iam::${local.account_id}:role/staff-eks-${var.cluster_name}-cluster-view-role"
        username = "staff-eks-${var.cluster_name}-cluster-view-role"
        groups   = ["cluster-viewer"]
      }
    ]
  )
  aws_auth_data = distinct(
    concat(
      local.eks_node_roles,
      local.aws_account_roles,
      local.aws_staff_roles,
    )
  )
  # once yamlencode became stable switch to: yamlencode(local.aws_auth_data)
  aws_auth_data_raw = <<-EOT
    %{for role in local.aws_auth_data}
    - rolearn: ${role.rolearn}
      username: ${role.username}
      groups: %{for group in role.groups}
        - ${group} %{endfor}
    %{endfor}
    EOT
  # get rid of '\n' from raw - human friendly (yaml) values
  aws_auth_data_yaml = indent(0, local.aws_auth_data_raw)
}

resource "kubernetes_config_map" "this" {
  metadata {
    name      = "aws-auth"
    namespace = "kube-system"
  }
  data = {
    mapRoles = local.aws_auth_data_yaml
    mapUsers = "" # obsolete - should not be in use - overriding to empty value
  }
}

resource "kubernetes_cluster_role_binding" "cluster_viewer" {
  metadata {
    name = "cluster-viewer"
  }
  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = "view"
  }
  subject {
    kind = "Group"
    name = "cluster-viewer"
  }
}

resource "kubernetes_cluster_role_binding" "cluster_viewer_crd" {
  metadata {
    name = "cluster-viewer-crd"
  }
  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = "cluster-viewer-crd"
  }
  subject {
    kind = "Group"
    name = "cluster-viewer"
  }
}

resource "kubernetes_cluster_role_binding" "cluster_viewer_built_in" {
  metadata {
    name = "cluster-viewer-built-in"
  }
  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = "cluster-viewer-built-in"
  }
  subject {
    kind = "Group"
    name = "cluster-viewer"
  }
}

resource "kubernetes_cluster_role_binding" "cluster_viewer_built_in_ungrouped" {
  metadata {
    name = "cluster-viewer-built-in-ungrouped"
  }
  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = "cluster-viewer-built-in-ungrouped"
  }
  subject {
    kind = "Group"
    name = "cluster-viewer"
  }
}
resource "kubernetes_cluster_role" "cluster_viewer_crd" {
  metadata {
    name = "cluster-viewer-crd"
  }
  rule {
    api_groups = [
      # CRD
      "acme.cert-manager.io",
      "cert-manager.io",
      "authentication.istio.io",
      "config.istio.io",
      "coordination.k8s.io",
      "events.k8s.io",
      "networking.istio.io",
      "rbac.istio.io",
      "security.istio.io",
      "crd.k8s.amazonaws.com",
      "monitoring.coreos.com",
    ]
    resources = ["*"]
    verbs     = ["get", "list", "watch"]
  }
}

resource "kubernetes_cluster_role" "cluster_viewer_built_in" {
  metadata {
    name = "cluster-viewer-built-in"
  }
  rule {
    api_groups = [
      "admissionregistration.k8s.io",
      "apiextensions.k8s.io",
      "policy",
      "rbac.authorization.k8s.io",
      "scheduling.k8s.io",
      "storage.k8s.io",
    ]
    resources = ["*"]
    verbs     = ["get", "list", "watch"]
  }
}

resource "kubernetes_cluster_role" "cluster_viewer_built_in_ungrouped" {
  metadata {
    name = "cluster-viewer-built-in-ungrouped"
  }
  rule {
    api_groups = [""]
    resources = [
      "nodes",
      "persistentvolumes",
      "podtemplates",
    ]
    verbs = ["get", "list", "watch"]
  }
}