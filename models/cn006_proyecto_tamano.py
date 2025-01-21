from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CN006ProyectoTamano(models.Model):
    _name = 'cn006.proyecto.tamano'
    _description = 'Tamaño de los proyectos IT'
    _order = 'tamano ASC'

    cn006_tamano = fields.Char(string='Tamaño', required=True, unique=True)
    cn006_descripcion = fields.Char(string='Descripción', required=False)

    
    _sql_constraints = [
        ('unique_cn006_tamano', 'UNIQUE(cn006_tamano)', 'El tamano debe ser único.'),
    ]

