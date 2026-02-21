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

    def write(self, vals):
        """Sincroniza el estado del cargo cuando cambia el estado de pago de la factura."""
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

    def unlink(self):
        """Si se elimina una factura borrador enlazada a un cargo, reseteamos el cargo.
        ondelete='set null' vacía invoice_id en BD pero no ajusta el state del cargo.
        """
        charges = self.env["comparsa.charge"].search(
            [("invoice_id", "in", self.ids)]
        )
        result = super().unlink()
        # Tras el unlink, invoice_id ya es False (set null); sólo corregimos el state
        charges.filtered(lambda c: c.state == "invoiced").write({"state": "pending"})
        return result
