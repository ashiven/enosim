output "private_ip_addresses" {
  value = [for _, nic in azurerm_network_interface.vm_nic : nic.ip_configuration[0].private_ip_address]
}
output "checker_ip" {
  value = azurerm_public_ip.vm_pip["checker"]._ip_address
}
output "engine_ip" {
  value = azurerm_public_ip.vm_pip["engine"]._ip_address
}
output "vulnbox1_ip" {
  value = azurerm_public_ip.vm_pip["vulnbox1"]._ip_address
}
