# -*- coding: utf-8 -*-
from odoo import fields, models

# Hereda el modelo de contactos
class ResPartner(models.Model):
  _inherit = "res.partner"

  # Clasifica los contactos externos a la comparsa que no tienen modelo propio
  # No incluye "guest" (no se encasilla, se excluye por dominio en los campos de invitado)
  comparsa_partner_type = fields.Selection(
    selection=[
      ("band", "Banda de música"),
      ("restaurant", "Restaurante"),
    ],
    string="Tipo comparsa",
    index=True,
  )

  # Inverso de comparsa.member.partner_id — permite filtrar miembros en dominios
  member_ids = fields.One2many(
    comodel_name="comparsa.member",
    inverse_name="partner_id",
    string="Miembro de comparsa",
  )
