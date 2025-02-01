from odoo import models, fields

class ProjectTask(models.Model):
    _inherit = 'project.task'

    cn006_grado_avance_id      = fields.Many2one('cn006.proyecto_tarea.grado.avance',      string='Grado Avance', help='Grado de avance de la tarea.')
