output "vulnbox_public_ips" {
  value = {
    for server in hcloud_server.vulnbox_vm :
    server.name => server.ipv4_address
  }
}
output "checker" {
  value = hcloud_server.checker_vm.ipv4_address
}
output "engine" {
  value = hcloud_server.engine_vm.ipv4_address
}
