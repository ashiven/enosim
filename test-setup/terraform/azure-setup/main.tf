locals {
  data_inputs = {
    services = var.services
  }
}

resource "azurerm_resource_group" "rg" {
  name     = "simulation-setup"
  location = "West Europe"
}

resource "azurerm_virtual_network" "vnet" {
  name = "simulation-network"
  # the last 16 bits are for addresses and the ones before are the network id
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}

resource "azurerm_subnet" "snet" {
  name                 = "internal"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  # the last 8 bits are for addresses and the ones before are the network id
  address_prefixes = ["10.0.2.0/24"]
}

resource "azurerm_public_ip" "vm_pip" {
  for_each = var.vm_map

  name                = "${each.value.name}-ip"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  allocation_method   = "Static"
}

resource "azurerm_network_interface" "vm_nic" {
  for_each = var.vm_map

  name                = "${each.value.name}-nic"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  ip_configuration {
    name                          = "ipconfig"
    subnet_id                     = azurerm_subnet.snet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.vm_pip[each.key].id
  }

}

resource "azurerm_linux_virtual_machine" "vm" {
  for_each = var.vm_map

  name                = each.value.name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  size           = each.value.size
  admin_username = "groot"
  admin_password = each.value.admin_password
  user_data      = base64encode(templatefile(each.value.user_data, local.data_inputs))
  custom_data    = base64encode(file("./data/id_rsa"))

  network_interface_ids = [azurerm_network_interface.vm_nic[each.key].id]

  admin_ssh_key {
    username   = "groot"
    public_key = file("./data/id_rsa.pub")
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS"
    version   = "latest"
  }

}

output "private_ip_addresses" {
  description = "IP addresses of the virtual machines"
  value       = [for _, nic in azurerm_network_interface.vm_nic : nic.ip_configuration[0].private_ip_address]
}

output "vulnbox_ip" {
  value = azurerm_public_ip.vm_pip["vulnbox"].ip_address
}
output "checker_ip" {
  value = azurerm_public_ip.vm_pip["checker"].ip_address
}
output "engine_ip" {
  value = azurerm_public_ip.vm_pip["engine"].ip_address
}


# DEBUG
# output "template" {
#   value = templatefile("data/deploy_checkers.tftpl", local.data_inputs)
# }
