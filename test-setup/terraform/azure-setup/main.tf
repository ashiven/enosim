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

  network_interface_ids = [azurerm_network_interface.vm_nic[each.key].id]

  admin_ssh_key {
    username   = "groot"
    public_key = file("./data/test_key.pub")
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

  #TODO: change this at some point lol
  custom_data = <<-EOF
    #!/bin/bash
    echo "BEGIN OPENSSH PRIVATE KEY-----
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
-----END OPENSSH PRIVATE KEY-----" > /home/groot/.ssh/test_key
  chmod 600 /home/groot/.ssh/test_key
  EOF
}

# DEBUG
#output "template" {
#  value = templatefile("data/deploy_checkers.tftpl", local.data_inputs)
#}
