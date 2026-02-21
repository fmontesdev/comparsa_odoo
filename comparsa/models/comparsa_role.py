# -*- coding: utf-8 -*-
from odoo import api, fields, models
# from odoo.exceptions import ValidationError

#Definimos el modelo de datos
class ComparsaRole(models.Model):
  #Nombre y descripcion del modelo de datos
  _name = "comparsa.role"
  _description = "Cargo de la comparsa"
  _order = "name"

  name = fields.Char(required=True, index=True)
  description = fields.Text()
  active = fields.Boolean(default=True)
