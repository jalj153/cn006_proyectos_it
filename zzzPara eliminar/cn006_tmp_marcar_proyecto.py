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
_ambiente = "STAGE"
if (_ambiente == "PROD"):
    #url = 'https://canella.odoo.com'
    db = 'piensom-canella1-main-7955386'
    username = 'odoo_reportes@canella.com.gt'
    password = '2adb5989440eaad90ad2b706d69e311757d6d389'
elif (_ambiente == "STAGE"):
    url="https://canella-canellatest2-17948159.dev.odoo.com"
    db = 'canella-canellatest2-17948159' 
    username = 'odoo_reportes@canella.com.gt'
    password = '2adb5989440eaad90ad2b706d69e311757d6d389'

#

# Conectar a Odoo
print("010 Conectando con odoo")
logger.info("010 Conectando con odoo")
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url), context=context)
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url), context=context)

# Filtrar proyectos que contienen "(cn006)" en el nombre
try:
    logger.info("020 Obteniendo proyectos con '(cn006)' en el nombre")
    proyectos = models.execute_kw(db, uid, password,
        'project.project', 'search_read',
        [[['name', 'ilike', '(cn006)']]],
        {'fields': ['id', 'name']}
    )

    if not proyectos:
        logger.info("No se encontraron proyectos con '(cn006)' en el nombre")
    else:
        logger.info(f"Se encontraron {len(proyectos)} proyectos con '(cn006)' en el nombre")
        # Actualizar el campo cn006_project = True para cada proyecto
        for proyecto in proyectos:
            project_id = proyecto['id']
            logger.info(f"Actualizando proyecto: {proyecto['name']} (ID: {project_id})")
            models.execute_kw(db, uid, password,
                'project.project', 'write',
                [[project_id], {'cn006_project': True}]
            )
            logger.info(f"Proyecto {proyecto['name']} actualizado correctamente.")

except Exception as e:
    logger.error(f"Error al conectar o procesar los proyectos: {e}")
    sys.exit(1)

logger.info("Proceso finalizado.")
