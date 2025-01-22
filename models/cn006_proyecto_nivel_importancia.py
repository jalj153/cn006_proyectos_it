from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CN006ProyectoNivelImportancia(models.Model):
    _name = 'cn006.proyecto.nivel.importancia'
    _description = '(CN006) Niveles de Importancia de los proyectos IT'
    _order = 'name ASC'

    name = fields.Char(string='Importancia', required=True)  # Este campo se usará para mostrar valores
    cn006_descripcion = fields.Char(string='Descripción', required=False)

    
    _sql_constraints = [
        ('unique_cn006_name', 'UNIQUE(cn006_name)', 'El nivel de importancia debe ser único.'),
    ]

