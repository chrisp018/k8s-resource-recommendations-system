module "skeleton" {
  source = "./modules/skeleton-infra"

  environment       = var.environment
  region            = var.region
  vpc_cidr_block    = "172.21.48.0/21"
  public_subnets    = ["172.21.48.0/26", "172.21.48.64/26", "172.21.48.128/26"]
  protected_subnets = ["172.21.48.192/26", "172.21.49.0/26", "172.21.49.64/26"]
  private_subnets   = ["172.21.50.0/23", "172.21.52.0/23", "172.21.54.0/23"]
}
