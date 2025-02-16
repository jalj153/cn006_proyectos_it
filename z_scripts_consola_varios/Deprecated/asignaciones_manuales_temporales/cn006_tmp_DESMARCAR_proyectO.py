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
print("\n\n\n\n010 Conectando con odoo")
logger.info("\n\n\n\n010 Conectando con odoo")
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url), context=context)
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url), context=context)

# Filtrar proyectos que contienen "(cn006)" en el nombre
try:

    logger.info("020 Obteniendo TODOS los proyectos con ")

    proyectos_ids = models.execute_kw(db, uid, password,
        'project.project', 'search',
        [[]]  # Sin condiciones para obtener todos los proyectos
    )

    logger.info("030 ACTUALIZANDO TODOS los proyectos con ")

    # Luego, actualizamos el campo `cn006_project` a False en todos los proyectos encontrados
    if proyectos_ids:
        models.execute_kw(db, uid, password,
            'project.project', 'write',
            [proyectos_ids, {'cn006_project': False}]
        )

    
    logger.info("040 FINALIZADO SE ACTUALIZARON TODOS los proyectos")
            

except Exception as e:
    logger.error(f"Error al conectar o procesar los proyectos: {e}")
    sys.exit(1)

logger.info("Proceso finalizado.")
