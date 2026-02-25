# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class MemberRegimeType(models.Model):
  #Nombre y descripcion del modelo de datos
  _name = "comparsa.member.regime.type"
  _description = "Regimen del comparsista"
  _order = "name"

  name = fields.Char(
    string="Nombre",
    required=True,
    index=True,
  )

  monthly_amount = fields.Float(
    string="Cuota mensual",
    required=True,
    default=0.0
  )

  yearly_amount = fields.Float(
    string="Cuota anual",
    required=True,
    default=0.0
  )

  allow_festive_by_default = fields.Boolean(
    string="Permitir 'Actos Festivos' por defecto",
    default=False
  )
  allow_meal_by_default = fields.Boolean(
    string="Permitir 'Comidas' por defecto",
    default=False
  )
  allow_internal_by_default = fields.Boolean(
    string="Permitir 'Actos Internos' por defecto",
    default=False
  )

  active = fields.Boolean(string="Activo", default=True)

  # Many2many explícita entre régimen y evento (excepciones permitidas)
  allowed_event_ids = fields.Many2many(
    comodel_name="comparsa.event",
    relation="comparsa_regime_event_rel",
    column1="regime_type_id",
    column2="event_id",
    string="Eventos permitidos (excepciones)",
  )

  # Restricciones SQL
  _uniq_regime_name = models.Constraint('UNIQUE(name)', 'El nombre del régimen del comparsista debe ser único')

  # Restricción para validar que los montos no sean negativos
  @api.constrains("monthly_amount", "yearly_amount")
  def _check_amounts(self):
    for rec in self:
      if rec.monthly_amount < 0 or rec.yearly_amount < 0:
        raise ValidationError("Los montos no pueden ser negativos")
