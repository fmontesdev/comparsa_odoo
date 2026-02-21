# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError

#Definimos el modelo de datos
class ComparsaSquadEvent(models.Model):
  #Nombre y descripcion del modelo de datos
  _name = "comparsa.squad.event"
  _description = "Squad Logistics for Festive Event"
  _order = "event_id desc, order asc"

  # No permite borrar el evento si tiene asignaciones de escuadra asociadas
  event_id = fields.Many2one(
    "comparsa.event",
    required=True,
    index=True,
    ondelete="restrict",
  )
  # No permite borrar la escuadra si tiene asignaciones de eventos de escuadra asociadas
  squad_id = fields.Many2one(
    "comparsa.squad",
    required=True,
    index=True,
    ondelete="restrict",
  )

  order = fields.Integer(required=True, index=True)

  # No permite borrar bandas de música si tiene asignaciones de eventos de escuadra en eventos
  band_partner_id = fields.Many2one(
    "res.partner",
    index=True,
    ondelete="restrict",
  )

  _uniq_event_squad = models.Constraint('UNIQUE(event_id, squad_id)', 'Una escuadra solo puede aparecer una vez por evento')
  _uniq_event_order = models.Constraint('UNIQUE(event_id, order)', 'El orden debe ser único dentro del evento')

  @api.constrains("event_id")
  def _check_event_is_festive(self):
    for rec in self:
      if rec.event_id.event_type != "festive":
        raise ValidationError("La logística de escuadra solo puede asignarse a actos festivos.")