#Provider
terraform {
  required_providers {
    fortios = {
        source = "fortinetdev/fortios"
    }
  }
}
provider "fortios" {
  hostname = "fortigate-aws.enriquegabriel.click"
  token    = var.token
  insecure = "true"
}
#Variables to access the Fortigate
variable "token" {
  description = "token"
}
resource "fortios_system_setting_global" "Hostname" {
  hostname       = "myFortigate-Test"
}
