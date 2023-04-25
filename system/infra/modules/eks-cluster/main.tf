resource "aws_eks_cluster" "this" {
  name     = var.eks_cluster_name
  role_arn = aws_iam_role.this.arn
  version  = var.kubernetes_version

  vpc_config {
    subnet_ids              = var.subnet_ids
    endpoint_private_access = true
    endpoint_public_access  = true

    security_group_ids = [
      aws_security_group.this.id
    ]
  }

  dynamic "encryption_config" {
    for_each = var.cluster_encryption_key

    content {
      provider {
        key_arn = element(var.cluster_encryption_key, 0)
      }
      resources = ["secrets"]
    }
  }
}

resource "aws_iam_openid_connect_provider" "this" {
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = var.thumbprint_list
  url             = aws_eks_cluster.this.identity.0.oidc.0.issuer
}

resource "aws_security_group" "this" {
  name        = lower("${var.environment}-eks-cluster-sg")
  vpc_id      = var.vpc_id
  description = "EKS security group"
}

resource "aws_security_group_rule" "egress_all" {
  type              = "egress"
  security_group_id = aws_security_group.this.id
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  description       = "Outgoing traffic from EKS to the world"
}

resource "aws_security_group_rule" "ingress_443" {
  type              = "ingress"
  security_group_id = aws_security_group.this.id
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  description       = "Incoming traffic to API server port"
}

data "aws_iam_policy_document" "this" {
  statement {
    sid = "EKSAssumeRole"

    actions = [
      "sts:AssumeRole",
    ]

    principals {
      identifiers = [
        "eks.amazonaws.com"
      ]

      type = "Service"
    }
  }
}

resource "aws_iam_role" "this" {
  name                  = lower("system-eks-${var.eks_cluster_name}-role")
  assume_role_policy    = data.aws_iam_policy_document.this.json
  force_detach_policies = true
}

resource "aws_iam_role_policy_attachment" "cluster_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.this.name
}

resource "aws_iam_role_policy_attachment" "service_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSServicePolicy"
  role       = aws_iam_role.this.name
}
