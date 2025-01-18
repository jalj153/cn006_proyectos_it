# -*- coding: utf-8 -*-
# .\__manifest__.py

# ***************************************************************************
# ***************************************************************************

{
    'name': '(CN006) Gestión Proyectos IT',
    'version': '00.00.005',
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
            
        # datos / cron
            
        # Orden Menú:  Vistas > Acciones > Menú
            # Vistas
                
            # Acciones
                'views/zzzcn006_menu_actions_dummy.xml',
            # Menú
                'views/cn006_menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

