# -*- coding: utf-8 -*-
from odoo import fields, models

class ComparsaEventSubtype(models.Model):
  #Nombre y descripcion del modelo de datos
  _name = "comparsa.event.subtype"
  _description = "Subtipo de evento de la comparsa"
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
  _uniq_subtype_type_name = models.Constraint('UNIQUE(type, name)', 'El subtipo de evento debe ser único por tipo')