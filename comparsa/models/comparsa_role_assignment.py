# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError

#Definimos el modelo de datos
class ComparsaRoleAssignment(models.Model):
  #Nombre y descripcion del modelo de datos
  _name = "comparsa.role.assignment"
  _description = "Asignación de cargo en la comparsa"
  _order = "date_start desc, id desc"

  # No permite borrar el miembro si tiene asignaciones de cargo asociadas
  member_id = fields.Many2one(
    "comparsa.member",
    required=True,
    index=True,
    ondelete="restrict",
  )

  # No permite borrar el cargo si tiene asignaciones de cargo asociadas
  role_id = fields.Many2one(
    "comparsa.role",
    required=True,
    index=True,
    ondelete="restrict",
  )

  date_start = fields.Date(required=True, index=True)
  date_end = fields.Date(required=True, index=True)

  # Restricción para validar que no haya solapamientos de cargos según fechas
  @api.constrains("date_start", "date_end")
  def _check_dates(self):
    for rec in self:
      if rec.date_start and rec.date_end and rec.date_start > rec.date_end:
        raise ValidationError("La fecha de inicio no puede ser posterior a la fecha de fin.")