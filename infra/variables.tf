variable "project" {
  type    = string
  default = "finbank"
}
variable "env" {
  type        = string
  description = "Entorno: dev o prod"
}
variable "location" {
  type    = string
  default = "eastus2"
}
variable "alert_email" {
  type        = string
  description = "Correo que recibe las alertas"
}
variable "my_ip" {
  type        = string
  description = "Tu IP pública, para el firewall de PostgreSQL"
}
variable "pg_sku" {
  type    = string
  default = "B_Standard_B1ms"
}
variable "engineers_group_id" { type = string }
variable "analysts_group_id" { type = string }
variable "admins_group_id" { type = string }

variable "pg_location" {
  type        = string
  default     = "centralus"
  description = "Región de PostgreSQL (puede diferir del resto si la región principal está restringida)"
}