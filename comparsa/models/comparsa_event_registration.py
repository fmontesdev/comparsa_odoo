# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ComparsaEventRegistration(models.Model):
  #Nombre y descripcion del modelo de datos
  _name = "comparsa.event.registration"
  _description = "Registro de asistencia a eventos de la comparsa"
  _order = "id desc"

  # No permite borrar el evento si tiene registros de asistencia asociados
  event_id = fields.Many2one(
    "comparsa.event",
    required=True,
    index=True,
    ondelete="restrict",
  )

  # No permite borrar el miembro si tiene registros de asistencia asociados
  member_id = fields.Many2one(
    "comparsa.member",
    index=True,
    ondelete="restrict",
  )
  # No permite borrar el invitado si tiene registros de asistencia
  guest_partner_id = fields.Many2one(
    "res.partner",
    index=True,
    ondelete="restrict",
  )
  # No permite borrar el comparsista que ha invitado a un invitado registrado
  invited_by_member_id = fields.Many2one(
    "comparsa.member",
    index=True,
    ondelete="restrict",
  )

  state = fields.Selection(
    selection=[("confirmed", "Confirmado"), ("cancelled", "Cancelado")],
    required=True,
    default="confirmed",
    index=True,
  )

  @api.constrains("event_id", "member_id", "state")
  def _check_no_duplicate_member_registration(self):
    """Un miembro no puede tener dos registros activos en el mismo evento."""
    for rec in self:
      if not rec.member_id:
        continue
      domain = [
        ("event_id", "=", rec.event_id.id),
        ("member_id", "=", rec.member_id.id),
        ("state", "!=", "cancelled"),
        ("id", "!=", rec.id),
      ]
      if self.search_count(domain):
        raise ValidationError("Este miembro ya tiene un registro activo en este evento.")

  @api.constrains("event_id", "guest_partner_id", "state")
  def _check_no_duplicate_guest_registration(self):
    """Un invitado no puede tener dos registros activos en el mismo evento."""
    for rec in self:
      if not rec.guest_partner_id:
        continue
      domain = [
        ("event_id", "=", rec.event_id.id),
        ("guest_partner_id", "=", rec.guest_partner_id.id),
        ("state", "!=", "cancelled"),
        ("id", "!=", rec.id),
      ]
      if self.search_count(domain):
        raise ValidationError("Este invitado ya tiene un registro activo en este evento.")

  @api.constrains("member_id", "guest_partner_id")
  def _check_xor_attendee(self):
    for rec in self:
      if bool(rec.member_id) == bool(rec.guest_partner_id):
        raise ValidationError("Solo puede haber un member_id o un guest_partner_id, no ambos ni ninguno")

  @api.constrains("guest_partner_id", "invited_by_member_id")
  def _check_guest_requires_inviter(self):
    for rec in self:
      if rec.guest_partner_id and not rec.invited_by_member_id:
        raise ValidationError("El registro de un invitado requiere un miembro que lo haya invitado")

  @api.constrains("event_id", "guest_partner_id")
  def _check_registration_mode(self):
    for rec in self:
      mode = rec.event_id.registration_mode
      if mode == "none":
        raise ValidationError("Este evento no permite registros")
      if mode == "members_only" and rec.guest_partner_id:
        raise ValidationError("Este evento no permite registros de invitados")

  @api.constrains("event_id", "member_id")
  def _check_member_permission_by_regime(self):
    """Permiso por régimen:
    Permitido si:
    - allow_*_by_default según event_type
    - o event está en allowed_event_ids del régimen
    """
    for rec in self:
      if not rec.member_id:
        continue

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
        raise ValidationError("El régimen del miembro no permite registrarse a este evento")