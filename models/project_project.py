from odoo import models, fields

class ProjectProject(models.Model):
    _inherit = 'project.project'

    cn006_clasificacion_id     = fields.Many2one('cn006.proyecto.clasificacion',     string='Clasificación', help='Clasificación del proyecto según la categoría definida.')
    cn006_grado_avance_id      = fields.Many2one('cn006.proyecto.grado.avance',      string='Avance', help='Grado de avance del proyecto.')
    cn006_grado_complejidad_id = fields.Many2one('cn006.proyecto.grado.complejidad', string='Compejidad', help='Grado de complejidad del proyecto.')
    cn006_nivel_importancia_id = fields.Many2one('cn006.proyecto.nivel.importancia', string='Importancia', help='Nivel de importancia del proyecto.')
    cn006_nivel_urgencia_id    = fields.Many2one('cn006.proyecto.nivel.urgencia',    string='Urgencia', help='Nivel de urgencia del proyecto.')
    cn006_tamano_id            = fields.Many2one('cn006.proyecto.tamano',            string='Tamaño', help='Tamaño del proyecto.')

    # La fecha de creación del proyecto es la fecha calendario en la que se considerará que el proyecto 
    cn006_fecha_creacion = fields.Datetime(string='Fecha de Creación', default=fields.Datetime.now, required=True)


