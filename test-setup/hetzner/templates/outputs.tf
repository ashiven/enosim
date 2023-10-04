output "public_ip_addresses" {
  value = {
    for vm in hcloud_server.vm :
    vm.name => vm.ipv4_address
  }
}