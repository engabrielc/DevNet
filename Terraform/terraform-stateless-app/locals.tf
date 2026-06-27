locals {
  # Consistent prefix for resource names, e.g. "stateless-app-dev".
  name_prefix = "${var.project_name}-${var.environment}"

  # Tags applied to every resource via the provider default_tags block.
  common_tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
    },
    var.tags,
  )
}
