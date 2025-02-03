from odoo import models, fields

class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    cn006_task_type = fields.Boolean(required=False, string='Etapa Tarea es (CN006)', 
            help='Permite identificar las etapas de tarea que pertenecen al módulo (CN006)', 
            default=False
            )

    
