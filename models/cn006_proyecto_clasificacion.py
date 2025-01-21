from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CN006ProyectoClasificacion(models.Model):
    _name = 'cn006.proyecto.clasificacion'
    _description = '(CN006) Clasificación de los proyectos IT'
    _order = 'cn006_clasificacion ASC'

    cn006_clasificacion = fields.Char(string='Clasificación', required=True, unique=True)
    cn006_descripcion = fields.Char(string='Descripción', required=False)

    
    _sql_constraints = [
        ('unique_cn006_clasificacion', 'UNIQUE(cn006_clasificacion)', 'La clasificación debe ser única.'),
    ]

