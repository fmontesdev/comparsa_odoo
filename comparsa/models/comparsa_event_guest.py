# -*- coding: utf-8 -*-
from odoo import fields, models


class ComparsaEventGuest(models.Model):
    # Nombre y descripcion del modelo de datos
    _name = "comparsa.event.guest"
    _description = "Invitado a un acto de la comparsa"
    _order = "id asc"

    # Registro de asistencia al que pertenece el invitado
    registration_id = fields.Many2one(
        comodel_name="comparsa.event.registration",
        string="Registro",
        required=True,
        index=True,
        ondelete="cascade",
    )

    # Para invitados sin nombre conocido usar el contacto «Anónimo»
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Invitado",
        required=True,
        index=True,
        ondelete="restrict",
    )
