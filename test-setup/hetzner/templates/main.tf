resource "hcloud_ssh_key" "ssh_key" {
  name       = _placeholder_
  public_key = file(_placeholder_)
}

resource "hcloud_network" "vnet" {
  name     = "simulation-network"
  ip_range = "10.0.0.0/16"
}

resource "hcloud_network_subnet" "snet" {
  type         = "cloud"
  network_id   = hcloud_network.vnet.id
  network_zone = "eu-central"
  ip_range     = "10.0.2.0/24"
}

# TODO: 
# - create nodes for engine, checker, vulnboxes
# - make sure that packer images can be used to create vms
resource "hcloud_server" "vm" {
  name        = "server"
  server_type = "cx11"
  image       = "ubuntu-20.04"
  location    = "nbg1"

  ssh_keys = [
    hcloud_ssh_key.ssh_key.id
  ]

   # creating a server auto-assigns a private and public ip
  network {
    network_id = hcloud_network.vnet.id
  }

  depends_on = [
    hcloud_network_subnet.snet
  ]
}
