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
elif (_ambiente == "STAGE"):
    url = "https://canella-canellatest2-18823178.dev.odoo.com/"
    db = 'canella-canellatest2-18823178'
    username = 'odoo_reportes@canella.com.gt'
    password = '2adb5989440eaad90ad2b706d69e311757d6d389'


# Conectar a Odoo
print("\n\n\n\n\n\n\n\n010 Conectando con odoo")
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url), context=context)
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url), context=context)

# Filtrar etapas donde cn006_task_type = True y comparar diferencias en project_ids
try:
    print("020 Obteniendo etapas con 'cn006_task_type' = True")

    # Obtener las etapas donde cn006_task_type es True
    etapas_filtradas = models.execute_kw(db, uid, password,
        'project.task.type', 'search_read',
        [
             [('cn006_task_type', '=', True)] # Filtra por cn006_task_type = True
        ],
        {'fields': ['id', 'name', 'project_ids']}
    )

    print("030 regresé de la consulta a Odoo")

    if not etapas_filtradas:
        print("No se encontraron etapas con 'cn006_task_type' = True")
    else:
        print(f"\nSe encontraron {len(etapas_filtradas)} etapas con 'cn006_task_type' = True")

        # Paso 1: Mostrar información de las etapas filtradas
        for etapa in etapas_filtradas:
            print(f"Etapa: {etapa['name']} (ID: {etapa['id']})")
            print(f"Project IDs: {etapa['project_ids']}")

        # Paso 2: Comparar project_ids entre las etapas filtradas
        for i, etapa in enumerate(etapas_filtradas):
            for j, otra_etapa in enumerate(etapas_filtradas):
                if i < j:  # Comparar solo una vez por cada par
                    # Obtener project_ids de ambas etapas
                    etapa_project_ids = set(etapa['project_ids'])
                    otra_etapa_project_ids = set(otra_etapa['project_ids'])

                    # Verificar diferencias en project_ids entre las etapas
                    diferencia = etapa_project_ids.symmetric_difference(otra_etapa_project_ids)
                    if diferencia:
                        print(f"Diferencia en project_ids entre las etapas {etapa['name']} (ID: {etapa['id']}) y {otra_etapa['name']} (ID: {otra_etapa['id']}):")
                        print(f"Diferencia encontrada: {diferencia}")

except Exception as e:
    print(f"Error al conectar o procesar las etapas: {e}")
    sys.exit(1)

print("Proceso finalizado.")
