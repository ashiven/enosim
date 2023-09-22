variable "vulnbox_count" {
  type    = number
  default = 1
}

variable "size" {
  description = "VM size for vulnboxes"
  type        = string
  default     = "Standard_A1_v2"
}

locals {
  vm_map = {
    "engine" = {
      name = "engine"
      size = var.size
    }
    "checker" = {
      name = "checker"
      size = var.size
    }
    dynamic_vm_map = merge(
      local.vm_map,
      {
        for vulnbox_id in range(1, var.vulnbox_count + 1) :
        "vulnbox${vulnbox_id}" => {
          name      = "vulnbox${vulnbox_id}"
          size      = var.size
          user_data = var.user_data_template
        }
      }
    )
  }
}


variable "vm_map" {
  type = map(object({
    name = string
    size = string
  }))
  default = local.vm_map
}
