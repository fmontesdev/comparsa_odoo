# -*- coding: utf-8 -*-
from odoo import api, fields, models

#Definimos el modelo de datos
class ComparsaChargeType(models.Model):
  #Nombre y descripcion del modelo de datos
  _name = "comparsa.charge.type"
  _description = "Charge Type"
  _order = "name"

  name = fields.Char(required=True)
  code = fields.Char(required=True, index=True)
  active = fields.Boolean(default=True)

  _uniq_charge_type_code_company = models.Constraint('UNIQUE(code)', 'El cobro debe tener un código único')
