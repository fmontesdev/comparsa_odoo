# -*- coding: utf-8 -*-
from datetime import date as Date
from odoo import api, fields, models

_MESES = [
  ("1",  "Enero"),
  ("2",  "Febrero"),
  ("3",  "Marzo"),
  ("4",  "Abril"),
  ("5",  "Mayo"),
  ("6",  "Junio"),
  ("7",  "Julio"),
  ("8",  "Agosto"),
  ("9",  "Septiembre"),
  ("10", "Octubre"),
  ("11", "Noviembre"),
  ("12", "Diciembre"),
]

class ComparsaChargeGenerationWizard(models.TransientModel):
  _name = "comparsa.charge.generation.wizard"
  _description = "Asistente de generación de cuotas periódicas"

  target_month = fields.Selection(
    selection=_MESES,
    string="Mes",
    required=True,
    default=lambda self: str(Date.today().month),
  )

  target_year = fields.Integer(
    string="Año",
    required=True,
    default=lambda self: Date.today().year,
  )

  fee_type = fields.Selection(
    selection=[
      ("monthly", "Solo mensuales"),
      ("yearly",  "Solo anuales"),
      ("both",    "Mensuales y anuales"),
    ],
    string="Tipo de cuota",
    required=True,
    default="monthly",
  )

  # Campos de resultado (solo lectura, visibles tras generar)
  state = fields.Selection(
    selection=[("draft", "Borrador"), ("done", "Generado")],
    default="draft",
    readonly=True,
  )

  result_created = fields.Integer(string="Cuotas creadas", readonly=True)
  result_skipped = fields.Integer(string="Ya existían (omitidas)", readonly=True)

  def action_generate(self):
    # Llama al método de generación de cuotas del modelo comparsa.charge, pasando mes, año y tipo de cuota
    result = self.env["comparsa.charge"]._generate_fees(
      month=int(self.target_month),
      year=self.target_year,
      fee_type=self.fee_type,
    )
    # Actualiza el estado y los resultados en el asistente
    self.write({
      "state": "done",
      "result_created": result["created"],
      "result_skipped": result["skipped"],
    })
    # Reabre el mismo wizard para mostrar los resultados
    return {
      "type":      "ir.actions.act_window",
      "res_model": self._name,
      "res_id":    self.id,
      "view_mode": "form",
      "target":    "new",
    }
