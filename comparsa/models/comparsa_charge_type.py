# -*- coding: utf-8 -*-
from odoo import fields, models

class ComparsaChargeType(models.Model):
  #Nombre y descripcion del modelo de datos
  _name = "comparsa.charge.type"
  _description = "Tipo de cargo de la comparsa"
  _order = "name"

  name = fields.Char(string="Nombre", required=True)
  code = fields.Char(string="Código", required=True, index=True)
  active = fields.Boolean(string="Activo", default=True)

  # Cuenta de ingresos usada al generar la factura desde un cargo de este tipo
  account_id = fields.Many2one(
    "account.account",
    string="Cuenta contable",
    domain="[('account_type', 'in', ['income', 'income_other'])]",
    ondelete="restrict",
  )

  _uniq_charge_type_code = models.Constraint('UNIQUE(code)', 'El cobro debe tener un código único')
