# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ComparsaChargeLine(models.Model):
  _name = "comparsa.charge.line"
  _description = "Línea de cobro de la comparsa"
  _order = "charge_id, id"

  charge_id = fields.Many2one(
    comodel_name="comparsa.charge",
    string="Cobro",
    required=True,
    index=True,
    ondelete="cascade",
  )

  name = fields.Char(string="Concepto", required=True)

  quantity = fields.Integer(string="Cantidad", required=True, default=1)

  price_unit = fields.Float(string="Precio unitario", required=True, default=0.0)

  subtotal = fields.Float(
    string="Subtotal",
    compute="_compute_subtotal",
    store=True,
  )

  @api.depends("quantity", "price_unit")
  def _compute_subtotal(self):
    for rec in self:
      rec.subtotal = rec.quantity * rec.price_unit
