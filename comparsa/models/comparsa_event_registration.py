# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ComparsaEventRegistration(models.Model):
  # Nombre y descripción del modelo de datos
  _name = "comparsa.event.registration"
  _description = "Registro de asistencia a eventos de la comparsa"
  _order = "id desc"

  # No permite borrar el evento si tiene registros de asistencia asociados
  event_id = fields.Many2one(
    comodel_name="comparsa.event",
    string="Acto",
    required=True,
    index=True,
    ondelete="restrict",
  )

  # Tipo de acto heredado del evento — almacenado para filtros y agrupamientos
  event_type = fields.Selection(
    related="event_id.event_type",
    string="Tipo de acto",
    store=True,
    index=True,
  )

  # Modo de registro heredado del evento — usado para controlar la visibilidad de campos en la vista
  registration_mode = fields.Selection(
    related="event_id.registration_mode",
    string="Modo de inscripción",
  )

  # El comparsista que realiza el registro y asume el cobro
  # No permite borrar el miembro si tiene registros de asistencia asociados
  member_id = fields.Many2one(
    comodel_name="comparsa.member",
    string="Miembro",
    required=True,
    index=True,
    ondelete="restrict",
  )

  # Acompañante (pareja/cónyuge)
  with_partner = fields.Boolean(string="Con pareja", default=False)

  # Niños a cargo del comparsista
  num_children = fields.Integer(string="Niños", default=0)

  # Invitados (personas no miembros)
  guest_ids = fields.One2many(
    comodel_name="comparsa.event.guest",
    inverse_name="registration_id",
    string="Invitados",
  )

  state = fields.Selection(
    selection=[("confirmed", "Confirmada"), ("cancelled", "Cancelada")],
    string="Estado",
    required=True,
    default="confirmed",
    index=True,
  )

  # Campo calculado para mostrar el número de invitados
  guest_count = fields.Integer(
    string="Invitados",
    compute="_compute_guest_count",
    store=True,
  )

  # Campo calculado para mostrar los nombres de los invitados en la vista de lista
  guest_names = fields.Char(
    string="Invitados",
    compute="_compute_guest_count",
    store=True,
  )

  # Total de plazas: miembro + pareja + niños + invitados
  total_attendees = fields.Integer(
    string="Total plazas",
    compute="_compute_total_attendees",
    store=True,
  )

  # Cobro generado al inscribirse en un acto de pago
  # Many2one + UNIQUE = equivalente a una relación 1:1 (Odoo no tiene campo One2one nativo)
  charge_id = fields.Many2one(
    comodel_name="comparsa.charge",
    string="Cobro",
    readonly=True,
    ondelete="set null",
    copy=False,
  )

  # Campo calculado para mostrar como nombre visible de la inscripción el nombre del evento y miembro
  def _compute_display_name(self):
    for rec in self:
      event = rec.event_id.display_name or "?"
      member = rec.member_id.display_name or "?"
      rec.display_name = f"{event} · {member}"

  _uniq_registration_charge = models.Constraint(
    "UNIQUE(charge_id)",
    "Una inscripción solo puede tener un cobro asociado.",
  )

  # Cálculo de guest_count y guest_names a partir de guest_ids
  @api.depends("guest_ids", "guest_ids.partner_id")
  def _compute_guest_count(self):
    for rec in self:
      rec.guest_count = len(rec.guest_ids)
      names = [g.partner_id.name for g in rec.guest_ids]
      rec.guest_names = ", ".join(names) if names else False

  # Cálculo del total de asistentes para una inscripción
  @api.depends("with_partner", "num_children", "guest_count")
  def _compute_total_attendees(self):
    for rec in self:
      rec.total_attendees = 1 + (1 if rec.with_partner else 0) + rec.num_children + rec.guest_count

  # Validación para asegurar que un miembro no pueda tener dos inscripciones activas en el mismo evento
  @api.constrains("event_id", "member_id", "state")
  def _check_no_duplicate_member_registration(self):
    for rec in self:
      domain = [
        ("event_id", "=", rec.event_id.id),
        ("member_id", "=", rec.member_id.id),
        ("state", "!=", "cancelled"),
        ("id", "!=", rec.id),
      ]
      if self.search_count(domain):
        raise ValidationError("Este miembro ya tiene una inscripción activa en este evento")

  # Validación para asegurar que el número de niños no sea negativo
  @api.constrains("num_children")
  def _check_num_children(self):
    for rec in self:
      if rec.num_children < 0:
        raise ValidationError("El número de niños no puede ser negativo")

  # Validación para asegurar que el modo de inscripción del evento permita el tipo de asistentes registrados
  @api.constrains("event_id", "guest_ids", "num_children")
  def _check_registration_mode(self):
    for rec in self:
      mode = rec.event_id.registration_mode
      if mode == "none":
        raise ValidationError("Este evento no permite inscripciones")
      has_guests = bool(rec.guest_ids)
      has_children = rec.num_children > 0
      allows_guests   = mode in {"members_and_guests", "open"}
      allows_children = mode in {"members_and_children", "open"}
      if has_guests and not allows_guests:
        raise ValidationError("Este evento no permite inscribir invitados")
      if has_children and not allows_children:
        raise ValidationError("Este evento no permite inscribir niños")

  # Validación para asegurar que el régimen del miembro permita inscribirse al evento según su tipo
  # Permitido si: allow_*_by_default según event_type, o event está en allowed_event_ids del régimen
  @api.constrains("event_id", "member_id")
  def _check_member_permission_by_regime(self):
    for rec in self:
      regime = rec.member_id.regime_type_id
      event = rec.event_id

      allowed_by_default = False
      if event.event_type == "festive":
        allowed_by_default = regime.allow_festive_by_default
      elif event.event_type == "meal":
        allowed_by_default = regime.allow_meal_by_default
      elif event.event_type == "internal":
        allowed_by_default = regime.allow_internal_by_default

      allowed_by_exception = event in regime.allowed_event_ids

      if not (allowed_by_default or allowed_by_exception):
        raise ValidationError("El régimen del miembro no permite inscribirse a este evento")

  # Solo crea el cargo automáticamente si el acto tiene modo de precio fijo
  @api.model_create_multi
  def create(self, vals_list):
    records = super().create(vals_list)
    for rec in records:
      if rec.event_id.pricing_mode == "fixed":
        rec._create_charge()
    return records

  # Crea el cargo al registrar la inscripción en un acto de pago
  def _create_charge(self):
    self.ensure_one()
    charge_type = self.env["comparsa.charge.type"].search([("code", "=", "ACTO")], limit=1)
    if not charge_type:
      raise ValidationError(
        "No se encontró el tipo de cobro con código 'ACTO'. "
        "Créalo en Configuración → Tipos de cobro."
      )
    event = self.event_id
    lines = [
      (0, 0, {
        "name": f"Miembro: {self.member_id.display_name}",
        "quantity": 1,
        "price_unit": event.price_member,
      })
    ]
    if self.with_partner:
      lines.append((0, 0, {
        "name": "Acompañante",
        "quantity": 1,
        "price_unit": event.price_member,
      }))
    if self.num_children > 0:
      lines.append((0, 0, {
        "name": "Niños",
        "quantity": self.num_children,
        "price_unit": event.price_children,
      }))
    for guest in self.guest_ids:
      lines.append((0, 0, {
        "name": f"Invitado: {guest.partner_id.name}",
        "quantity": 1,
        "price_unit": event.price_guest,
      }))
    charge = self.env["comparsa.charge"].create({
      "company_id": event.company_id.id,
      "member_id": self.member_id.id,
      "charge_type_id": charge_type.id,
      "event_id": event.id,
      "registration_id": self.id,
      "line_ids": lines,
    })
    self.charge_id = charge

  # Permite cambiar el estado de la inscripción a confirmado
  def action_confirm(self):
    self.write({"state": "confirmed"})

  # Abre el cobro asociado a esta inscripción
  def action_open_charge(self):
    self.ensure_one()
    if not self.charge_id:
      return
    return {
      "type": "ir.actions.act_window",
      "res_model": "comparsa.charge",
      "res_id": self.charge_id.id,
      "view_mode": "form",
      "target": "current",
    }

  # Cancela la inscripción. Bloquea si el cobro ya está facturado o pagado
  def action_cancel(self):
    for rec in self:
      if rec.charge_id and rec.charge_id.state != "cancelled":
        if rec.charge_id.state != "pending":
          state_label = dict(rec.charge_id._fields["state"].selection).get(rec.charge_id.state, rec.charge_id.state)
          raise ValidationError(
            f"No se puede cancelar la inscripción porque el cobro está en estado '{state_label}'.\n"
            "Gestiona primero el cobro antes de cancelar la inscripción."
          )
        rec.charge_id.state = "cancelled"
      rec.state = "cancelled"
