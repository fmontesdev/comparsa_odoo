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
    comodel_name="res.partner",
    string="Miembro",
    required=True,
    ondelete="cascade",
    index=True,
  )

  # Comparsa = company
  company_id = fields.Many2one(
    comodel_name="res.company",
    string="Comparsa",
    required=True,
    default=lambda self: self.env.company,
    index=True,
  )

  regime_type_id = fields.Many2one(
    comodel_name="comparsa.member.regime.type",
    string="Régimen",
    required=True,
    ondelete="restrict",
    index=True,
  )

  payment_plan = fields.Selection(
    selection=[("monthly", "Mensual"), ("yearly", "Anual")],
    string="Plan de pago",
    required=True,
    default="monthly",
    index=True,
  )

  squad_id = fields.Many2one(
    comodel_name="comparsa.squad",
    string="Escuadra",
    required=True,
    ondelete="restrict",
    index=True,
  )

  # Cargos del comparsista
  role_assignment_ids = fields.One2many(
    comodel_name="comparsa.role.assignment",
    inverse_name="member_id",
    string="Cargos",
  )

  # Propio del modelo, independiente del active del res.partner delegado
  active = fields.Boolean(string="Activo", default=True)

  # Restricciones SQL
  _uniq_member_partner_company = models.Constraint(
    'UNIQUE(partner_id, company_id)',
    'Un comparsista (partner) solo puede ser miembro de una comparsa (company)'
  )
