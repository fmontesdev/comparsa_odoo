# -*- coding: utf-8 -*-
from odoo import models

_PAYMENT_STATE_MAP = {
  "not_paid": "invoiced",
  "in_payment": "paid",
  "paid": "paid",
  "partial": "partial",
  "reversed": "invoiced",
}

class AccountMove(models.Model):
  _inherit = "account.move"

  # Sincroniza el estado de los cobros cuando se actualiza el estado de pago de la factura
  def _compute_payment_state(self):
    super()._compute_payment_state()
    charges = self.env["comparsa.charge"].search(
      [("invoice_id", "in", self.ids)]
    )
    for charge in charges:
      invoice = charge.invoice_id
      # Factura cancelada -> el cargo vuelve a pendiente y se desvincula
      if invoice.state == "cancel":
        charge.write({"state": "pending", "invoice_id": False})
        continue
      # Factura publicada -> sincronizamos según el estado de pago
      if invoice.state == "posted":
        new_state = _PAYMENT_STATE_MAP.get(invoice.payment_state)
        if new_state and charge.state != new_state:
          charge.write({"state": new_state})

  def unlink(self):
    # Antes de eliminar capturamos los cargos enlazados
    charges = self.env["comparsa.charge"].search(
      [("invoice_id", "in", self.ids)]
    )
    result = super().unlink()
    # Factura eliminada -> el cargo vuelve a pendiente (invoice_id ya es False por ondelete=set null)
    charges.write({"state": "pending"})
    return result
