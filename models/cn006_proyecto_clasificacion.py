from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CN006ProyectoClasificacion(models.Model):
    _name = 'cn006.proyecto.clasificacion'
    _description = '(CN006) Clasificación de los proyectos IT'
    _order = 'name ASC'

    name = fields.Char(string='Clasificación', required=True) 
    cn006_descripcion = fields.Char(string='Descripción', required=False)

    
    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', 'La clasificación debe ser única.'),
    ]

