# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


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
    # Excluye empresas y partners clasificados como banda o restaurante
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Invitado",
        required=True,
        index=True,
        ondelete="restrict",
        domain="[('is_company', '=', False), ('member_ids', '=', False), ('comparsa_partner_type', 'not in', ['band', 'restaurant'])]",
    )

    # Validación para evitar crear o modificar invitados si el registro de asistencia ya tiene un cobro generado
    def _check_no_charge(self):
        for rec in self:
            if rec.registration_id.charge_id:
                raise ValidationError(
                    "No se pueden modificar los invitados porque la inscripción ya tiene un cobro generado.\n"
                    "Cancela primero el cobro si necesitas hacer cambios."
                )

    # Al añadir un invitado se valida que no haya un cobro generado
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._check_no_charge()
        return records

    # Al eliminar un invitado se valida que no haya un cobro generado
    def unlink(self):
        self._check_no_charge()
        return super().unlink()
