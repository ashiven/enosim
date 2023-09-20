variable "services" {
  default = ["CVExchange", "bollwerk", "expenses"]
  type    = list(string)
}
variable "vm_map" {
  type = map(object({
    name           = string
    size           = string
    admin_password = string
    user_data      = string
  }))
  default = {
    "vulnbox" = {
      admin_password = "vulnboxPassword1!"
      name           = "vulnbox"
      size           = "Standard_A1_v2"
      user_data      = "templates/deploy_services.tftpl"
    }
    "engine" = {
      admin_password = "enginePassword1!"
      name           = "engine"
      size           = "Standard_A1_v2"
      user_data      = "templates/deploy_engine.tftpl"
    }
    "checker" = {
      admin_password = "checkerPassword1!"
      name           = "checker"
      size           = "Standard_A1_v2"
      user_data      = "templates/deploy_checkers.tftpl"
    }
  }
}
