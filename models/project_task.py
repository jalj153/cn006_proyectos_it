from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)
class ProjectTask(models.Model):
    _inherit = 'project.task'

    cn006_grado_avance_id   = fields.Many2one('cn006.proyecto.tarea.grado.avance', string='Grado Avance', help='Grado de avance de la tarea.')
    cn006_es_implementacion = fields.Boolean(string="Es Implementación", compute="_compute_cn006_es_implementacion", store=True)
    cn006_tipificacion_id   = fields.Many2one('cn006.proyecto.tarea.tipificacion', string='Tipo Tarea', help='Clasificación de tareas para agrupación de horas.')
    cn006_tipo_soporte_id   = fields.Many2one('cn006.proyecto.tarea.tipo.soporte', string='Tipo Soporte Asociado', help='Si la tarea es IMPLEMENTACIÓN se debe seleccionar la incidencia')

    @api.depends('cn006_tipificacion_id')
    def _compute_cn006_es_implementacion(self):
        _logger.info(f"(cn006) Recalculado creo que es poque se grabó el registro.")
        try:
            implementacion_id = self.env.ref('cn006_proyectos_it.cn006_proyecto_tarea_tipificacion_30').id
        except ValueError:
            implementacion_id = False

        for record in self:
            record.cn006_es_implementacion = record.cn006_tipificacion_id.id == implementacion_id

    @api.onchange('cn006_tipificacion_id')
    def _onchange_cn006_tipificacion_id(self):
        _logger.info(f"(cn006) Detecté un cambio.  voy a actualizar valor de cn006_es_implementacion ({self.cn006_es_implementacion})")
        for record in self:
            record._compute_cn006_es_implementacion()
        _logger.info(f"(cn006) Ya realicé el cambio.  Valor de cn006_es_implementacion ({self.cn006_es_implementacion})")
        _logger.info(f"(cn006) Ya realicé el cambio.  Valor de record ({record.cn006_es_implementacion})")


