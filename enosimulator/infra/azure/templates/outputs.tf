output "private_ip_addresses" {
  value = {
    for name, vm in azurerm_network_interface.vm_nic : name => vm.private_ip_address
  }
}
output "checker" {
  value = azurerm_public_ip.vm_pip["checker"].ip_address
}
output "engine" {
  value = azurerm_public_ip.vm_pip["engine"].ip_address
}
