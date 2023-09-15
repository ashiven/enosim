variable "services" {
  description = "Service to be deployed on vulnboxes"
  default     = "CVExchange"
  type        = string
}

variable "checkers" {
  description = "Checkers to be deployed on checker"
  default     = "CVExchange"
  type        = string
}

variable "engine" {
  description = "Engine to be deployed on engine"
  default     = "CVExchange"
  type        = string
}

variable "vm_map" {
  type = map(object({
    name           = string
    size           = string
    admin_password = string
  }))
  default = {
    "vulnbox1" = {
      admin_password = "vulnbox1Password"
      name           = "vulnbox1"
      size           = "Standard_A1_v2"
      user_data      = base64encode("data/deploy_services.sh", local.data_inputs))
    }
    #    "vulnbox2" = {
    #      admin_password = "vulnbox2Password"
    #      name           = "vulnbox2"
    #      size           = "Standard_A1_v2"
    #    }
    #    "vulnbox3" = {
    #      admin_password = "vulnbox3Password"
    #      name           = "vulnbox3"
    #      size           = "Standard_A1_v2"
    #    }
    "enoengine" = {
      admin_password = "enoengine1Password"
      name           = "enoengine"
      size           = "Standard_A1_v2"
      user_data      = base64encode("data/deploy_engine.sh", local.data_inputs))
    }
    "checkers" = {
      admin_password = "checkers1Password"
      name           = "checkers"
      size           = "Standard_A1_v2"
      user_data      = base64encode("data/deploy_checkers.sh", local.data_inputs))
    }
  }
}
