# -*- coding: utf-8 -*-
from datetime import date as Date
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
    related="charge_type_id.periodicity",
    string="Periodicidad",
    store=True,
  )

  period_key = fields.Char(string="Clave de periodo", index=True)  # monthly: YYYY-MM, yearly: YYYY, single: NULL

  # Líneas de desglose del cobro (concepto, cantidad, precio unitario)
  line_ids = fields.One2many(
    comodel_name="comparsa.charge.line",
    inverse_name="charge_id",
    string="Líneas",
  )

  # Importe total calculado a partir de las líneas
  amount_total = fields.Float(
    string="Importe total",
    compute="_compute_amount_total",
    store=True,
  )

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

  # Divisa heredada de la compañía para facilitar el acceso en las líneas y la factura
  currency_id = fields.Many2one(
    related="company_id.currency_id",
    string="Moneda",
    readonly=True,
  )

  # Enlace a la factura de Odoo generada para este cargo
  invoice_id = fields.Many2one(
    "account.move",
    string="Factura",
    readonly=True,
    ondelete="set null",
    copy=False,
  )

  # Cálculo del nombre para mostrar del cargo, combinando tipo, periodo, evento y miembro
  def _compute_display_name(self):
    for rec in self:
      parts = []
      if rec.charge_type_id:
        parts.append(rec.charge_type_id.name)
      if rec.period_key:
        parts.append(rec.period_key)
      if rec.event_id:
        parts.append(rec.event_id.display_name)
      if rec.member_id:
        parts.append(rec.member_id.display_name)
      rec.display_name = " · ".join(parts) if parts else f"Cobro #{rec.id}"

  # Cálculo del importe total a partir de las líneas
  @api.depends("line_ids.subtotal")
  def _compute_amount_total(self):
    for rec in self:
      rec.amount_total = sum(rec.line_ids.mapped("subtotal"))

  # Validación para evitar cargos duplicados para el mismo miembro, tipo y periodo (excluyendo cancelados)
  @api.constrains("member_id", "charge_type_id", "period_key", "state")
  def _check_no_duplicate_period(self):
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
        raise ValidationError("Ya existe un cargo activo para este miembro, tipo y periodo")

  # Validación para asegurar que la clave de periodo sea adjunte o no debidamente según la periodicidad del tipo de cobro
  @api.constrains("charge_type_id", "period_key")
  def _check_period_key(self):
    for rec in self:
      if rec.periodicity == "single" and rec.period_key:
        raise ValidationError("Clave de período debe estar vacío para los cargos únicos")
      if rec.periodicity in ("monthly", "yearly") and not rec.period_key:
        raise ValidationError("Clave de período es obligatoria para los cargos mensuales/anuales")

  # Para periodicity = single -> period_key = NULL. PostgreSQL no garantiza unicidad con NULL = NULL, por eso se usa esta validación a nivel Python
  @api.constrains("member_id", "charge_type_id", "event_id", "registration_id", "state")
  def _check_no_duplicate_single(self):
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
        raise ValidationError("Ya existe un cargo único para este miembro, tipo y evento")

  # Validación para asegurar que event_id y registration_id correspondan al mismo evento cuando ambos están establecidos
  @api.constrains("registration_id", "event_id")
  def _check_event_matches_registration(self):
    for rec in self:
      if rec.registration_id and rec.event_id and rec.registration_id.event_id != rec.event_id:
        raise ValidationError("event_id debe coincidir con registration_id.event_id cuando ambos están establecidos")

  # Validación para impedir cancelar un cargo que ya tiene una factura activa en facturación
  @api.constrains("state", "invoice_id")
  def _check_cancel_with_invoice(self):
    for rec in self:
      if rec.state == "cancelled" and rec.invoice_id and rec.invoice_id.state != "cancel":
        raise ValidationError(
          "No se puede cancelar un cargo con una factura activa. "
          "Cancela primero la factura en facturación."
        )

  # Acción para generar una factura de cliente (account.move) a partir de este cobro y enlazarla
  def action_create_invoice(self):
    for rec in self:
      if rec.invoice_id:
        raise ValidationError("Este cobro ya tiene una factura asociada")
      if rec.state == "cancelled":
        raise ValidationError("No se puede facturar un cobro cancelado")
      if not rec.line_ids:
        raise ValidationError("El cobro no tiene líneas de detalle. Añade al menos una línea")

      # Construir las líneas de la factura
      # Si el tipo de cobro tiene producto, Odoo rellena impuestos y cuenta automáticamente
      # Si no, Odoo usa la cuenta por defecto del diario de ventas (proporcionada por l10n_es)
      invoice_lines = []
      for line in rec.line_ids:
        line_vals = {
          "name": line.name,
          "quantity": line.quantity,
          "price_unit": line.price_unit,
        }
        if rec.charge_type_id.product_id:
          line_vals["product_id"] = rec.charge_type_id.product_id.id
        invoice_lines.append((0, 0, line_vals))

      invoice = self.env["account.move"].create({
        "move_type": "out_invoice",
        "partner_id": rec.member_id.partner_id.id,
        "company_id": rec.company_id.id,
        "invoice_date": fields.Date.today(),
        "narration": f"Cargo: {rec.charge_type_id.name}"
                    + (f" — {rec.period_key}" if rec.period_key else ""),
        "invoice_line_ids": invoice_lines,
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

  # Acción para abrir la factura asociada a este cobro
  def action_open_invoice(self):
    self.ensure_one()
    if not self.invoice_id:
      return
    return {
      "type": "ir.actions.act_window",
      "res_model": "account.move",
      "res_id": self.invoice_id.id,
      "view_mode": "form",
      "target": "current",
    }

  # Acción para cancelar el cobro, sólo si no tiene factura activa
  def action_cancel(self):
    for rec in self:
      if rec.invoice_id and rec.invoice_id.state != "cancel":
        raise ValidationError(
          "No se puede cancelar un cobro con una factura activa. "
          "Cancela primero la factura en facturación."
        )
      rec.state = "cancelled"

  # Cron para generación automática de cuotas el día 1 de cada mes (configurado en data/comparsa_cron.xml)
  # En septiembre genera también las cuotas anuales
  def _cron_generate_fees(self):
    today = Date.today()
    fee_type = "both" if today.month == 9 else "monthly"
    self._generate_fees(month=today.month, year=today.year, fee_type=fee_type)

  # Generación de cuotas periódicas para los miembros activos
  def _generate_fees(self, month, year, fee_type="both"):
    Charge = self.env["comparsa.charge"]
    charge_type_mes = self.env["comparsa.charge.type"].search([("code", "=", "CUOTA_MES")], limit=1)
    charge_type_ano = self.env["comparsa.charge.type"].search([("code", "=", "CUOTA_ANO")], limit=1)

    period_monthly = f"{year:04d}-{month:02d}"
    period_yearly  = str(year)

    members = self.env["comparsa.member"].search([("active", "=", True)])
    created = skipped = 0

    for member in members:

      # CUOTA MENSUAL 
      if fee_type in ("monthly", "both") and member.payment_plan == "monthly" and charge_type_mes:
        # Verifica si ya existe una cuota para este miembro, tipo y periodo (excluyendo canceladas)
        exists = Charge.search_count([
          ("member_id",       "=", member.id),
          ("charge_type_id",  "=", charge_type_mes.id),
          ("period_key",      "=", period_monthly),
          ("state",           "!=", "cancelled"),
        ])
        if exists:
          skipped += 1
        else:
          Charge.create({
            "company_id":      member.company_id.id,
            "member_id":       member.id,
            "charge_type_id":  charge_type_mes.id,
            "period_key":      period_monthly,
            "line_ids": [(0, 0, {
              "name":       f"Cuota mensual {period_monthly}",
              "quantity":   1,
              "price_unit": member.regime_type_id.monthly_amount,
            })],
          })
          created += 1

      # CUOTA ANUAL
      if fee_type in ("yearly", "both") and member.payment_plan == "yearly" and charge_type_ano:
        # Verifica si ya existe una cuota para este miembro, tipo y periodo (excluyendo canceladas)
        exists = Charge.search_count([
          ("member_id",       "=", member.id),
          ("charge_type_id",  "=", charge_type_ano.id),
          ("period_key",      "=", period_yearly),
          ("state",           "!=", "cancelled"),
        ])
        if exists:
          skipped += 1
        else:
          Charge.create({
            "company_id":      member.company_id.id,
            "member_id":       member.id,
            "charge_type_id":  charge_type_ano.id,
            "period_key":      period_yearly,
            "line_ids": [(0, 0, {
              "name":       f"Cuota anual {period_yearly}",
              "quantity":   1,
              "price_unit": member.regime_type_id.yearly_amount,
            })],
          })
          created += 1

    return {"created": created, "skipped": skipped}
