variable "vulnbox_count" {
  type    = number
  default = _placeholder_
}

locals {
  dynamic_vm_map = merge(
    var.vm_map,
    {
      for vulnbox_id in range(1, var.vulnbox_count + 1) :
      "vulnbox${vulnbox_id}" => {
        name = "vulnbox${vulnbox_id}"
        size = "Standard_A1_v2"
      }
    }
  )
  vm_map = local.dynamic_vm_map
}


variable "vm_map" {
  type = map(object({
    name = string
    size = string
  }))
  default = {
    "engine" = {
      name = "engine"
      size = "Standard_A1_v2"
    }
    "checker" = {
      name = "checker"
      size = "Standard_A1_v2"
    }
  }
}
