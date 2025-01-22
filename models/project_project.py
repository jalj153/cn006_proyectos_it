from odoo import models, fields

class ProjectProject(models.Model):
    _inherit = 'project.project'

    cn006_clasificacion_id     = fields.Many2one('cn006.proyecto.clasificacion',     string='Clasificación', help='Clasificación del proyecto según la categoría definida.')
    cn006_grado_avance_id      = fields.Many2one('cn006.proyecto.grado.avance',      string='Avance', help='Grado de avance del proyecto.')
    cn006_grado_complejidad_id = fields.Many2one('cn006.proyecto.grado.complejidad', string='Compejidad', help='Grado de complejidad del proyecto.')
    cn006_nivel_importancia_id = fields.Many2one('cn006.proyecto.nivel.importancia', string='Importancia', help='Nivel de importancia del proyecto.')
    cn006_nivel_urgencia_id    = fields.Many2one('cn006.proyecto.nivel.urgencia',    string='Urgencia', help='Nivel de urgencia del proyecto.')
    cn006_tamano_id            = fields.Many2one('cn006.proyecto.tamano',            string='Tamaño', help='Tamaño del proyecto.')

    #region Fechas del Proyecto
    """ 
        SECCIÓN DE FECHAS
        Típicamente una fecha tendrá variantes, el mismo significado pero con variantes
            _estimada: Fecha que se estimó para finalización (ya sea por el responsable del proyecto o Informática)
            _sistema : Es la fecha real cuando fue grabada en Odoo.  Importantes para ver la diferencia entre "el suceso real" y "la grabación al sistema"
            _oficial : La fecha que se considerará para efectos de estadísticas y reportes
    """
    #endregion Fechas del Proyecto

    cn006_fecha_creacion_sistema = fields.Datetime(required=True, string='(SIS) Fecha Creación', help='Fecha en que se grabó el proyecto en el sistema', default=fields.Datetime.now)
    cn006_fecha_creacion_oficial = fields.Datetime(required=False, string='Fecha Creación'     , help='Fecha en que se gestó el proyecto.')

    cn006_fecha_inicio_oficial = fields.Datetime(required=False, string='Fecha Inicio'      , help='Fecha en que iniciaron trabajos en el proyecto.  El proyecto empezó a comsumir horas.')
    cn006_fecha_inicio_sistema = fields.Datetime(required=False, string='(SIS) Fecha Inicio', help='Fecha en que actualizó el proyecto - Fecha en que iniciaron trabajos en el proyecto.  El proyecto empezó a comsumir horas.')

    cn006_fecha_entrega_informatica_estimada = fields.Datetime(required=False, string='Fecha Entrega a Informática'            , help='Fecha en que el responsable (interno externo) debe entregar a Informática')
    cn006_fecha_entrega_informatica_oficial  = fields.Datetime(required=False, string='Fecha Real Entrega a Informática'       , help='Fecha en que el responsable (interno externo) realmente entregó a Informática')
    cn006_fecha_entrega_informatica_sistema  = fields.Datetime(required=False, string='(SIS) Fecha Entrega Real a Informática' , help='Fecha en que se actualizó el proyecto - Fecha en que el responsable (interno externo) realmente entregó a Informática')

    cn006_fecha_entrega_usuario_estimada = fields.Datetime(required=False, string='Fecha Entrega a Usuario'            , help='Fecha en que se debe entregar a usuario')
    cn006_fecha_entrega_usuario_oficial  = fields.Datetime(required=False, string='Fecha Real Entrega a Usuario'       , help='Fecha en que realmente se entregó a usuario')
    cn006_fecha_entrega_usuario_sistema  = fields.Datetime(required=False, string='(SIS) Fecha Real Entrega a Usuario' , help='Fecha en que se actualizó el proyecto - Fecha en que realmente se entregó a usuario')

    cn006_fecha_cierre_estimada = fields.Datetime(required=False, string='Fecha cierre'           , help='Fecha en que se estima cerrar el proyecto')
    cn006_fecha_cierre_oficial  = fields.Datetime(required=False, string='Fecha Real cierre'      , help='Fecha en que realmente se cerró el proyecto')
    cn006_fecha_cierre_sistema  = fields.Datetime(required=False, string='(SIS) Fecha Real cierre', help='Fecha en que se actualizó el proyecto - Fecha en que realmente se cerró el proyecto')


