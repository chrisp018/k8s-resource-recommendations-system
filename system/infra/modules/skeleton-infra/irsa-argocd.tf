data "aws_caller_identity" "current" {}
data "aws_iam_policy_document" "argo_cd_assume_role" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    effect  = "Allow"

    condition {
      test     = "StringEquals"
      variable = "oidc.eks.ap-southeast-1.amazonaws.com/id/C9346C22EF38640E5C465F9128A3DCE0:sub"  #"${replace(var.eks-auth-oidc-url, "https://", "")}:sub"
      values   = ["system:serviceaccount:argo:argo-role"]
    }

    principals { 
      identifiers = ["arn:aws:iam::832438989008:oidc-provider/oidc.eks.ap-southeast-1.amazonaws.com/id/C9346C22EF38640E5C465F9128A3DCE0"] #[var.eks-auth-oidc-arn]
      type        = "Federated"
    }
  }
}

data "aws_iam_policy_document" "argo_cd_secret" {
  statement {
    sid = "SecretsManager"
    actions = [
      "secretsmanager:GetResourcePolicy",
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret",
      "secretsmanager:ListSecretVersionIds",
      "secretsmanager:ListSecrets"
    ]
    effect    = "Allow"
    resources = ["arn:aws:secretsmanager:${var.region}:${data.aws_caller_identity.current.account_id}:secret:devops-gh/argo/*"]
  }
}

resource "aws_iam_role" "argo_cd_secret" {
  assume_role_policy = data.aws_iam_policy_document.argo_cd_assume_role.json
  name               = "system-opspace-argo-cd-worker-role"
}

resource "aws_iam_role_policy" "argo_cd_secret" {
  name   = "system-opspace-argo-cd-manager-policy"
  role   = aws_iam_role.argo_cd_secret.name
  policy = data.aws_iam_policy_document.argo_cd_secret.json
}