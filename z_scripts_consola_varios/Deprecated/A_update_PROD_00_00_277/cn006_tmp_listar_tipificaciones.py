import logging
import sys
import ssl
import xmlrpc.client

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
    # Obtener todas las clasificaciones de cn006.proyecto.tarea.tipificacion
    tipificaciones = models.execute_kw(
        db, uid, password,
        'cn006.proyecto.tarea.tipificacion', 'search_read',
        [],
        {'fields': ['id', 'display_name']}
    )

    if not tipificaciones:
        print("No se encontraron clasificaciones en cn006.proyecto.tarea.tipificacion.")
        sys.exit(0)

    # Mostrar resultados en pantalla
    print("\nListado de Clasificaciones:")
    for tipificacion in tipificaciones:
        print(f"ID: {tipificacion['id']}, Display Name: {tipificacion['display_name']}")

except Exception as e:
    print(f"Error al obtener clasificaciones: {e}")
    sys.exit(1)

print("Proceso finalizado.")
