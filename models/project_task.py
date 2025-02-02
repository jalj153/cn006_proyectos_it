from odoo import models, fields

class ProjectTask(models.Model):
    _inherit = 'project.task'

    cn006_grado_avance_id      = fields.Many2one('cn006.proyecto.tarea.grado.avance',  string='Grado Avance', help='Grado de avance de la tarea.')
    cn006_tipificacion_id      = fields.Many2one('cn006.proyecto.tarea.tipificacion',  string='Tipo Tarea', help='Clasificación de tareas para agrupación de horas.')
