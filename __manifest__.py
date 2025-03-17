# -*- coding: utf-8 -*-
# .\__manifest__.py

# ***************************************************************************
# Grupo: (cn006_proyectos_it_usuarios) : (CN006) Usuarios Proyectos IT
#   id = 191
#   Está quemado en código porque Odoo no puede resolver la referencia
# ***************************************************************************

{
    'name': '(CN006) Gestión Proyectos IT',
    'version': '00.00.339',
    'summary': '(CN006) Gestión Proyectos IT',
    'description': '(CN006) Gestión de proyectos del área de IT',
    'author': 'Neotropo®',
    'license': 'Other proprietary',
    'website': 'https://www.neotropo.com/odoo_dev',
    'category': 'Project',
    'icon': '/cn006_proyectos_it/static/description/icon.png',
    'depends': ['base','project','hr_timesheet'],
    'data': [
        # Definición de la seguridad
            'security/cn006_security.xml',
            'security/ir.model.access.csv',
        
            #'views/cn006_project_project_view_form_simplified.xml',
            'views/cn006_project_project_view_form.xml',
            #'views/cn006_menu_actions_special.xml',
        # datos
            'data/cn006_proyecto_clasificacion.xml',
            'data/cn006_proyecto_grado_complejidad.xml',
            'data/cn006_proyecto_nivel_importancia.xml',
            'data/cn006_proyecto_nivel_urgencia.xml',
            'data/cn006_proyecto_stage.xml',
            'data/cn006_proyecto_tamano.xml',
            'data/cn006_proyecto_task_type.xml',
            'data/cn006_proyecto_tipo.xml',
            'data/cn006_tarea_grado_avance.xml',
            'data/cn006_tarea_tipificacion.xml',
            'data/cn006_tarea_tipo_soporte.xml',
        # Orden Menú:  Vistas > Acciones > Menú
            # Vistas
                'views/cn006_project_project_view_kanban_filter.xml',
                'views/cn006_project_project_view_kanban_tasks.xml',
                'views/cn006_project_project_view_kanban.xml',

                'views/cn006_project_project_view_tree.xml',
                'views/cn006_project_task_view_form.xml',
                'views/cn006_project_task_view_kanban_filter.xml',
                'views/cn006_project_task_view_kanban.xml',

                'views/cn006_proyecto_clasificacion_views.xml',
                'views/cn006_proyecto_stage_tree.xml',
                'views/cn006_proyecto_task_type_tree.xml',
                
            # Acciones
                'views/cn006_menu_actions.xml',
                'views/zzzcn006_menu_actions_dummy.xml',
            # Menú
                'views/cn006_menu.xml',
        
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

