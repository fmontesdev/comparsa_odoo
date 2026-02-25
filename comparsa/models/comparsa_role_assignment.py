# -*- coding: utf-8 -*-
from datetime import date
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ComparsaRoleAssignment(models.Model):
  #Nombre y descripcion del modelo de datos
  _name = "comparsa.role.assignment"
  _description = "Asignación de cargo en la comparsa"
  _order = "date_start desc, id desc"

  # No permite borrar el miembro si tiene asignaciones de cargo asociadas
  member_id = fields.Many2one(
    comodel_name="comparsa.member",
    string="Miembro",
    required=True,
    index=True,
    ondelete="restrict",
  )

  # No permite borrar el cargo si tiene asignaciones de cargo asociadas
  role_id = fields.Many2one(
    comodel_name="comparsa.role",
    string="Cargo",
    required=True,
    index=True,
    ondelete="restrict",
  )

  date_start = fields.Date(
    string="Fecha de inicio",
    required=True,
    index=True
  )
  
  date_end = fields.Date(
    string="Fecha de fin",
    required=True,
    index=True
  )

  # Campo calculado para mostrar el nombre del cargo y del miembro
  def _compute_display_name(self):
    for rec in self:
      role = rec.role_id.display_name or "?"
      member = rec.member_id.display_name or "?"
      rec.display_name = f"{role} – {member}"

  _uniq_role_assignment = models.Constraint(
    'UNIQUE(role_id, date_start, date_end)',
    'Ya existe una asignación para este cargo con las mismas fechas de inicio y fin',
  )

  # OnChange para calcular fechas a partir de la duración del cargo y el año en curso
  # inicio = 1 sep año actual, fin = 31 ago (año actual + duración)
  @api.onchange("role_id")
  def _onchange_role_id(self):
    if self.role_id and self.role_id.duration_years:
      year = fields.Date.today().year
      self.date_start = date(year, 9, 1)
      self.date_end = date(year + self.role_id.duration_years, 8, 31)

  # Restricción para validar que no haya solapamientos de cargos según fechas
  @api.constrains("date_start", "date_end")
  def _check_dates(self):
    for rec in self:
      if rec.date_start and rec.date_end and rec.date_start > rec.date_end:
        raise ValidationError("La fecha de inicio no puede ser posterior a la fecha de fin")

  # Restricción para validar que no haya más de una asignación activa para el mismo cargo (date_end >= hoy)
  @api.constrains("role_id", "date_start", "date_end")
  def _check_role_not_active(self):
    today = fields.Date.today()
    for rec in self:
      domain = [
        ("role_id", "=", rec.role_id.id),
        ("date_end", ">=", today),
        ("id", "!=", rec.id),
      ]
      if self.search_count(domain):
        raise ValidationError(
          f"El cargo '{rec.role_id.name}' ya tiene una asignación vigente. "
          "Espera a que finalice antes de crear una nueva, o modifica la asignación existente."
        )