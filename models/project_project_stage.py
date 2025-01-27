from odoo import models, fields

class ProjectTask(models.Model):
    _inherit = 'project.project.stage'

    cn006_stage = fields.Boolean(required=False, string='Etapa es (CN006)', help='Permite filtrar los proyectos asociados al módulo', default=False)

    
