# -*- coding: utf-8 -*-
from odoo import fields, models

#Definimos el modelo de datos
class ComparsaSquad(models.Model):
  #Nombre y descripcion del modelo de datos
  _name = "comparsa.squad"
  _description = "Escuadra"
  _order = "name"

  name = fields.Char(required=True, index=True)
  active = fields.Boolean(default=True)
