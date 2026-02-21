# -*- coding: utf-8 -*-
from odoo import fields, models

class ComparsaSquad(models.Model):
  #Nombre y descripcion del modelo de datos
  _name = "comparsa.squad"
  _description = "Escuadra"
  _order = "name"

  name = fields.Char(
    string="Nombre",
    required=True,
    index=True,
  )

  active = fields.Boolean(string="Activo", default=True)
