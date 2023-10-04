output "vulnbox_public_ips" {
  value = ["${hcloud_server.vulnbox_vm.*.ipv4_address}"]
}
output "chccker_public_ips" {
  value = ["${hcloud_server.checker_vm.*.ipv4_address}"]
}
output "engine_public_ips" {
  value = ["${hcloud_server.engine_vm.*.ipv4_address}"]
}

