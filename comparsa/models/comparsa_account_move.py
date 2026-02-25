# -*- coding: utf-8 -*-
from odoo import models

# Mapa de payment_state de account.move → state de comparsa.charge
_PAYMENT_STATE_MAP = {
    "not_paid": "invoiced",
    "in_payment": "paid",
    "paid": "paid",
    "partial": "partial",
    "reversed": "invoiced",
}

class AccountMove(models.Model):
    _inherit = "account.move"

    # Sincronización del estado del cobro cuando se modifica el estado de pago de la factura
    def write(self, vals):
        result = super().write(vals)
        if "payment_state" not in vals and "state" not in vals:
            return result
        # Buscamos los cargos enlazados a las facturas modificadas
        charges = self.env["comparsa.charge"].search(
            [("invoice_id", "in", self.ids)]
        )
        for charge in charges:
            invoice = charge.invoice_id
            # Factura cancelada => el cargo vuelve a pendiente y pierde el enlace
            if invoice.state == "cancel":
                charge.write({"state": "pending", "invoice_id": False})
                continue
            # Factura confirmada => sincronizamos según payment_state
            if invoice.state == "posted":
                new_state = _PAYMENT_STATE_MAP.get(invoice.payment_state)
                if new_state and charge.state != new_state:
                    charge.write({"state": new_state})
        return result

    # Si se elimina una factura enlazada a un cargo, cambiamos el estado del cargo a pendiente y eliminamos el enlace
    def unlink(self):
        charges = self.env["comparsa.charge"].search(
            [("invoice_id", "in", self.ids)]
        )
        result = super().unlink()
        # Tras el unlink, invoice_id ya es False (set null); sólo corregimos el state
        charges.filtered(lambda c: c.state == "invoiced").write({"state": "pending"})
        return result
