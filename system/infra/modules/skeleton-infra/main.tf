module "infra-network" {
  source             = "../vpc"
  environment        = var.environment
  cidr_block         = var.vpc_cidr_block
  eks_cluster_name   = var.eks_cluster_name
  public_subnets     = var.public_subnets
  private_subnets    = var.private_subnets
  protected_subnets  = var.protected_subnets
  enable_nat_gateway = true
}

module "eks-cluster" {
  source = "../eks-cluster"

  vpc_id             = module.infra-network.vpc_id
  subnet_ids         = module.infra-network.private_subnets_ids
  kubernetes_version = "1.23"
  environment        = var.environment
  name               = var.eks_cluster_name
}

module "eks-node-group" {
  source = "../eks-nodegroup"

  subnet_ids         = module.infra-network.private_subnets_ids
  kubernetes_version = "1.23"
  environment        = var.environment
  name               = module.eks-cluster.this_eks_cluster_id
  node_groups        = var.node_groups
  region             = var.region
  eks_cluster_sg     = module.eks-cluster.this_eks_cluster_security_group_id
  eks_cluster_ca     = module.eks-cluster.this_eks_cluster_certificate_authority
  eks_cluster_api    = module.eks-cluster.this_eks_cluster_endpoint
}
