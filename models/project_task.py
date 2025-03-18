from odoo import models, fields, api
import datetime


import logging

_logger = logging.getLogger("CN006")
class ProjectTask(models.Model):
    _inherit = 'project.task'

    cn006_grado_avance_id   = fields.Many2one('cn006.proyecto.tarea.grado.avance', string='Grado Avance', help='Grado de avance de la tarea.')
    cn006_es_implementacion = fields.Boolean(string="Es Implementación", compute="_compute_cn006_es_implementacion", store=True)
    cn006_tipificacion_id   = fields.Many2one('cn006.proyecto.tarea.tipificacion', string='Tipo Tarea', help='Clasificación de tareas para agrupación de horas.')
    cn006_tipo_soporte_id   = fields.Many2one('cn006.proyecto.tarea.tipo.soporte', string='Tipo Soporte Asociado', help='Si la tarea es IMPLEMENTACIÓN se debe seleccionar la incidencia')


    
    def name_get(self):
        result = []
        for task in self:
            # Convertir ID a cadena y separar cada 3 dígitos con comas
            formatted_id = "{:,}".format(task.id)
            
            # Crear el nombre con el formato deseado
            name = f"({formatted_id}) {task.name}"  # Esto debería mostrar el ID correctamente formateado
           
            result.append((task.id, name))
        return result
    
    @api.model
    def create(self, vals):
        task = super(ProjectTask, self).create(vals)
        task._assign_deadline_if_needed()
        return task

        
    

    def _read_group_stage_ids(self, stages, domain, order):
        """Carga todas las etapas en Kanban solo para CN006, manteniendo el comportamiento normal en otros casos."""
        
        # Extraer el contexto para verificar si estamos en CN006
        is_cn006 = self._context.get("cn006_mode", False)

        if is_cn006:
            # Aplicar el filtro solo si estamos en el módulo CN006
            return self.env['project.task.type'].search([('cn006_task_type', '=', True)])

        # Si no estamos en CN006, devolver el comportamiento normal de Odoo

        if ('cn006_task_type', '=', False) not in domain:
            domain.append(('cn006_task_type', '=', False))

        return super()._read_group_stage_ids(stages, domain, order)

    @api.constrains('stage_id')  # Se ejecuta solo cuando cambia la etapa
    def _assign_deadline_if_needed(self):
        for task in self:
            if not task.project_id.cn006_project:
                return

            # Si la etapa es "Backlog", eliminar la fecha de vencimiento
            if task.stage_id == self.env.ref('cn006_proyectos_it.cn006_task_type_avance000'):
                task.date_deadline = False  # Usar False en lugar de ""
                return  

            # Si la etapa es "ESTA SEMANA" y no tiene fecha, asignar la fecha
            if not task.date_deadline:
                today = datetime.date.today()
                weekday = today.weekday()

                if weekday in (5, 6):  # Sábado (5) o Domingo (6)
                    days_since_friday = weekday - 4  
                    friday_date = today - datetime.timedelta(days=days_since_friday)  
                else:
                    days_until_friday = (4 - weekday + 7) % 7  
                    friday_date = today + datetime.timedelta(days=days_until_friday)

                task.date_deadline = friday_date

    @api.depends('cn006_tipificacion_id')
    def _compute_cn006_es_implementacion(self):
        _logger.info(f"(cn006) Recalculado creo que es poque se grabó el registro.")
        try:
            implementacion_id = self.env.ref('cn006_proyectos_it.cn006_proyecto_tarea_tipificacion_30').id
        except ValueError:
            implementacion_id = False

        for record in self:
            record.cn006_es_implementacion = record.cn006_tipificacion_id.id == implementacion_id

    @api.onchange('cn006_tipificacion_id')
    def _onchange_cn006_tipificacion_id(self):
        _logger.info(f"(cn006) Detecté un cambio.  voy a actualizar valor de cn006_es_implementacion ({self.cn006_es_implementacion})")
        for record in self:
            record._compute_cn006_es_implementacion()
        _logger.info(f"(cn006) Ya realicé el cambio.  Valor de cn006_es_implementacion ({self.cn006_es_implementacion})")
        _logger.info(f"(cn006) Ya realicé el cambio.  Valor de record ({record.cn006_es_implementacion})")


