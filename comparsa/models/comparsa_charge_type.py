# -*- coding: utf-8 -*-
from odoo import fields, models

class ComparsaChargeType(models.Model):
  #Nombre y descripcion del modelo de datos
  _name = "comparsa.charge.type"
  _description = "Tipo de cargo de la comparsa"
  _order = "name"

  name = fields.Char(string="Nombre", required=True)
  code = fields.Char(string="Código", required=True, index=True)

  periodicity = fields.Selection(
    selection=[("monthly", "Mensual"), ("yearly", "Anual"), ("single", "Único")],
    string="Periodicidad",
    required=True,
    default="single",
  )

  # Si se indica, las facturas generadas incluirán este producto en cada línea lo que permite aplicar los impuestos
  # y la categoría contable definidos en él. Si se deja vacío, Odoo usará los valores por defecto del diario de ventas
  product_id = fields.Many2one(
    comodel_name="product.product",
    string="Producto en factura",
    domain="[('type', '=', 'service')]",
    check_company=True,
  )

  active = fields.Boolean(string="Activo", default=True)

  _uniq_charge_type_code = models.Constraint('UNIQUE(code)', 'El cobro debe tener un código único')
