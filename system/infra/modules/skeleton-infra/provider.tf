provider "kubernetes" {
  alias                  = "infra"
  host                   = module.eks-cluster.this_eks_cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks-cluster.this_eks_cluster_certificate_authority)
  token                  = data.aws_eks_cluster_auth.this.token
}
