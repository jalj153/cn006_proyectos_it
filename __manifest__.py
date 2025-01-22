# -*- coding: utf-8 -*-
# .\__manifest__.py

# ***************************************************************************
# ***************************************************************************

{
    'name': '(CN006) Gestión Proyectos IT',
    'version': '00.00.064',
    'summary': '(CN006) Gestión Proyectos IT',
    'description': '(CN006) Gestión de proyectos del área de IT',
    'author': 'Neotropo®',
    'license': 'Other proprietary',
    'website': 'https://www.neotropo.com',
    'category': 'Project',
    'icon': '/cn006_proyectos_it/static/description/icon.png',
    'depends': ['base','project','hr_timesheet'],
    'data': [
        # Código especial que no necesita referencia en el manifest


        # Definición de la seguridad
            'security/cn006_security.xml',
            
        
        # Orden Menú:  Vistas > Acciones > Menú
            # Vistas
                'views/cn006_project_project_view_form.xml',
                'views/cn006_project_project_view_kanban.xml',
                'views/cn006_project_task_view_form.xml',
            # Acciones
                'views/cn006_menu_actions.xml',
                'views/zzzcn006_menu_actions_dummy.xml',
            # Menú
                'views/cn006_menu.xml',

        # datos / cron
            # 'data/cn006_proyecto_clasificacion.csv',
            # 'data/cn006_proyecto_grado_avance.csv',
            # 'data/cn006_proyecto_grado_complejidad.csv',
            # 'data/cn006_proyecto_nivel_importancia.csv',
            # 'data/cn006_proyecto_nivel_urgencia.csv',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

