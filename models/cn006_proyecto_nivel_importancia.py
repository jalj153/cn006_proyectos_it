from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CN006ProyectoNivelImportancia(models.Model):
    _name = 'cn006.proyecto.nivel.importancia'
    _description = '(CN006) Niveles de Importancia de los proyectos IT'
    _order = 'nivel_importancia ASC'

    cn006_nivel_importancia = fields.Integer(string='Nivel de Importancia', required=True, unique=True)
    cn006_descripcion = fields.Char(string='Descripción', required=False)

    
    _sql_constraints = [
        ('unique_cn006_nivel_importancia', 'UNIQUE(cn006_nivel_importancia)', 'El nivel de importancia debe ser único.'),
        ('positive_cn006_nivel_importancia', 'CHECK(cn006_nivel_importancia > 0)', 'El nivel de importancia debe ser un número mayor a CERO.'),
    ]

    @api.constrains('cn006_nivel_importancia')
    def _check_positive_value(self):
        for record in self:
            if record.cn006_nivel_importancia <= 0:
                raise ValidationError("El nivel de importancia debe ser un número mayor a CERO.")
