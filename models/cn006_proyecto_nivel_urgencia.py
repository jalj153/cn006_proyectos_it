from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CN006ProyectoNivelUrgencia(models.Model):
    _name = 'cn006.proyecto.nivel.urgencia'
    _description = '(CN006) Niveles de Urgencia de los proyectos IT'
    _order = 'nivel_urgencia ASC'

    cn006_nivel_urgencia = fields.Integer(string='Nivel de Urgencia', required=True, unique=True)
    cn006_descripcion = fields.Char(string='Descripción', required=False)

    
    _sql_constraints = [
        ('unique_cn006_nivel_urgencia', 'UNIQUE(cn006_nivel_urgencia)', 'El nivel de urgencia debe ser único.'),
        ('positive_cn006_nivel_urgencia', 'CHECK(cn006_nivel_urgencia > 0)', 'El nivel de urgencia debe ser un número mayor a CERO.'),
    ]

    @api.constrains('nivel_urgencia')
    def _check_positive_value(self):
        for record in self:
            if record.cn006_nivel_urgencia <= 0:
                raise ValidationError("El nivel de urgencia debe ser un número mayor a CERO.")
