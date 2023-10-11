#Provider
terraform {
  required_providers {
    fortios = {
        source = "fortinetdev/fortios"
    }
  }
}
#Connecting to the Fortigate Firewall
provider "fortios" {
  hostname = "example.com or x.x.x.x"
  token    = var.token
  insecure = "true"
  vdom     = "root" # Make sure to select the vdom with the VPNs and traffic policies.
}
#Inserting the API-Rest token
variable "token" {
  description = "token"
}
#VPN Phase 1
resource "fortios_vpnipsec_phase1interface" "VPN_NAME" {

    name                 = "VPN_NAME" #Should not exceed 15 characters.
    remote_gw            = "x.x.x.x" #Public IP of the remote end.
    interface            = "port12" # The interface with the public IP (WAN interface).
    psksecret            = "123456789" # Use a stronger PSK. 
    proposal             = "aes256-sha256"
    dhgrp                = "14"
    keylife              = 28800
    net_device           = "disable"
    ike_version          = "2"
    mode                 = "main"
    idle_timeout         = "disable"

}
#VPN phase 2
resource "fortios_vpnipsec_phase2interface" "VPN_NAME" {
    name                 = "VPN_NAME"
    phase1name           = fortios_vpnipsec_phase1interface.VPN_NAME.name
    proposal             = "aes256-sha256"
    dhgrp                = "14"
    src_subnet           = "0.0.0.0 0.0.0.0"
    dst_subnet           = "0.0.0.0 0.0.0.0"
    src_port             = 0 #Zero means all.
    dst_port             = 0 #Zero means all.
    protocol             = 0 #Zero means all.
    keylife_type         = "seconds"
    keylifeseconds       = 3600
    auto_negotiate       = "enable"
    pfs                  = "enable"
}
#Firewall policy to allow traffic from the IPSec tunnel to the LAN
resource "fortios_firewall_policy" "fw-policy" {
  name               = "SiteA-to-SiteB"
  nat                = "disable"
  action             = "accept"
  status             = "enable"
   service {
    name = "ALL"
  }
  srcintf {
    name = fortios_vpnipsec_phase2interface.VPN_NAME.name
   }
  dstintf {
    name = "port11" # The interface with the local IP (LAN interface).
  }
 }

