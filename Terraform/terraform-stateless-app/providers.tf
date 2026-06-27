provider "aws" {
  region = var.region

  # default_tags applies these tags to every taggable resource managed by this
  # provider, so individual resources only need to add what's unique to them.
  default_tags {
    tags = local.common_tags
  }
}
