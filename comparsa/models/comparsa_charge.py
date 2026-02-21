# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError

#Definimos el modelo de datos
class ComparsaCharge(models.Model):
  #Nombre y descripcion del modelo de datos
  _name = "comparsa.charge"
  _description = "Charge"
  _order = "id desc"

  company_id = fields.Many2one(
    "res.company",
    required=True,
    default=lambda self: self.env.company,
    index=True,
  )

  # No permite borrar el miembro si tiene cargos asociados
  member_id = fields.Many2one(
    "comparsa.member",
    required=True,
    index=True,
    ondelete="restrict",
  )

  # No permite borrar el tipo de cargo si tiene cargos asociados
  charge_type_id = fields.Many2one(
    "comparsa.charge.type",
    required=True,
    index=True,
    ondelete="restrict",
  )

  # Redundancias aceptadas por eficiencia
  event_id = fields.Many2one(
    "comparsa.event",
    index=True,
    ondelete="set null",
  )

  # Redundancias aceptadas por eficiencia
  registration_id = fields.Many2one(
    "comparsa.event.registration",
    index=True,
    ondelete="set null",
  )

  periodicity = fields.Selection(
    selection=[("monthly", "Mensual"), ("yearly", "Anual"), ("single", "Único")],
    required=True,
    default="single",
    index=True,
  )

  period_key = fields.Char(index=True)  # monthly: YYYY-MM, yearly: YYYY, single: NULL

  amount_total = fields.Float(required=True)

  state = fields.Selection(
    selection=[("pending", "Pendiente"), ("partial", "Parcial"), ("paid", "Pagado"), ("cancelled", "Cancelado")],
    required=True,
    default="pending",
    index=True,
  )

  @api.constrains("member_id", "charge_type_id", "periodicity", "period_key", "state")
  def _check_no_duplicate_period(self):
    """Evita cargos duplicados para monthly/yearly excluyendo cancelados."""
    for rec in self:
      if rec.periodicity not in ("monthly", "yearly") or not rec.period_key:
        continue
      domain = [
        ("member_id", "=", rec.member_id.id),
        ("charge_type_id", "=", rec.charge_type_id.id),
        ("periodicity", "=", rec.periodicity),
        ("period_key", "=", rec.period_key),
        ("state", "!=", "cancelled"),
        ("id", "!=", rec.id),
      ]
      if self.search_count(domain):
        raise ValidationError("Ya existe un cargo activo para este miembro, tipo y periodo.")

  @api.constrains("amount_total")
  def _check_amount_total(self):
    for rec in self:
      if rec.amount_total <= 0:
        raise ValidationError("El importe del cargo debe ser mayor que 0.")

  @api.constrains("periodicity", "period_key")
  def _check_period_key(self):
    for rec in self:
      if rec.periodicity == "single" and rec.period_key:
        raise ValidationError("period_key debe estar vacío para los cargos únicos.")
      if rec.periodicity in ("monthly", "yearly") and not rec.period_key:
        raise ValidationError("period_key es obligatorio para los cargos mensuales/anuales.")

  # Para periodicity=single => period_key=NULL. PostgreSQL no garantiza unicidad con NULL = NULL, por eso se usa esta validación a nivel Python
  @api.constrains("member_id", "charge_type_id", "periodicity", "event_id", "registration_id", "state")
  def _check_no_duplicate_single(self):
    """UNIQUE SQL no cubre NULL=NULL; protegemos los cargos single por Python."""
    for rec in self:
      if rec.periodicity != "single":
        continue
      domain = [
        ("member_id", "=", rec.member_id.id),
        ("charge_type_id", "=", rec.charge_type_id.id),
        ("periodicity", "=", "single"),
        ("event_id", "=", rec.event_id.id if rec.event_id else False),
        ("registration_id", "=", rec.registration_id.id if rec.registration_id else False),
        ("state", "!=", "cancelled"),
        ("id", "!=", rec.id),
      ]
      if self.search_count(domain):
        raise ValidationError("Ya existe un cargo único para este miembro, tipo y evento.")

  @api.constrains("registration_id", "event_id")
  def _check_event_matches_registration(self):
    for rec in self:
      if rec.registration_id and rec.event_id and rec.registration_id.event_id != rec.event_id:
        raise ValidationError("event_id debe coincidir con registration_id.event_id cuando ambos están establecidos.")