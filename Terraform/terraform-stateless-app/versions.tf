terraform {
  # Pin a minimum Terraform version. Features used here (optional object
  # attributes, moved blocks, sensitive validation) require >= 1.5.
  required_version = ">= 1.5.0, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.60"
    }
  }

  # ---------------------------------------------------------------------------
  # Remote state backend (recommended for any shared / production use).
  #
  # Local state is fine for a quick personal try-out, but for collaboration you
  # want remote state with locking. Uncomment and fill in, then run
  # `terraform init -migrate-state`. With AWS provider >= 5.x you can use S3
  # native locking (use_lockfile) instead of a separate DynamoDB table.
  # ---------------------------------------------------------------------------
  # backend "s3" {
  #   bucket       = "my-tfstate-bucket"
  #   key          = "stateless-app/terraform.tfstate"
  #   region       = "us-east-1"
  #   encrypt      = true
  #   use_lockfile = true
  # }
}
