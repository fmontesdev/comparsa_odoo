# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ComparsaEvent(models.Model):
  #Nombre y descripcion del modelo de datos
  _name = "comparsa.event"
  _description = "Acto de la comparsa"
  _order = "date desc, id desc"

  company_id = fields.Many2one(
    "res.company",
    required=True,
    default=lambda self: self.env.company,
    index=True,
  )

  # Tipo de acto: festivo, comida, interno
  event_type = fields.Selection(
    selection=[("festive", "Festivo"), ("meal", "Comida"), ("internal", "Interno")],
    required=True,
    index=True,
  )

  # Subtipo de acto, que depende del tipo
  # No permite borrar un subtipo si hay eventos que lo usan
  event_subtype_id = fields.Many2one(
    "comparsa.event.subtype",
    required=True,
    index=True,
    ondelete="restrict",
  )

  date = fields.Datetime(required=True, index=True)

  registration_mode = fields.Selection(
    selection=[
      ("none", "No"),
      ("members_only", "Solo miembros"),
      ("members_and_guests", "Miembros y invitados"),
    ],
    required=True,
    default="members_only",
    index=True,
  )

  pricing_mode = fields.Selection(
    selection=[("free", "Gratis"), ("fixed", "Fijo")],
    required=True,
    default="free",
    index=True,
  )

  price_member = fields.Float(default=0.0)
  price_guest = fields.Float(default=0.0)
  price_children = fields.Float(default=0.0)

  # Solo para actos de tipo comida
  restaurant_partner_id = fields.Many2one(
    "res.partner",
    string="Restaurant",
    index=True,
  )
  menu = fields.Text()
  active = fields.Boolean(default=True)

  @api.constrains("pricing_mode", "registration_mode", "price_member", "price_guest", "price_children")
  def _check_prices(self):
    for rec in self:
      if rec.pricing_mode == "free":
        if rec.price_member != 0.0 or rec.price_guest != 0.0 or rec.price_children != 0.0:
          raise ValidationError("Los precios deben ser 0 cuando el modo de precio es gratuito.")
      elif rec.pricing_mode == "fixed":
        if rec.price_member <= 0 or rec.price_children <= 0:
          raise ValidationError("El precio para miembro e infantil debe ser mayor que 0 cuando el modo de precio es fijo.")
        # Solo validamos precios de invitado si el evento admite invitados
        if rec.registration_mode == "members_and_guests":
          if rec.price_guest <= 0:
            raise ValidationError("El precio de invitado debe ser mayor que 0 cuando el evento admite invitados y el modo de precio es fijo.")

  @api.constrains("event_type", "event_subtype_id")
  def _check_subtype_matches_type(self):
    for rec in self:
      if rec.event_subtype_id and rec.event_subtype_id.type != rec.event_type:
        raise ValidationError("El tipo de evento del subtipo debe coincidir con el tipo de evento")

  @api.constrains("event_type", "restaurant_partner_id", "menu")
  def _check_meal_fields(self):
    for rec in self:
      if rec.event_type != "meal" and (rec.restaurant_partner_id or rec.menu):
        raise ValidationError("El restaurant y el menú solo pueden establecerse para eventos de tipo comida")
