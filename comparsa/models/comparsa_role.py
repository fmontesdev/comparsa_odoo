# -*- coding: utf-8 -*-
from odoo import fields, models

class ComparsaRole(models.Model):
  #Nombre y descripcion del modelo de datos
  _name = "comparsa.role"
  _description = "Cargo de la comparsa"
  _order = "name"

  name = fields.Char(
    string="Nombre",
    required=True,
    index=True,
  )

  description = fields.Text(string="Descripción")

  # Duración del cargo en años. Se usa para calcular las fechas por defecto al crear una asignación.
  # Al crear una asignación: inicio = 1 sep año actual, fin = 31 ago (año actual + duración)
  duration_years = fields.Integer(
    string="Duración (años)",
    default=1,
  )

  active = fields.Boolean(string="Activo", default=True)
