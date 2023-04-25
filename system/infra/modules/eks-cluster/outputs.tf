output "this_eks_cluster_endpoint" {
  value = aws_eks_cluster.this.endpoint
}

output "this_eks_cluster_certificate_authority" {
  value     = aws_eks_cluster.this.certificate_authority[0].data
  sensitive = true
}

output "this_eks_cluster_id" {
  value = aws_eks_cluster.this.id
}

output "this_security_group_id" {
  value = aws_security_group.this.id
}

output "this_eks_cluster_security_group_id" {
  value = aws_eks_cluster.this.vpc_config[0].cluster_security_group_id
}

output "this_iam_openid_connect_provider_arn" {
  value = aws_iam_openid_connect_provider.this.arn
}

output "this_iam_openid_connect_provider_url" {
  value = aws_iam_openid_connect_provider.this.url
}