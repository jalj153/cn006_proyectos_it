from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CN006ProyectoNivelUrgencia(models.Model):
    _name = 'cn006.proyecto.nivel.urgencia'
    _description = '(CN006) Niveles de Urgencia de los proyectos IT'
    _order = 'name ASC'

    name = fields.Char(string='Urgencia', required=True)  # Este campo se usará para mostrar valores
    cn006_descripcion = fields.Char(string='Descripción', required=False)

    
    _sql_constraints = [
        ('unique_ame', 'UNIQUE(name)', 'El nivel de urgencia debe ser único.'),
    ]
