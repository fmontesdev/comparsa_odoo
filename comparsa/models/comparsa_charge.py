# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ComparsaCharge(models.Model):
  #Nombre y descripcion del modelo de datos
  _name = "comparsa.charge"
  _description = "Cobro o cuota de la comparsa"
  _order = "id desc"

  company_id = fields.Many2one(
    comodel_name="res.company",
    string="Compañía",
    required=True,
    default=lambda self: self.env.company,
    index=True,
  )

  # No permite borrar el miembro si tiene cargos asociados
  member_id = fields.Many2one(
    comodel_name="comparsa.member",
    string="Miembro",
    required=True,
    index=True,
    ondelete="restrict",
  )

  # No permite borrar el tipo de cargo si tiene cargos asociados
  charge_type_id = fields.Many2one(
    comodel_name="comparsa.charge.type",
    string="Tipo de cobro",
    required=True,
    index=True,
    ondelete="restrict",
  )

  # Redundancias aceptadas por eficiencia
  event_id = fields.Many2one(
    comodel_name="comparsa.event",
    string="Acto",
    index=True,
    ondelete="set null",
  )

  # Redundancias aceptadas por eficiencia
  registration_id = fields.Many2one(
    comodel_name="comparsa.event.registration",
    string="Registro de asistencia",
    index=True,
    ondelete="set null",
  )

  periodicity = fields.Selection(
    selection=[("monthly", "Mensual"), ("yearly", "Anual"), ("single", "Único")],
    string="Periodicidad",
    required=True,
    default="single",
    index=True,
  )

  period_key = fields.Char(string="Clave de periodo", index=True)  # monthly: YYYY-MM, yearly: YYYY, single: NULL
  amount_total = fields.Float(string="Importe total", required=True)

  state = fields.Selection(
    selection=[
      ("pending", "Pendiente"),
      ("invoiced", "Facturado"),
      ("partial", "Parcial"),
      ("paid", "Pagado"),
      ("cancelled", "Cancelado"),
    ],
    string="Estado",
    required=True,
    default="pending",
    index=True,
  )

  # Enlace a la factura de Odoo generada para este cargo
  invoice_id = fields.Many2one(
    "account.move",
    string="Factura",
    readonly=True,
    ondelete="set null",
    copy=False,
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

  @api.constrains("state", "invoice_id")
  def _check_cancel_with_invoice(self):
    """Impide cancelar un cargo que ya tiene una factura activa en contabilidad."""
    for rec in self:
      if rec.state == "cancelled" and rec.invoice_id and rec.invoice_id.state != "cancel":
        raise ValidationError(
          "No se puede cancelar un cargo con una factura activa. "
          "Cancela primero la factura en contabilidad."
        )

  def action_create_invoice(self):
    """Genera una factura de cliente (account.move) para este cargo y la enlaza."""
    for rec in self:
      if rec.invoice_id:
        raise ValidationError("Este cargo ya tiene una factura asociada.")
      if rec.state == "cancelled":
        raise ValidationError("No se puede facturar un cargo cancelado.")
      if not rec.charge_type_id.account_id:
        raise ValidationError(
          f"El tipo de cargo '{rec.charge_type_id.name}' no tiene cuenta contable configurada."
        )

      partner = rec.member_id.partner_id
      invoice = self.env["account.move"].create({
        "move_type": "out_invoice",
        "partner_id": partner.id,
        "company_id": rec.company_id.id,
        "invoice_date": fields.Date.today(),
        "narration": f"Cargo: {rec.charge_type_id.name}"
                     + (f" — {rec.period_key}" if rec.period_key else ""),
        "invoice_line_ids": [(0, 0, {
          "name": rec.charge_type_id.name
                  + (f" ({rec.period_key})" if rec.period_key else ""),
          "quantity": 1,
          "price_unit": rec.amount_total,
          "account_id": rec.charge_type_id.account_id.id,
        })],
      })
      rec.invoice_id = invoice
      rec.state = "invoiced"

    # Abrir la factura recién creada (útil cuando se llama desde un botón)
    if len(self) == 1:
      return {
        "type": "ir.actions.act_window",
        "res_model": "account.move",
        "res_id": self.invoice_id.id,
        "view_mode": "form",
        "target": "current",
      }