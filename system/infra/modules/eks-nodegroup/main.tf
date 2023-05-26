data "aws_caller_identity" "current" {}

locals {
  account_id = data.aws_caller_identity.current.account_id
}

resource "aws_eks_node_group" "this" {
  for_each = var.node_groups

  cluster_name    = var.name
  node_group_name = lower("${var.name}-${each.key}")
  node_role_arn   = aws_iam_role.this.arn
  subnet_ids      = var.subnet_ids
  ami_type        = var.ami_type
  # disk_size       = each.value.disk_size
  instance_types = each.value.instance_types
  capacity_type  = each.value.capacity_type
  version        = var.kubernetes_version
  dynamic "taint" {
    for_each = each.value.kubernetes_taints

    content {
      key    = taint.value["key"]
      value  = taint.value["value"]
      effect = taint.value["effect"]
    }
  }
  dynamic "launch_template" {
    for_each = [each.key]
    content {
      id      = aws_launch_template.this[each.key].id
      version = coalesce(try(aws_launch_template.this[each.key].default_version, "$Default"))
    }
  }
  scaling_config {
    desired_size = each.value.desired_capacity
    max_size     = each.value.max_size
    min_size     = each.value.min_size
  }

  labels = {
    "Name" = lower("${var.name}-${each.key}")
  }

  tags = {
    Environment                             = lower(var.environment)
    Name                                    = lower("${var.name}-${each.key}")
    "k8s.io/cluster-autoscaler/enabled"     = 1
    "k8s.io/cluster-autoscaler/${var.name}" = 1
  }

  lifecycle {
    # This will be handled by cluster-autoscaler
    ignore_changes = [scaling_config.0.desired_size]
  }
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    sid = "EKSWorkerAssumeRole"

    actions = [
      "sts:AssumeRole",
    ]

    principals {
      type = "Service"
      identifiers = [
        "ec2.amazonaws.com",
      ]
    }
  }
}

resource "aws_iam_role" "this" {
  # Following pattern system-(application)-(functionality)-role
  name                  = lower("system-eks-${var.name}-worker-role")
  assume_role_policy    = data.aws_iam_policy_document.assume_role.json
  force_detach_policies = true
}

resource "aws_iam_instance_profile" "this" {
  name = lower("system-eks-${var.name}-worker-instance-profile")
  role = aws_iam_role.this.name
}

resource "aws_iam_role_policy_attachment" "AmazonEKSWorkerNodePolicy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.this.name
}

resource "aws_iam_role_policy_attachment" "AmazonEKS_CNI_Policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.this.name
}

resource "aws_iam_role_policy_attachment" "AmazonEC2ContainerRegistryReadOnly" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.this.name
}

resource "aws_iam_role_policy_attachment" "AmazonCloudwatchAgentPolicy" {
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
  role       = aws_iam_role.this.name
}

resource "aws_iam_role_policy_attachment" "AmazonSSMManagedInstanceCore" {
  role       = aws_iam_role.this.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy_attachment" "AmazonSSMFullAccess" {
  role       = aws_iam_role.this.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMFullAccess"
}

resource "aws_iam_role_policy_attachment" "AmazonS3FullAccess" {
  role       = aws_iam_role.this.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role_policy_attachment" "Route53" {
  role       = aws_iam_role.this.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonRoute53FullAccess"
}
