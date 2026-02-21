# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError

#Definimos el modelo de datos
class ComparsaPayment(models.Model):
  #Nombre y descripcion del modelo de datos
  _name = "comparsa.payment"
  _description = "Pago de un cargo de la comparsa"
  _order = "payment_date desc, id desc"

  # No permite borrar el cargo si tiene pagos asociados
  charge_id = fields.Many2one(
    "comparsa.charge",
    required=True,
    index=True,
    ondelete="restrict",
  )

  # No permite borrar el miembro si tiene pagos asociados
  # Redundante por eficiencia; debe coincidir con charge.member_id
  member_id = fields.Many2one(
    "comparsa.member",
    required=True,
    index=True,
    ondelete="restrict",
  )

  amount = fields.Float(required=True)
  payment_date = fields.Datetime(required=True, default=fields.Datetime.now)

  method = fields.Selection(
    selection=[
      ("cash", "Efectivo"),
      ("transfer", "Transferencia bancaria"),
      ("card", "Tarjeta"),
      ("bizum", "Bizum"),
      ("other", "Otro"),
    ],
    required=True,
    default="cash",
    index=True,
  )

  @api.constrains("member_id", "charge_id")
  def _check_member_matches_charge(self):
    for rec in self:
      if rec.charge_id and rec.member_id != rec.charge_id.member_id:
        raise ValidationError("El miembro del pago debe coincidir con el miembro del cargo asociado")

  @api.constrains("amount")
  def _check_amount(self):
    for rec in self:
      if rec.amount <= 0:
        raise ValidationError("El importe del pago debe ser mayor que 0")
