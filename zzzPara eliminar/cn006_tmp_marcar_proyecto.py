import openpyxl
import logging
import sys
import ssl
import xmlrpc.client

from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


context = ssl._create_unverified_context()

# Credenciales de autenticación
_ambiente = "PROD"
if (_ambiente == "PROD"):
    url = 'https://canella.odoo.com'
    db = 'piensom-canella1-main-7955386'
    username = 'odoo_reportes@canella.com.gt'
    password = '2adb5989440eaad90ad2b706d69e311757d6d389'
    etapas_tareas = [564, 565, 566] 
    usuarios_cn006 = [195,294,312,445,2767,3198,3199,3200,3201,3202,3203,3204]
elif (_ambiente == "STAGE"):
    #url="https://canella-canellatest2-17948159.dev.odoo.com"
    db = 'canella-canellatest2-17948159' 
    username = 'odoo_reportes@canella.com.gt'
    password = '2adb5989440eaad90ad2b706d69e311757d6d389'
    etapas_tareas = [564,565,566] 
    usuarios_cn006 = [252,312]
#

# Conectar a Odoo
print("\n\n\n\n\n\n\n\n010 Conectando con odoo")
print("010 Conectando con odoo")
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url), context=context)
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url), context=context)

# Filtrar proyectos que contienen "(cn006)" en el nombre
try:
    print("020 Obteniendo proyectos con '(cn006)' en el nombre")


    # Luego, actualizamos el campo `cn006_project` a False en todos los proyectos encontrados
    #['display_name', 'ilike', 'cn006'],  # Filtra por display_name
    #['user_id', 'in', usuarios_cn006]
    proyectos = models.execute_kw(db, uid, password,
            'project.project', 'search_read',
                [
                    [['user_id', 'in', usuarios_cn006]]  # Filtra por user_id en la lista
                ],
                {'fields': ['id', 'cn006_project', 'name', 'display_name']}
            )

    if not proyectos:
        print("No se encontraron proyectos con '(cn006)' en el nombre")
    else:
        print(f"\nSe encontraron {len(proyectos)} proyectos con '(cn006)' en el nombre")
        print(f"Se encontraron {len(proyectos)} proyectos con '(cn006)' en el nombre")
        print(f"Se encontraron {len(proyectos)} proyectos con '(cn006)' en el nombre")
        print(f"Se encontraron {len(proyectos)} proyectos con '(cn006)' en el nombre")
        print(f"Se encontraron {len(proyectos)} proyectos con '(cn006)' en el nombre\n")

        for proyecto in proyectos:
            actualizar = proyecto['cn006_project'] != True

            #Actualizar cn006_project a True
            project_id = proyecto['id']
            if actualizar:
                print(f"Actualizando proyecto: {proyecto['name']} (ID: {project_id})")
                models.execute_kw(db, uid, password,
                      'project.project', 'write',
                      [[project_id], {'cn006_project': True}]
                  )
                print(f"Proyecto {proyecto} - actualizado y asignado a las etapas correctamente.")

                # # Asignar el proyecto a las etapas indicadas
                for etapa_id in etapas_tareas:
                    models.execute_kw(db, uid, password,
                        'project.task.type', 'write',
                        [[etapa_id], {'project_ids': [(4, project_id)]}]  # Agrega el proyecto sin duplicarlo
                    )

            

except Exception as e:
    print(f"Error al conectar o procesar los proyectos: {e}")
    sys.exit(1)

print("Proceso finalizado.")
