output "vulnbox_public_ip_addresses" {
  value = {
    for server in hcloud_server.vulnbox_vm :
    server.name => server.ipv4_address
  }
}
output "checker_public_ip_addresses" {
  value = {
    for server in hcloud_server.checker_vm :
    server.name => server.ipv4_address
  }
}
output "engine_public_ip_address" {
  value = {
    for server in hcloud_server.engine_vm :
    server.name => server.ipv4_address
  }
}
