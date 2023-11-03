resource "virtualbox_vm" "vulnbox1" {
  name   = "vulnbox1"
  image  = "https://app.vagrantup.com/ubuntu/boxes/bionic64/versions/20180903.0.0/providers/virtualbox.box"
  cpus   = 2
  memory = "512 mib"
  #user_data = file("${path.module}/services")

  network_adapter {
    type           = "bridged"
    host_interface = "Intel(R) Ethernet Connection (2) I219-V"
  }
}

resource "virtualbox_vm" "vulnbox2" {
  name   = "vulnbox2"
  image  = "https://app.vagrantup.com/ubuntu/boxes/bionic64/versions/20180903.0.0/providers/virtualbox.box"
  cpus   = 2
  memory = "512 mib"
  #user_data = file("${path.module}/services")

  network_adapter {
    type           = "bridged"
    host_interface = "Intel(R) Ethernet Connection (2) I219-V"
  }
}

resource "virtualbox_vm" "checkers" {
  name   = "checkers"
  image  = "https://app.vagrantup.com/ubuntu/boxes/bionic64/versions/20180903.0.0/providers/virtualbox.box"
  cpus   = 1
  memory = "512 mib"
  #user_data = file("${path.module}/user_data")

  network_adapter {
    type           = "bridged"
    host_interface = "Intel(R) Ethernet Connection (2) I219-V"
  }
}

resource "virtualbox_vm" "enoengine" {
  name   = "enoengine"
  image  = "https://app.vagrantup.com/ubuntu/boxes/bionic64/versions/20180903.0.0/providers/virtualbox.box"
  cpus   = 1
  memory = "512 mib"
  #user_data = file("${path.module}/user_data")

  network_adapter {
    type           = "bridged"
    host_interface = "Intel(R) Ethernet Connection (2) I219-V"
  }
}
