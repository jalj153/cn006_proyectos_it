from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CN006ProyectoTipo(models.Model):
    _name = 'cn006.proyecto.tipo.proyecto'
    _description = '(CN006) Tipo de proyectos IT'
    _order = 'name ASC'

    cn006_tipo_proyecto = fields.Char(string='Tipo', required=True) 
    cn006_descripcion = fields.Char(string='Descripción', required=False)

    
    _sql_constraints = [
        ('unique_cn006_tipo_proyecto', 'UNIQUE(cn006_tipo_proyecto)', 'El tipo debe ser único.'),
    ]

