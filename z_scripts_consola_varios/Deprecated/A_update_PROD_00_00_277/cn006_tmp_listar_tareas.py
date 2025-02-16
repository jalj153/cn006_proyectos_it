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
if _ambiente == "PROD":
    url = 'https://canella.odoo.com'
    db = 'piensom-canella1-main-7955386'
    username = 'odoo_reportes@canella.com.gt'
    password = '2adb5989440eaad90ad2b706d69e311757d6d389'
elif _ambiente == "STAGE":
    db = 'canella-canellatest2-17948159'
    username = 'odoo_reportes@canella.com.gt'
    password = '2adb5989440eaad90ad2b706d69e311757d6d389'

# Conectar a Odoo
print("\n\n010 Conectando con Odoo...")
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", context=context)
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", context=context)

if not uid:
    print("Error: No se pudo autenticar con Odoo")
    sys.exit(1)

try:
    # Obtener proyectos donde cn006_project = True
    project_ids = models.execute_kw(
        db, uid, password,
        'project.project', 'search_read',
        [[('cn006_project', '=', True)]],
        {'fields': ['id', 'name', 'cn006_project']}
    )

    if not project_ids:
        print("No se encontraron proyectos con cn006_project = True.")
        sys.exit(0)

    # Obtener todas las tareas de esos proyectos
    project_ids_list = [proj['id'] for proj in project_ids]

    task_ids = models.execute_kw(
        db, uid, password,
        'project.task', 'search_read',
        [[('project_id', 'in', project_ids_list)]],
        {'fields': ['id', 'name', 'project_id', 'stage_id']}
    )

    # Crear archivo Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Tareas CN006"
    
    # Escribir encabezados
    headers = ["ID Proyecto", "Nombre Proyecto", "cn006_project", "ID Task", "Nombre Task", "ID Task Type", "Task Type"]
    ws.append(headers)

    # Mapear IDs de proyectos y etapas a nombres
    project_map = {p['id']: (p['name'], p['cn006_project']) for p in project_ids}
    stage_map = {}

    # Obtener los nombres de las etapas de tarea
    stage_ids_list = list(set(t['stage_id'][0] for t in task_ids if t['stage_id']))
    if stage_ids_list:
        stage_data = models.execute_kw(
            db, uid, password,
            'project.task.type', 'search_read',
            [[('id', 'in', stage_ids_list)]],
            {'fields': ['id', 'name']}
        )
        stage_map = {s['id']: s['name'] for s in stage_data}

    # Llenar datos en el Excel
    for task in task_ids:
        project_info = project_map.get(task['project_id'][0], ("Desconocido", False))
        stage_info = stage_map.get(task['stage_id'][0], "Desconocido") if task['stage_id'] else "Desconocido"
        
        ws.append([
            task['project_id'][0],  # ID Proyecto
            project_info[0],        # Nombre Proyecto
            project_info[1],        # cn006_project
            task['id'],             # ID Task
            task['name'],           # Nombre Task
            task['stage_id'][0] if task['stage_id'] else "",  # ID Task Type
            stage_info              # Task Type
        ])

    # Guardar archivo
    excel_filename = "cn006_tmp_listar_tareas_cn006.xlsx"
    wb.save(excel_filename)
    print(f"Archivo generado: {excel_filename}")

except Exception as e:
    print(f"Error al conectar o procesar los proyectos: {e}")
    sys.exit(1)

print("Proceso finalizado.")
