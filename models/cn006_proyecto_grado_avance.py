from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CN006ProyectoGradoAvance(models.Model):
    _name = 'cn006.proyecto.grado.avance'
    _description = '(CN006) Grado de Avance de los proyectos IT'
    _order = 'cn006_orden ASC'

    cn006_orden = fields.Integer(string='Orden', required=True, unique=True)
    cn006_grado_avance = fields.Char(string='Descripción', required=True, unique=True)
    cn006_descripcion = fields.Char(string='Descripción', required=False)

    
    _sql_constraints = [
        ('unique_cn006_orden', 'UNIQUE(cn006_orden)', 'El orden asignado debe ser único.'),
        ('positive_cn006_orden', 'CHECK(cn006_orden > 0)', 'El orden asignado debe ser un número mayor a CERO.'),
        ('unique_cn006_grado_avance', 'UNIQUE(cn006_grado_avance)', 'El grado de avance debe ser único.'),
    ]

    @api.constrains('orden')
    def _check_positive_value(self):
        for record in self:
            if record.cn006_orden <= 0:
                raise ValidationError("El orden asignado debe ser un número mayor a CERO.")