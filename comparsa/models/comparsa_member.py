# -*- coding: utf-8 -*-
from odoo import fields, models

class ComparsaMember(models.Model):
  #Nombre y descripcion del modelo de datos
  _name = "comparsa.member"
  _description = "Comparsista"
  _inherits = {"res.partner": "partner_id"}
  _rec_name = "name"
  _order = 'id desc'

  # Herencia delegada a res.partner
  partner_id = fields.Many2one(
    "res.partner",
    required=True,
    ondelete="cascade",
    index=True,
  )

  # Comparsa = company
  company_id = fields.Many2one(
    "res.company",
    required=True,
    default=lambda self: self.env.company,
    index=True,
  )

  regime_type_id = fields.Many2one(
    "comparsa.member.regime.type",
    required=True,
    ondelete="restrict",
    index=True,
  )

  payment_plan = fields.Selection(
    selection=[("monthly", "Mensual"), ("yearly", "Anual")],
    required=True,
    default="monthly",
    index=True,
  )

  squad_id = fields.Many2one(
    "comparsa.squad",
    required=True,
    ondelete="restrict",
    index=True,
  )

  # Propio del modelo, independiente del active del res.partner delegado
  active = fields.Boolean(default=True)

  # Restricciones SQL
  _uniq_member_partner_company = models.Constraint(
    'UNIQUE(partner_id, company_id)',
    'Un comparsista (partner) solo puede ser miembro de una comparsa (company)'
  )
