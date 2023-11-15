resource "hcloud_ssh_key" "ssh_key" {
  name       = "simulation-ssh-key"
  public_key = file(_placeholder_)
}

resource "hcloud_network" "vnet" {
  name     = "simulation-network"
  ip_range = "10.1.0.0/16"
}

############# Subnets #############

############# VMs #############
