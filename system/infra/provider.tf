provider "aws" {
  region = var.region

  default_tags {
    tags = {
      "thesis:project" = "k8s-resource-recommendation-system"
      "thesis:iac"     = "terraform"
    }
  }
}
