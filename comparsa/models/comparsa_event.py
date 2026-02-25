# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ComparsaEvent(models.Model):
  #Nombre y descripcion del modelo de datos
  _name = "comparsa.event"
  _description = "Acto de la comparsa"
  _rec_name = "event_category_id"
  _order = "date desc, id desc"

  company_id = fields.Many2one(
    comodel_name="res.company",
    string="Comparsa",
    required=True,
    default=lambda self: self.env.company,
    index=True,
  )

  # Categoría del acto (catálogo configurable que incluye su clasificación)
  # No permite borrar una categoría si hay eventos que la usan
  event_category_id = fields.Many2one(
    comodel_name="comparsa.event.category",
    string="Categoría",
    required=True,
    index=True,
    ondelete="restrict",
  )

  # Calculado a partir de la categoría — almacenado para filtros y vistas
  # Hereda selection y etiquetas de comparsa.event.category.type
  event_type = fields.Selection(
    related="event_category_id.type",
    string="Tipo de acto",
    store=True,
    index=True,
  )

  date = fields.Datetime(
    string="Fecha/Hora",
    required=True,
    index=True
  )

  registration_mode = fields.Selection(
    selection=[
      ("none",                "Sin inscripción"),
      ("members_only",        "Solo miembros"),
      ("members_and_children","Miembros y niños"),
      ("members_and_guests",  "Miembros e invitados"),
      ("open",                "Miembros, invitados y niños"),
    ],
    string="Modo de inscripción",
    required=True,
    default="members_only",
    index=True,
  )

  pricing_mode = fields.Selection(
    selection=[("free", "Gratis"), ("fixed", "Fijo")],
    string="Modo de precio",
    required=True,
    default="free",
    index=True,
  )

  price_member = fields.Float(string="Precio miembro", default=0.0)
  price_guest = fields.Float(string="Precio invitado", default=0.0)
  price_children = fields.Float(string="Precio infantil", default=0.0)

  # Solo para actos de tipo comida
  restaurant_partner_id = fields.Many2one(
    comodel_name="res.partner",
    string="Restaurante",
    index=True,
    domain="[('comparsa_partner_type', '=', 'restaurant')]",
  )
  menu = fields.Text(string="Menú")
  active = fields.Boolean(string="Activo", default=True)

  registration_ids = fields.One2many(
    comodel_name="comparsa.event.registration",
    inverse_name="event_id",
    string="Inscripciones",
  )

  squad_event_ids = fields.One2many(
    comodel_name="comparsa.squad.event",
    inverse_name="event_id",
    string="Escuadras",
  )

  _MODES_WITH_GUESTS   = {"members_and_guests", "open"}
  _MODES_WITH_CHILDREN = {"members_and_children", "open"}

  # Validaciones para asegurar la coherencia entre el modo de inscripción, el modo de precio y los precios establecidos
  @api.constrains("pricing_mode", "registration_mode", "price_member", "price_guest", "price_children")
  def _check_prices(self):
    for rec in self:
      if rec.registration_mode == "none" and rec.pricing_mode != "free":
        raise ValidationError("El modo de precio debe ser gratuito cuando el acto no tiene inscripción")
      if rec.pricing_mode == "free":
        if rec.price_member != 0.0 or rec.price_guest != 0.0 or rec.price_children != 0.0:
          raise ValidationError("Los precios deben ser 0 cuando el modo de precio es gratuito")
      elif rec.pricing_mode == "fixed":
        if rec.registration_mode != "none" and rec.price_member <= 0:
          raise ValidationError("El precio de miembro debe ser mayor que 0 cuando el modo de precio es fijo")
        if rec.registration_mode in self._MODES_WITH_CHILDREN and rec.price_children <= 0:
          raise ValidationError("El precio infantil debe ser mayor que 0 para este modo de inscripción con precio fijo")
        if rec.registration_mode in self._MODES_WITH_GUESTS and rec.price_guest <= 0:
          raise ValidationError("El precio de invitado debe ser mayor que 0 para este modo de inscripción con precio fijo")

  # Validación para asegurar que los campos de comida solo se establezcan para eventos de tipo comida
  @api.constrains("event_category_id", "restaurant_partner_id", "menu")
  def _check_meal_fields(self):
    for rec in self:
      if rec.event_type != "meal" and (rec.restaurant_partner_id or rec.menu):
        raise ValidationError("El restaurant y el menú solo pueden establecerse para eventos de tipo comida")
