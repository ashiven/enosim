resource "hcloud_ssh_key" "ssh_key" {
  name       = _placeholder_
  public_key = file(_placeholder_)
}

resource "hcloud_network" "vnet" {
  name     = "simulation-network"
  ip_range = "10.1.0.0/16"
}


############# Subnets #############
resource "hcloud_network_subnet" "engine_snet" {
  type         = "cloud"
  network_id   = hcloud_network.vnet.id
  network_zone = "eu-central"
  ip_range     = "10.1.20.0/24"
}
resource "hcloud_network_subnet" "checker_snet" {
  type         = "cloud"
  network_id   = hcloud_network.vnet.id
  network_zone = "eu-central"
  ip_range     = "10.1.21.0/24"
}
# address of team: 10.1.<team_id>.0
# address of team vulnbox: 10.1.<team_id>.1
resource "hcloud_network_subnet" "vulnbox1_snet" {
  type         = "cloud"
  network_id   = hcloud_network.vnet.id
  network_zone = "eu-central"
  ip_range     = "10.1.1.0/24"
}
resource "hcloud_network_subnet" "vulnbox2_snet" {
  type         = "cloud"
  network_id   = hcloud_network.vnet.id
  network_zone = "eu-central"
  ip_range     = "10.1.2.0/24"
}


############# VMs #############
resource "hcloud_server" "vm" {
  name        = "engine"
  server_type = "cx11"
  image       = "ubuntu-20.04"
  location    = "nbg1"

  ssh_keys = [
    hcloud_ssh_key.ssh_key.id
  ]

  # creating a server auto-assigns a private and public ip
  network {
    network_id = hcloud_network.vnet.id
    ip         = "10.1.20.1"
  }

  depends_on = [
    hcloud_network_subnet.engine_snet
  ]
}
resource "hcloud_server" "vm" {
  name        = "checker"
  server_type = "cx11"
  image       = "ubuntu-20.04"
  location    = "nbg1"

  ssh_keys = [
    hcloud_ssh_key.ssh_key.id
  ]

  network {
    network_id = hcloud_network.vnet.id
    ip         = "10.1.21.1"
  }

  depends_on = [
    hcloud_network_subnet.checker_snet
  ]
}
resource "hcloud_server" "vm" {
  name        = "vulnbox1"
  server_type = "cx11"
  image       = "ubuntu-20.04"
  location    = "nbg1"

  ssh_keys = [
    hcloud_ssh_key.ssh_key.id
  ]

  network {
    network_id = hcloud_network.vnet.id
    ip         = "10.1.1.1"
  }

  depends_on = [
    hcloud_network_subnet.vulnbox1_snet
  ]
}
resource "hcloud_server" "vm" {
  name        = "vulnbox2"
  server_type = "cx11"
  image       = "ubuntu-20.04"
  location    = "nbg1"

  ssh_keys = [
    hcloud_ssh_key.ssh_key.id
  ]

  network {
    network_id = hcloud_network.vnet.id
    ip         = "10.1.2.1"
  }

  depends_on = [
    hcloud_network_subnet.vulnbox2_snet
  ]
}

