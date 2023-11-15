resource "azurerm_resource_group" "rg" {
  name     = "simulation-setup"
  location = "West Europe"
}

resource "azurerm_virtual_network" "vnet" {
  name                = "simulation-network"
  address_space       = ["10.1.0.0/16"]
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}

resource "azurerm_subnet" "snet" {
  for_each = local.vm_map

  name                 = "${each.value.name}-snet"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.1.${each.value.subnet_id}.0/24"]
}

resource "azurerm_public_ip" "vm_pip" {
  for_each = local.vm_map

  name                = "${each.value.name}-ip"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  allocation_method   = "Static"
}

resource "azurerm_network_interface" "vm_nic" {
  for_each = local.vm_map

  name                = "${each.value.name}-nic"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  ip_configuration {
    name                          = "ipconfig"
    subnet_id                     = azurerm_subnet.snet[each.key].id
    private_ip_address_allocation = "Static"
    private_ip_address            = "10.1.${each.value.subnet_id}.4"
    public_ip_address_id          = azurerm_public_ip.vm_pip[each.key].id
  }
}

resource "azurerm_linux_virtual_machine" "vm" {
  for_each = local.vm_map

  name                = each.value.name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  size           = each.value.size
  admin_username = "groot"

  network_interface_ids = [azurerm_network_interface.vm_nic[each.key].id]

  admin_ssh_key {
    username   = "groot"
    public_key = file(_placeholder_)
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
