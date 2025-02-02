import logging
from odoo import models, fields

_logger = logging.getLogger(__name__)

class ProjectProject(models.Model):
    _inherit = 'project.project'

    #region Campos relacionados
    cn006_clasificacion_id     = fields.Many2one('cn006.proyecto.clasificacion',     string='Clasificación', help='Clasificación del proyecto según la categoría definida.')
    cn006_grado_complejidad_id = fields.Many2one('cn006.proyecto.grado.complejidad', string='Grado Compejidad', help='Grado de complejidad del proyecto.')
    cn006_nivel_importancia_id = fields.Many2one('cn006.proyecto.nivel.importancia', string='Importancia', help='Nivel de importancia del proyecto.')
    cn006_nivel_urgencia_id    = fields.Many2one('cn006.proyecto.nivel.urgencia',    string='Urgencia', help='Nivel de urgencia del proyecto.')
    cn006_tamano_id            = fields.Many2one('cn006.proyecto.tamano',            string='Tamaño', help='Tamaño del proyecto.')
    #endregion Campos relacionados

    cn006_project   = fields.Boolean(required=False, string='Proyecto Marcado (CN006)', help='Permite filtrar los proyectos asociados al módulo', default=False)
    cn006_emergente = fields.Boolean(required=False, string='¿Es emergente?',           help='Determinar el grupo de gestión del proyecto', default=False)

    #region Fechas del Proyecto
    """ 
        SECCIÓN DE FECHAS
        Típicamente una fecha tendrá variantes, el mismo significado pero con variantes
            _estimada: Fecha que se estimó para finalización (ya sea por el responsable del proyecto o Informática)
            _sistema : Es la fecha real cuando fue grabada en Odoo.  Importantes para ver la diferencia entre "el suceso real" y "la grabación al sistema"
            _oficial : La fecha que se considerará para efectos de estadísticas y reportes
    """
    #endregion Fechas del Proyecto

    cn006_fecha_creacion_sistema = fields.Date(required=True,  string='(SIS) Fecha Creación', help='Fecha en que se grabó el proyecto en el sistema', default=fields.Date.context_today)
    cn006_fecha_creacion_oficial = fields.Date(required=False, string='Fecha Creación'     , help='Fecha en que se gestó el proyecto.')

    cn006_fecha_inicio_oficial = fields.Date(required=False, string='Fecha Inicio'      , help='Fecha en que iniciaron trabajos en el proyecto.  El proyecto empezó a comsumir horas.')
    cn006_fecha_inicio_sistema = fields.Date(required=False, string='(SIS) Fecha Inicio', help='Fecha en que actualizó el proyecto - Fecha en que iniciaron trabajos en el proyecto.  El proyecto empezó a comsumir horas.')

    cn006_fecha_entrega_informatica_estimada = fields.Date(required=False, string='Fecha Entrega a Informática'            , help='Fecha en que el responsable (interno externo) debe entregar a Informática')
    cn006_fecha_entrega_informatica_oficial  = fields.Date(required=False, string='Fecha Real Entrega a Informática'       , help='Fecha en que el responsable (interno externo) realmente entregó a Informática')
    cn006_fecha_entrega_informatica_sistema  = fields.Date(required=False, string='(SIS) Fecha Entrega Real a Informática' , help='Fecha en que se actualizó el proyecto - Fecha en que el responsable (interno externo) realmente entregó a Informática')

    cn006_fecha_entrega_usuario_estimada = fields.Date(required=False, string='Fecha Entrega a Usuario'            , help='Fecha en que se debe entregar a usuario')
    cn006_fecha_entrega_usuario_oficial  = fields.Date(required=False, string='Fecha Real Entrega a Usuario'       , help='Fecha en que realmente se entregó a usuario')
    cn006_fecha_entrega_usuario_sistema  = fields.Date(required=False, string='(SIS) Fecha Real Entrega a Usuario' , help='Fecha en que se actualizó el proyecto - Fecha en que realmente se entregó a usuario')

    cn006_fecha_cierre_estimada = fields.Date(required=False, string='Fecha cierre'           , help='Fecha en que se estima cerrar el proyecto')
    cn006_fecha_cierre_oficial  = fields.Date(required=False, string='Fecha Real cierre'      , help='Fecha en que realmente se cerró el proyecto')
    cn006_fecha_cierre_sistema  = fields.Date(required=False, string='(SIS) Fecha Real cierre', help='Fecha en que se actualizó el proyecto - Fecha en que realmente se cerró el proyecto')

#region Métodos para Acciones de Kanban Dashboard   
#   Estos métodos se llaman desde el kanban view inicial del módulo CN004
#   No tiene sentido llamarlos desde otros módulos
#   No se valida que están en módulo CN004 porque el nombre debe evitar llamadas no requeridas
# 
    def cn006_method_view_project_tasks(self, **kwargs):
        # Validar y forzar que venga solamente 1 registro
        self.ensure_one()  

        # Obtener la acción creada por el módulo
        _logger.info(f"(cn006) Tomando la acción")
        action = self.env.ref('cn006_proyectos_it.cn006_action_project_task_view_kanban').read()[0]
                               

        _logger.info(f"(cn006) Ya se tiene la acción \n***********\n\n{action}\n***********\n\n")
        
        if not isinstance(action, dict):
            raise TypeError(f"El valor de 'action' no es un diccionario. Es de tipo: {type(action)}\n  valor: {action}")
        
        return action  #cn006_method_view_project_tasks
#endregion Métodos para Acciones de Kanban Dashboard   
