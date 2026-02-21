# -*- coding: utf-8 -*-
from odoo import api, fields, models

#Definimos el modelo de datos
class ComparsaEventSubtype(models.Model):
  #Nombre y descripcion del modelo de datos
  _name = "comparsa.event.subtype"
  _description = "Subtipo de evento de la comparsa"
  _order = "type, name"

  name = fields.Char(required=True, index=True)
  type = fields.Selection(
    selection=[("festive", "Festivo"), ("meal", "Comida"), ("internal", "Interno")],
    required=True,
    index=True,
  )
  active = fields.Boolean(default=True)

  # Restricciones SQL
  _uniq_subtype_company_type_name = models.Constraint('UNIQUE(type, name)', 'El subtipo de evento debe ser único por tipo')