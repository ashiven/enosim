output "private_ip_addresses" {
  value = [for _, nic in azurerm_network_interface.vm_nic : nic.ip_configuration[0].private_ip_address]
}
output "checker" {
  value = azurerm_public_ip.vm_pip["checker"]._ip_address
}
output "engine" {
  value = azurerm_public_ip.vm_pip["engine"]._ip_address
}
output "vulnbox1" {
  value = azurerm_public_ip.vm_pip["vulnbox1"]._ip_address
}
