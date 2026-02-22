# -*- coding: utf-8 -*-
from odoo import fields, models

class ComparsaEventCategory(models.Model):
  #Nombre y descripcion del modelo de datos
  _name = "comparsa.event.category"
  _description = "Categoría de acto de la comparsa"
  _order = "type, name"

  name = fields.Char(
    string="Nombre",
    required=True,
    index=True
  )

  type = fields.Selection(
    selection=[("festive", "Festivo"), ("meal", "Comida"), ("internal", "Interno")],
    string="Tipo de acto",
    required=True,
    index=True,
  )
  
  active = fields.Boolean(string="Activo", default=True)

  # Restricciones SQL
  _sql_constraints = [
    ('uniq_type_name', 'UNIQUE(type, name)', 'El evento debe ser único por tipo')
  ]