from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CN006TareaTipificacion(models.Model):
    _name = 'cn006.proyecto.tarea.tipificacion'
    _description = '(CN006) Tipificación de tareas'
    _order = 'cn006_orden ASC'


    cn006_orden = fields.Integer(string='Orden', required=True)
    name = fields.Char(string='Avance', required=True)
    cn006_descripcion = fields.Char(string='Descripción', required=False)

    
    _sql_constraints = [
        ('unique_cn006_tarea_tipificacion_orden', 'UNIQUE(cn006_orden)', 'El orden asignado debe ser único.'),
        ('positive_cn006_tarea_tipificacion_orden', 'CHECK(cn006_orden > 0)', 'El orden asignado debe ser un número mayor a CERO.'),
        ('unique_name_cn006_tarea_tipificacion_', 'UNIQUE(name)', 'La tipificación debe ser única.'),
    ]

    @api.constrains('orden')
    def _check_positive_value(self):
        for record in self:
            if record.cn006_orden <= 0:
                raise ValidationError("El orden asignado debe ser un número mayor a CERO.")
