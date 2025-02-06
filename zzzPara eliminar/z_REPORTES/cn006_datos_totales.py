import xmlrpc.client
import json
import argparse
import pytz
from datetime import datetime
from collections import defaultdict
import codecs
from cNT_odoo_autenticar import cNT_odoo_autenticar 

#region EXPLICACIÓN DEL PROCESO
"""  ******* EXPLICACIÓN DEL PROCESO
    1. Obtiene todos los tickets con los siguientes criterios:
        1.1. En el rango de fecha_desde y fecha_hasta 
        1.2. Compañía = 1  (Canella) y (Equipo = 35)
        1.3. Se agregan los tickets que tengan partes de horas en el rango de fechas
    2. Agrega los datos de los partes de horas en el rango de fechas
    3. Realiza cálculos previos de tiempo abierto
    4. Los registros en este punto se duplican cuando hay más de un parte de horas asociado
    5. Se crea el resumen de tickets consolidando los partes de horas
    6. Se formatea la información
************************************************************************  """
#endregion

#region VERSIONAMIENTO
"""******* VERSIONAMIENTO
# v160
#   Funcionamiento correcto del script como se explica en EXPLICACIÓN DEL PROCESO
************************************************************************  """
#endregion

################################################################################################################
# Datos globales
################################################################################################################
#region VARIABLES GLOBALES
g_todo_ok = True
g_datos_conexion = {}
g_msj = ""
g_debug = False

# grupos de CN003 ADM, SUPERVISORES, AGENTES, USUARIOS
# cn003_group_ids = [170, 171, 172, 173]
#endregion

################################################################################################################
# Métodos de aplicación general
################################################################################################################

def asigna_error (p_msj: str):
    global g_todo_ok, g_datos_conexion, g_msj, g_debug

    if g_debug:
        print(f"\n*** Voy a asignar error:\n")
        print(f"Este es el mensaje que recibo: ***{p_msj}***")

    g_todo_ok = False
    g_msj = p_msj
    g_datos_conexion = {}  
    return  

def clean_newlines(record):
    global g_todo_ok, g_datos_conexion, g_msj, g_debug
    for key in record:
        if isinstance(record[key], str):
            record[key] = record[key].replace('\n', ' ** ')
    return record

def str2bool(v):
    global g_todo_ok, g_datos_conexion, g_msj, g_debug
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1','verdadero','v','si'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0','falso','f'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

################################################################################################################
# Extracción de información
################################################################################################################
def autenticar_odoo (pURL, pDB, pUserName, pPassword): 
    global g_todo_ok, g_datos_conexion, g_msj, g_debug

    if g_debug:
            print(f"\nIniciando autenticar_odoo ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})")

    autenticador = cNT_odoo_autenticar(pURL, pDB, pUserName, pPassword)
    g_todo_ok, g_datos_conexion, g_msj = autenticador.conectar_odoo()

    if g_debug:
        if g_todo_ok:
            print(f"Autenticación exitosa ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})")
        else:
            print(f"Hubo un error al autenticar ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})")

        print(f"\nFinalizado autenticar_odoo\nDatos de autenticación:\n{g_datos_conexion}")
    return

def convertir_gtc_a_utc (p_fecha, p_tipo):
    global g_todo_ok, datos_conexion, msj

    if g_debug:
        print(f"\nIniciando convertir_gtc_a_utc p_fecha: {p_fecha} p_tipo: {p_tipo}")

    guatemala_tz = pytz.timezone('America/Guatemala')
    utc_tz = pytz.utc
    
    p_tipo = p_tipo.upper()

    if len(p_fecha) == 10:
        if p_tipo == "INI":
            p_fecha = datetime.strptime(p_fecha + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
        else:
            p_fecha = datetime.strptime(p_fecha + ' 23:59:59', '%Y-%m-%d %H:%M:%S')



    p_fecha = guatemala_tz.localize(p_fecha)
    p_fecha = p_fecha.astimezone(utc_tz)

    if g_debug:
        print(f"\nFinalizado convertir_gtc_a_utc p_fecha: {p_fecha} p_tipo: {p_tipo}")

    return p_fecha

def obtener_tickets (p_fecha_desde, p_fecha_hasta):
    global g_todo_ok, g_datos_conexion, g_msj, g_debug

    if g_debug:
            print(f"\nInciando proceso obtener_tickets.  p_fecha_desde: {p_fecha_desde}  p_fecha_hasta: {p_fecha_hasta} ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})")

    # Datos para conexión a modelo de datos
    uid = g_datos_conexion['uid']
    url = g_datos_conexion['odoo_url']
    db = g_datos_conexion['db_name']
    password = g_datos_conexion['password']

    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    tickets = models.execute_kw(db, uid, password, 'helpdesk.ticket', 'search_read',
        [[
            ['cn003_fecha_apertura_reporte', '>=', p_fecha_desde],
            ['cn003_fecha_apertura_reporte', '<=', p_fecha_hasta],
            ['company_id', '=', 1],
            ['team_id', '=', 35],
        ]],
        {'fields': 
            [
                'ticket_ref', 'team_id',    'partner_id', 'user_id',  'name_company','canal_atencion_id'
                , 'clasificacion_tipo_soporte_id','clasificacion_aplicacion_id', 'clasificacion_modulo_id', 'clasificacion_proyecto_id'
                ,'cn003_fecha_apertura', 'cn003_fecha_apertura_flag','cn003_fecha_apertura_manual', 'cn003_fecha_apertura_reporte', 'cn003_fecha_cierre', 'cn003_fecha_cierre_flag','cn003_fecha_cierre_manual', 'cn003_fecha_cierre_ofrecida', 'cn003_fecha_cierre_reporte'
                ,'create_date', '__last_update', 'write_date' 
                , 'company_id', 'create_uid', 'description','id','kanban_state','kanban_state_label','name', 'name_company'
                ,'partner_id','partner_name','priority', 'stage_id', 'stage_fold', 'timesheet_ids'
                , 'tipo_cierre_id', 'tipo_cierre_descripcion'
                , 'user_id'
                ,'vhur_correo_electronico', 'vhur_departamento_nombre', 'vhur_empresa_nombre'
            ]
        }
    )

    if g_debug:
            #print(f"Fin proceso obtener_tickets.  Detallando los datos:\n\n")
            #for ticket in tickets:
            #    print(f"*** ticket: {ticket} ***\n")
            print(f"\n\nFin de datos obtener tickets. ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})")

    return tickets

def obtener_tickets_2(p_fecha_desde, p_fecha_hasta,p_fecha_desde_ph, p_fecha_hasta_ph):
    global g_todo_ok, g_datos_conexion, g_msj, g_debug

    if g_debug:
        print(f"\nIniciando proceso obtener_tickets.  p_fecha_desde: {p_fecha_desde}  p_fecha_hasta: {p_fecha_hasta}  Control: ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")

    # Datos para conexión a modelo de datos
    uid = g_datos_conexion['uid']
    url = g_datos_conexion['odoo_url']
    db = g_datos_conexion['db_name']
    password = g_datos_conexion['password']

    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    # Buscar partes de horas que coincidan con los criterios
    partes_horas = models.execute_kw(db, uid, password, 'account.analytic.line', 'search_read',
        [[
            ['date', '>=', p_fecha_desde_ph],
            ['date', '<=', p_fecha_hasta_ph],
            ['company_id', '=', 1],
        ]],
        {'fields': ['id','date' ,'helpdesk_ticket_id']}
    )

    if g_debug:
        print(f"Estos son los partesde horas adicionales")
        for ph in partes_horas:
            print(f"ph {ph}")

    # Extraer ticket_ids únicos de partes de horas
    ticket_ids_adicionales = list(set(ph['helpdesk_ticket_id'][0] for ph in partes_horas if ph.get('helpdesk_ticket_id')))
    
    # Consultar los tickets originales más los adicionales
    tickets = models.execute_kw(db, uid, password, 'helpdesk.ticket', 'search_read',
        [[
            '|',
            ['id', 'in', ticket_ids_adicionales],
            '&',
            ['cn003_fecha_apertura_reporte', '>=', p_fecha_desde],
            ['cn003_fecha_apertura_reporte', '<=', p_fecha_hasta],
            ['company_id', '=', 1],
            ['team_id', '=', 35]
        ]],
        {'fields': 
            [
                'ticket_ref', 'team_id', 'partner_id', 'user_id', 'name_company','canal_atencion_id',
                'clasificacion_tipo_soporte_id', 'clasificacion_aplicacion_id', 'clasificacion_modulo_id',
                'clasificacion_proyecto_id', 'cn003_fecha_apertura', 'cn003_fecha_apertura_flag',
                'cn003_fecha_apertura_manual', 'cn003_fecha_apertura_reporte', 'cn003_fecha_cierre',
                'cn003_fecha_cierre_flag', 'cn003_fecha_cierre_manual', 'cn003_fecha_cierre_ofrecida',
                'cn003_fecha_cierre_reporte', 'create_date', '__last_update', 'write_date', 'company_id',
                'create_uid', 'description', 'id', 'kanban_state', 'kanban_state_label', 'name', 'name_company',
                'partner_id', 'partner_name', 'priority', 'stage_id', 'stage_fold', 'timesheet_ids',
                'tipo_cierre_id', 'tipo_cierre_descripcion', 'user_id', 'vhur_correo_electronico',
                'vhur_departamento_nombre', 'vhur_empresa_nombre'
            ],
            'order': 'id ASC'
        }
    )

    if g_debug:
        print(f"\n\nFin de datos obtener tickets. ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")

    return tickets

def calcular_tiempo_abierto (p_tickets):
    global g_todo_ok, g_datos_conexion, g_msj, g_debug

    if g_debug:
        print(f"Iniciando calcular_tiempo_abierto  ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})\n")

    # CAMBIO la diferencia de tiempo es con las varibles apertura_reporte y cierre_reporte
    #fecha_tmp = datetime.strptime("2024-08-31 12:00:00", "%Y-%m-%d %H:%M:%S")
    tiempo_dif = ""
    for ticket in p_tickets:
        #create_date = datetime.strptime(ticket['create_date'], "%Y-%m-%d %H:%M:%S")
        #tiempo_abierto_timedelta = fecha_tmp - create_date
        if (ticket["cn003_fecha_cierre_reporte"]):
            tmp_fecha = ticket["cn003_fecha_cierre_reporte"]
        else:
            tmp_fecha = ticket["create_date"]

        tiempo_abierto_timedelta = datetime.strptime(tmp_fecha, "%Y-%m-%d %H:%M:%S") - datetime.strptime(ticket["cn003_fecha_apertura_reporte"], "%Y-%m-%d %H:%M:%S")    
        tiempo_abierto_segundos = tiempo_abierto_timedelta.total_seconds()/86400*24

        ticket['fecha_operacion'] =  datetime.strptime(ticket['create_date'], "%Y-%m-%d %H:%M:%S").date().isoformat()
        ticket['tiempo_abierto_segundos'] = tiempo_abierto_segundos
        ticket['tiempo_abierto_formato'] = abs(tiempo_abierto_segundos/24)
        ticket['tiempo_abierto'] = tiempo_abierto_segundos

    if g_debug:
        print(f"Finalizado calcular_tiempo_abierto  ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})\n")
        # print(f"\nEstos son los datos con tiempo abierto \n")
        # for ticket in p_tickets:
        #     print(f"*** {ticket} ***")
        # print(f"\n\nFin de datos calcular_tiempo_abierto")

    return p_tickets

# region Parte Horas Bloque
def agregar_partes_horas_por_lotes(p_tickets,p_fecha_desde, p_fecha_hasta):
    global g_todo_ok, g_datos_conexion, g_msj, g_debug

    if g_debug:
        print(f"******   \nIniciando agregar_partes_horas_por_lotes  ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})\n***")
        print(f"Por procesar {len(p_tickets)} registros\n") 

    # Datos para conexión a modelo de datos
    uid = g_datos_conexion['uid']
    url = g_datos_conexion['odoo_url']
    db = g_datos_conexion['db_name']
    password = g_datos_conexion['password']

    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    tickets_timesheets = []
    all_timesheet_ids = []

    # Recopilar todos los IDs de partes de horas de los tickets
    for ticket in p_tickets:
        timesheet_ids = ticket.get('timesheet_ids', [])
        all_timesheet_ids.extend(timesheet_ids)

    # Obtener detalles de partes de horas en bloques
    timesheets = tickets_timesheets_bloque(models, db, uid, password, all_timesheet_ids, p_fecha_desde, p_fecha_hasta)

    # Crear un diccionario para mapear timesheet_id a sus detalles
    timesheets_dict = {timesheet['id']: timesheet for timesheet in timesheets}

    # Procesar los tickets con los detalles de los partes de horas obtenidos
    contador = 0
    for ticket in p_tickets:
        contador += 1
        #if g_debug:
        #    print(f"   * Procesando contador: {contador}   ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})")

        timesheet_ids = ticket.get('timesheet_ids', [])

        if not timesheet_ids:
            # Si no hay partes de horas, agregar el ticket tal cual
            ticket['timesheet_user_id'] = ""
            ticket['timesheet_user_name'] = ""
            ticket['tiempo_abierto'] = 0  # Ajustar el campo tiempo_abierto
            tickets_timesheets.append(ticket)
        else:
            # Iterar sobre los IDs de partes de horas y crear registros de tickets con partes de horas
            for i, timesheet_id in enumerate(timesheet_ids):
                timesheet = timesheets_dict.get(timesheet_id)
                if timesheet:
                    ticket_with_timesheet = ticket.copy()
                    ticket_with_timesheet['unit_amount_60'] = 0.00

                    if timesheet.get('user_id'):
                        tmp_user_id = timesheet['user_id'][0]
                        tmp_user_name = timesheet['user_id'][1]
                    else:
                        tmp_user_id = ""
                        tmp_user_name = ""

                    ticket_with_timesheet.update({
                        'timesheet_id': timesheet['id'],
                        'timesheet_name': timesheet['name'],
                        'timesheet_date': timesheet['date'],
                        'timesheet_unit_amount': timesheet['unit_amount'],
                        'timesheet_unit_amount_60': timesheet['unit_amount'] / 24,
                        'timesheet_amount': timesheet['amount'],
                        'timesheet_user_id': tmp_user_id,  
                        'timesheet_user_name': tmp_user_name,
                        'timesheet_account_id': timesheet['account_id'],
                    })
                    # Para el primer timesheet, mantener el valor de tiempo_abierto, para los demás ponerlo a cero
                    ticket_with_timesheet['tiempo_abierto'] = ticket.get('tiempo_abierto', 0)
                    tickets_timesheets.append(ticket_with_timesheet)

    if g_debug:
        print(f"Finalizó agregar_partes_horas_por_lotes  ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})\n")
        print(f"\n\nEstos son los datos con sus partes de horas")
        for ticket in tickets_timesheets:
            print(f"*** {ticket} ***\n")
        print(f"Fin de datos con partes de horas\n")

    return tickets_timesheets

def tickets_timesheets_bloque(models, db, uid, password, all_timesheet_ids, p_fecha_desde_ph, p_fecha_hasta_ph, chunk_size=300):
    """Obtener detalles de partes de horas de Odoo en bloques para evitar timeout."""
    all_timesheets = []
    total_ids = len(all_timesheet_ids)

    for i in range(0, total_ids, chunk_size):
        chunk = all_timesheet_ids[i:i + chunk_size]
        if g_debug:
            print(f"*** Obteniendo partes de horas para IDs: \n{chunk}")
        try:
            timesheets = models.execute_kw(db, uid, password, 'account.analytic.line', 'search_read',
                [[
                    ['id', 'in', chunk],
                    ['date', '>=', p_fecha_desde_ph],
                    ['date', '<=', p_fecha_hasta_ph]
                ]],
                {'fields': ['id', 'name', 'date', 'unit_amount', 'amount', 'user_id', 'account_id']}
            )

            all_timesheets.extend(timesheets)
        except Exception as e:
            print(f"Error al obtener partes de horas para IDs {chunk}: {e}")

    return all_timesheets

# end region

def sumarizar_partes_horas (p_tickets, p_minutos):
    global g_todo_ok, g_datos_conexion, g_msj, g_debug

    if g_debug:
        print(f"Iniciando sumarizar_partes_horas. Registros a procesar: {len(p_tickets)}  ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})")
    
    tickets_sumarizados = []

    # Diccionario para almacenar los tiempos sumarizados por ticket
    ticket_sums = {}

    p_minutos = round(p_minutos / 60,8)
    for ticket in p_tickets:
        ticket_id = ticket['id']

        if ticket_id not in ticket_sums:
            # Copiar todos los campos originales al diccionario ticket_sums[ticket_id]
            ticket_sums[ticket_id] = ticket.copy()
            
            # Inicializar los campos sumarizados
            ticket_sums[ticket_id]['tiempo_efectivo'] = 0
            ticket_sums[ticket_id]['tiempo_efectivo_60'] =0
            ticket_sums[ticket_id]['partes_horas_cantidad'] = 0
            ticket_sums[ticket_id]['tiempo_dif'] = 0
            ticket_sums[ticket_id]['tiempo_dif_60'] = 0
            ticket_sums[ticket_id]['valido'] = '0'
            
        # Si el ticket tiene partes de horas
        if ticket['timesheet_ids']:
            ticket_sums[ticket_id]['partes_horas_cantidad'] = len(ticket['timesheet_ids'])
            ticket_sums[ticket_id]['tiempo_efectivo'] += ticket['timesheet_unit_amount']
            ticket_sums[ticket_id]['tiempo_efectivo_60'] += ticket['timesheet_unit_amount']/24
            
            ticket_sums[ticket_id]['tiempo_dif'] = ticket['tiempo_abierto'] - ticket_sums[ticket_id]['tiempo_efectivo']
            ticket_sums[ticket_id]['tiempo_dif_60'] = abs((ticket['tiempo_abierto'] - ticket_sums[ticket_id]['tiempo_efectivo']) / 24)
            
            if round(abs(ticket_sums[ticket_id]['tiempo_dif']),8) <= p_minutos:
                ticket_sums[ticket_id]['valido'] = '1'
            else:
                ticket_sums[ticket_id]['valido'] = '0'

            # if g_debug:
            #     print(f"   *** Analizando tiempo_dif (si tiene partes de horas)")
            #     print(f"      Ticket {ticket['ticket_ref']}")
            #     print(f"      TiempoDIF (abs): {abs(ticket_sums[ticket_id]['tiempo_dif'])}")
            #     print(f"      p_minutos: {p_minutos}")
            #     print(f"      ticket_sums[ticket_id]['valido']: {ticket_sums[ticket_id]['valido']}")
            
            
        else:
            ticket_sums[ticket_id]['partes_horas_cantidad'] = 0
            ticket_sums[ticket_id]['tiempo_efectivo'] = 0
            ticket_sums[ticket_id]['tiempo_dif'] = 0
            ticket_sums[ticket_id]['tiempo_dif_60'] = 0
            ticket_sums[ticket_id]['valido'] = '0'

        # El ticket no está finalizado por lo que el criterio no se puede aplicar
        if not ticket['stage_fold']:
            ticket_sums[ticket_id]['valido'] = '0'

    # Convertir el diccionario de tickets sumarizados a una lista
    tickets_sumarizados = list(ticket_sums.values())

    if g_debug:
        print(f"FINALIZADO sumarizar_partes_horas  ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})")
        # for ticket in tickets_sumarizados:
        #     print(f"*** ticket: {ticket}")
        # print("Fin de datos sumarizar_partes_horas")
    return tickets_sumarizados

def formatear_estructura (p_key, p_value, p_new_ticket, p_seguir_procesando):
    global g_todo_ok, g_datos_conexion, g_msj, g_debug
    p_seguir_procesando = True
    
    if p_key[-3:] == "_id":
        k_id = p_key
        k_valor = p_key[:-3] 
    else:
        k_id = p_key + "_id"
        k_valor = p_key

    if isinstance(p_value, list) and len(p_value) == 2:
        p_new_ticket[k_id] = p_value[0]
        p_new_ticket[k_valor] = p_value[1]
        p_seguir_procesando = False
    else:
        if (p_key in ["tipo_cierre_id", "user_id", "clasificacion_tipo_soporte_id", "clasificacion_aplicacion_id", "clasificacion_modulo_id"
                      , "clasificacion_proyecto_id", "company_id","stage_id", "partner_id", "canal_atencion_id"
                      ]):
            p_new_ticket[k_id] = ""
            p_new_ticket[k_valor] = ""
            p_seguir_procesando = False

    return p_new_ticket, p_seguir_procesando

def formatear_fecha_utc(p_key, p_value, p_new_ticket, p_seguir_procesando):
    global g_todo_ok, g_datos_conexion, g_msj, g_debug

    # Se asume que si viene una fecha está en UTC y se debe convertir a GTC
    l_key = p_key.lower()
    l_es_fecha = False
    p_seguir_procesando = True

    l_es_fecha = (
                    ("date" in l_key or "fecha" in l_key)    
                    and
                    (l_key not in ["timesheet_date", "fecha_operacion"])
                    and 
                    ("flag" not in l_key)
                )

    # if g_debug and l_es_fecha:
    #     print(f"*** Tengo una fecha: ")
    #     print(f"    p_key: {p_key}  p_value: {p_value}")
        #print(f"ticket con fechas ORIGINALES\n{p_new_ticket}")

    if (l_es_fecha) and (not p_value):
        p_seguir_procesando = False
        p_new_ticket[p_key] = ""

    if (p_seguir_procesando) and (l_es_fecha):
        # Define la zona horaria UTC
        utc_zone = pytz.utc
        # Define la zona horaria de Guatemala
        gtc_zone = pytz.timezone('America/Guatemala')
        
        # Convierte el string p_value a un objeto datetime
        if p_key == "cn003_fecha_cierre_ofrecida":
            p_value = p_value + " 00:00:00"

        utc_datetime = datetime.strptime(p_value, '%Y-%m-%d %H:%M:%S')
        
        # Asigna la zona horaria UTC al objeto datetime
        utc_datetime = utc_zone.localize(utc_datetime)
        
        # Convierte la fecha-hora a la zona horaria de Guatemala
        gtc_datetime = utc_datetime.astimezone(gtc_zone)
        p_new_ticket[p_key] = gtc_datetime.isoformat()
        p_seguir_procesando = False

        # if g_debug:
        #     print(f"    Hora convertida: {gtc_datetime}")
            #print(f"ticket con fechas modificadas\n{p_new_ticket}")
    return p_new_ticket, p_seguir_procesando, l_es_fecha

def fecha_excel(p_fecha):
    # Si la fecha es nula o vacía, devolver el valor correspondiente a 1900-01-01
    if not p_fecha:
        return 1.0  # 1900-01-01 en Excel es 1

    # Convierte la cadena de fecha en un objeto datetime
    dt = datetime.fromisoformat(p_fecha)
    
    # Remueve la información de zona horaria para hacer dt "offset-naive"
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)

    # Define el inicio de la fecha en Excel (01-01-1900)
    excel_epoch = datetime(1899, 12, 30)

    # Calcula la diferencia en días y fracción de días (horas, minutos, segundos)
    delta = dt - excel_epoch

    # Calcula el número de días en formato Excel
    excel_date_value = delta.days + (delta.seconds + delta.microseconds / 1e6) / 86400

    return excel_date_value

def ajustar_ticket_excel(new_ticket):
    global g_todo_ok, g_datos_conexion, g_msj, g_debug

    # Lista de campos a procesar
    campos_fechas = [
        'cn003_fecha_apertura'
        ,'cn003_fecha_apertura_manual'
        ,'cn003_fecha_apertura_reporte'
        ,'cn003_fecha_cierre'
        ,'cn003_fecha_cierre_manual'
        ,'cn003_fecha_cierre_ofrecida'
        ,'cn003_fecha_cierre_reporte'
        ,'create_date'
        ,'__last_update'
        ,'write_date'
    ]
    
    #if g_debug:
    #    print(f"***** Iniciando ajustar_ticket_excel  ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})")
        #print(f"         ticket recibido: {new_ticket}\n")

    # Itera sobre los campos y convierte las fechas usando fecha_excel
    for campo in campos_fechas:
        if campo in new_ticket:
            new_ticket[campo] = fecha_excel(new_ticket[campo])

    #if g_debug:
    #    print(f"***** Finalizado ajustar_ticket_excel  ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})\n")
        #print(f"      ticket a retornar: {new_ticket}")

    return new_ticket

def ajustar_nombre_key (p_key):
    p_key = p_key.lower()

    # if g_debug:
    #     if p_key in ["60", "unit","unit_amount", "valido"]:
    #         print(f"Hay un p_key de interes.   p_key: {p_key}")

    if p_key == "id": 
        p_key = "__tck_interno_id"
    elif p_key == "ticket_ref": 
        p_key = "TCK Ticket"
    elif p_key == "team_id": 
        p_key = "TCK Mesa Id"
    elif p_key == "team": 
        p_key = "TCK Mesa"
    elif p_key == "partner_id": 
        p_key = "TCK Cliente Id"
    elif p_key == "partner": 
        p_key = "TCK Cliente"
    elif p_key == "user_id": 
        p_key = "TCK Técnico Id"
    elif p_key == "user": 
        p_key = "TCK Técnico"
    elif p_key == "name_company": 
        p_key = "__tck_interno_empresa"
    elif p_key =="canal_atencion_id":
        p_key = "TCK Canal Atención Id"
    elif p_key =="canal_atencion":
        p_key = "TCK Canal Atención"
    elif p_key == "clasificacion_tipo_soporte_id": 
        p_key = "TCK Tipo Soporte Id"
    elif p_key == "clasificacion_tipo_soporte": 
        p_key = "TCK Tipo Soporte"
    elif p_key == "clasificacion_aplicacion_id": 
        p_key = "TCK Aplicación Id"
    elif p_key == "clasificacion_aplicacion": 
        p_key = "TCK Aplicación"
    elif p_key == "clasificacion_modulo_id": 
        p_key = "TCK Módulo Id"
    elif p_key == "clasificacion_modulo": 
        p_key = "TCK Módulo"
    elif p_key == "clasificacion_proyecto_id": 
        p_key = "TCK Proyecto ID"
    elif p_key == "clasificacion_proyecto": 
        p_key = "TCK Proyecto"
    elif p_key == "cn003_fecha_apertura": 
        p_key = "TCK cn003_fecha_apertura"
    elif p_key == "cn003_fecha_apertura_flag": 
        p_key = "TCK cn003_fecha_apertura_flag"
    elif p_key == "cn003_fecha_apertura_manual": 
        p_key = "TCK cn003_fecha_apertura_manual"
    elif p_key == "cn003_fecha_apertura_reporte": 
        p_key = "TCK cn003_fecha_apertura_reporte"
    elif p_key == "cn003_fecha_cierre": 
        p_key = "TCK cn003_fecha_cierre"
    elif p_key == "cn003_fecha_cierre_flag": 
        p_key = "TCK cn003_fecha_cierre_flag"
    elif p_key == "cn003_fecha_cierre_manual": 
        p_key = "TCK cn003_fecha_cierre_manual"
    elif p_key == "cn003_fecha_cierre_ofrecida": 
        p_key = "TCK cn003_fecha_cierre_ofrecida"
    elif p_key == "cn003_fecha_cierre_reporte": 
        p_key = "TCK cn003_fecha_cierre_reporte"
    elif p_key == "tiempo_dif":
        p_key = "TCK DIF"
    elif p_key == "tiempo_dif_60":
        p_key = "TCK DIF 60"
    elif (p_key == "valido" or p_key == "TCK valido"):
        p_key = "TCK Valido"
    elif p_key == "fecha_operacion":
        p_key = "TCK Fecha Operación"
    elif p_key == "create_date": 
        p_key = "TCK Fecha Creación"
    elif p_key == "TCK CN003_FECHA_CIERRE_OFRECIDA":
        p_key = "TCK Fecha Ofrecida"
    elif p_key == "__last_update": 
        p_key = "TCK Fecha Última Actualización"
    elif p_key == "write_date": 
        p_key = "TCK Fecha Modificación"
    elif p_key == "company_id": 
        p_key = "__tck_interno_company_id"
    elif p_key == "company": 
        p_key = "__tck_interno_company"
    elif p_key == "create_uid_id": 
        p_key = "__tck_interno_create_uid_id"
    elif p_key == "create_uid": 
        p_key = "__interno_tck_create_uid"
    elif p_key == "description": 
        p_key = "TCK description"
    elif p_key == "kanban_state": 
        p_key = "TCK kanban_state"
    elif p_key == "kanban_state_label": 
        p_key = "TCK Kanban"
    elif p_key == "name": 
        p_key = "TCK Descripción Corta"
    elif p_key == "partner_name": 
        p_key = "TCK Cliente"
    elif p_key == "priority": 
        p_key = "TCK Prioridad"
    elif p_key == "stage_id": 
        p_key = "TCK stage_id"
    elif p_key == "stage": 
        p_key = "TCK Etapa"
    elif p_key == "stage_fold": 
        p_key = "TCK stage_fold"
    elif p_key == "timesheet_ids": 
        p_key = "TCK Partes de Horas Asociados"
    elif p_key == "timesheet_ids_id":
        p_key = "TCK Parte Horas ID"
    elif p_key == "tipo_cierre_id": 
        p_key = "TCK Cierre Tipo Id"
    elif p_key == "tipo_cierre": 
        p_key = "TCK Cierre Tipo"
    elif p_key == "tipo_cierre_descripcion": 
        p_key = "TCK Cierre Descripción"
    elif p_key == "vhur_correo_electronico": 
        p_key = "TCK Cliente email"
    elif p_key == "vhur_departamento_nombre": 
        p_key = "TCK Cliente Departamento"
    elif p_key == "vhur_empresa_nombre": 
        p_key = "TCK Cliente Empresa"
    elif p_key == "tiempo_abierto_segundos": 
        p_key = "TCK Tiempo Abierto"
    elif p_key == "tiempo_abierto_formato": 
        p_key = "TCK Tiempo Abierto 60"
    elif p_key == "timesheet_id": 
        p_key = "PH Parte de Horas"
    elif p_key == "timesheet_name": 
        p_key = "PH Descripción"
    elif p_key == "timesheet_date": 
        p_key = "PH Fecha"
    elif p_key == "timesheet_unit_amount": 
        p_key = "PH Tiempo"
    elif p_key in ["timesheet_unit_amount_60", "unit_amount_60"]:
        p_key = "PH Tiempo 60"
    elif p_key == "timesheet_amount": 
        p_key = "__interno_timesheet_amount"
    elif p_key == "timesheet_user_id": 
        p_key = "PH Técnico Id"
    elif p_key in ["timesheet_user","timesheet_user_name", "TIMESHEET_USER_NAME"]: 
        p_key = "PH Técnico"
    elif p_key == "timesheet_account_id": 
        p_key = "__interno_timesheet_account_id"
    elif p_key == "timesheet_account": 
        p_key = "__interno_timesheet_account"
    elif p_key == "tiempo_abierto": 
        p_key = "TCK Tiempo Abierto xx"

    p_key = p_key.lower()
    return p_key

def formatear_nombre (p_tickets):
    global g_todo_ok, g_datos_conexion, g_msj, g_debug

    #if g_debug:
    #    print(f"   ***Iniciando formatear_nombre  ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})"  )

    tickets_modificados = []
    for ticket in p_tickets:
        ticket_modificado = {}

        for p_key, value in ticket.items():
            p_key = ajustar_nombre_key(p_key)
            ticket_modificado[p_key] = value
        tickets_modificados.append(ticket_modificado)

    #if g_debug:
    #    print(f"   ***Finalizado formatear_nombre  ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})\n"  )

    return tickets_modificados

def asigna_diccionario(p_tipo_registro):
    global g_todo_ok, g_datos_conexion, g_msj, g_debug

    if g_debug:
        print (f"\n****** Iniciando asignar diccionario p_tipo_registro ***{p_tipo_registro}***  ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})")

    diccionario = []

    p_tipo_registro = p_tipo_registro.replace(" ", "").strip().upper()

    if not(p_tipo_registro in ["NORMAL", "RESUMEN"]):
        if g_debug:
            print(f"p_tipo_registro no tiene valor válido.  Valor recibido: ***{p_tipo_registro}***")
        return diccionario
    
    if p_tipo_registro == "NORMAL":
        diccionario = [
                "TCK TICKET", "PH TIEMPO","PH TIEMPO 60", "TCK ETAPA", "TCK PRIORIDAD"
                , "TCK FECHA CREACIÓN", "TCK CN003_FECHA_CIERRE_OFRECIDA", "TCK CN003_FECHA_APERTURA_REPORTE"
                , "TCK CN003_FECHA_CIERRE_REPORTE"
                , "TCK TIEMPO ABIERTO", "TCK TIEMPO ABIERTO 60"
                ,"TCK DIF","TCK DIF 60", "TCK FECHA OPERACIÓN"
                , "TCK CN003_FECHA_APERTURA", "TCK CN003_FECHA_APERTURA_FLAG", "TCK CN003_FECHA_APERTURA_MANUAL"
                , "TCK CN003_FECHA_CIERRE", "TCK CN003_FECHA_CIERRE_FLAG"
                , "TCK CN003_FECHA_CIERRE_MANUAL", "TCK FECHA ÚLTIMA ACTUALIZACIÓN", "TCK FECHA MODIFICACIÓN"
                , "TCK CIERRE TIPO", "TCK CIERRE DESCRIPCIÓN", "PH FECHA"
                , "TIMESHEET_USER_NAME", "PH DESCRIPCIÓN", "TCK TÉCNICO", "TCK TIPO SOPORTE", "TCK CANAL ATENCIÓN"
                , "TCK APLICACIÓN", "TCK MÓDULO", "TCK PROYECTO", "TCK CLIENTE EMPRESA"
                , "TCK CLIENTE DEPARTAMENTO"
                , "__TCK_INTERNO_ID", "TCK MESA ID", "TCK MESA", "TCK CLIENTE ID", "TCK CLIENTE", "TCK TÉCNICO ID", "__TCK_INTERNO_EMPRESA"
                , "TCK TIPO SOPORTE ID", "TCK APLICACIÓN ID", "TCK MÓDULO ID", "TCK PROYECTO ID", "__TCK_INTERNO_COMPANY_ID", "__TCK_INTERNO_COMPANY"
                , "__TCK_INTERNO_CREATE_UID_ID", "__INTERNO_TCK_CREATE_UID", "TCK DESCRIPTION", "TCK KANBAN_STATE", "TCK KANBAN", "TCK DESCRIPCIÓN CORTA"
                , "TCK STAGE_ID", "TCK STAGE_FOLD", "TCK PARTES DE HORAS ASOCIADOS", "TCK CIERRE TIPO ID", "TCK CLIENTE EMAIL"
                , "PH PARTE DE HORAS", "__INTERNO_TIMESHEET_AMOUNT", "PH TÉCNICO ID"
                , "__INTERNO_TIMESHEET_ACCOUNT_ID", "__INTERNO_TIMESHEET_ACCOUNT", "TCK TIEMPO ABIERTO", "TCK PARTE HORAS ID"
            ]
    else:
        diccionario = [ "TCK TICKET"
                , "TIEMPO_EFECTIVO", "TIEMPO_EFECTIVO_60","PARTES_HORA_CANTIDAD"
                , "TCK TIEMPO ABIERTO", "TCK TIEMPO ABIERTO 60"
                , "TCK DIF", "TCK DIF 60", "TCK VALIDO"
                , "TCK ETAPA", "TCK PRIORIDAD"
                , "TCK CN003_FECHA_APERTURA_REPORTE", "TCK CN003_FECHA_CIERRE_REPORTE", "TCK FECHA CREACIÓN"
                , "TCK CN003_FECHA_CIERRE_OFRECIDA"
                , "TCK DIF", "TCK FECHA OPERACIÓN"
                , "TCK TÉCNICO", "TCK CLIENTE", "TCK TIPO SOPORTE", "TCK CANAL ATENCIÓN"
                , "TCK APLICACIÓN", "TCK MÓDULO", "TCK PROYECTO", "TCK CLIENTE EMPRESA"
                , "TCK CLIENTE DEPARTAMENTO"
                , "TCK CIERRE TIPO", "TCK CIERRE DESCRIPCIÓN"
                , "TCK KANBAN", "TCK STAGE_FOLD", "TCK DESCRIPCIÓN CORTA"
                , "__TCK_INTERNO_EMPRESA"
                
            ]
                    


    
    diccionario = [clave.lower() for clave in diccionario]
        
    if g_debug:
        print(f"****** Finalizado asignar diccionario.  ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})")
        #print(f"          Resultado: \n{diccionario}")

    return diccionario

def ordenar_nombre (p_tickets, p_tipo_registro):
    global g_todo_ok, g_datos_conexion, g_msj, g_debug

    if g_debug:
        print (f"Iniciando ordenar_nombre P_TIPO_REGISTRO ***{p_tipo_registro}***  ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})")

    # Diccionario de orden de los campos
    orden = asigna_diccionario(p_tipo_registro)

    
    
    # Iterar sobre cada ticket en la lista y aplicar el orden a cada diccionario
    tickets_ordenados = []
    for ticket in p_tickets:
        ticket_ordenado = {clave: ticket[clave] for clave in orden if clave in ticket}
        tickets_ordenados.append(ticket_ordenado)	

    if g_debug:
        print("********************************************************************************************************************************")
        print("********************************************************************************************************************************")
        print (f"Finalizado ordenar_nombre  ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})")
        print("********************************************************************************************************************************")
        print("********************************************************************************************************************************")

    return tickets_ordenados

def formatear_info (p_tickets, p_tipo_registro):
    """
    Coloca los formatos correctos en cada campo, asigna nombres para usuario final y dependiendo si es el registro sumarizador, reduce la cantidad de datos

    Args:
        p_tickets (list): Una lista de diccionarios, donde cada diccionario 
                        representa un ticket con sus respectivos campos.
        
        p_tipo_registro: 
                        NORMAL:  Son los registros de detalle de los tickets.  Conserva todos los campos.

                        RESUMEN: Son los registros ya totalizados.  Se seleccionan los campos que se conservan. 
    Returns:
        tickets_ajustados:  Una lista de diccionarios donde cada diccionario representa un ticket.
                            NORMAL: Devuelve un registro de ticket por cada parte de horas que tiene el ticket.  No totaliza. 
                            
                            RESUMEN: Devuelve un registro único por cada ticket con el total del tiempo de partes de horas en el registro.
    """
    global g_todo_ok, g_datos_conexion, g_msj, g_debug

    if g_debug:
        print(f"Iniciando formatear_info.  p_tipo_registro: {p_tipo_registro}  ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})")
        #if p_tipo_registro == "RESUMEN":
        #    print(f"{p_tickets}\n")


    # Nueva estructura para almacenar los tickets modificados
    tickets_ajustados = []

    p_tipo_registro = p_tipo_registro.replace(" ", "").strip().upper()

    if not(p_tipo_registro in ["NORMAL", "RESUMEN"]):
        if g_debug:
            print(f"p_tipo_registro no tiene valor válido.  Valor recibido: ***{p_tipo_registro}***")
        return tickets_ajustados
   
    # Crear un conjunto para las claves que deben procesarse como estructuras simples
    estructura_claves = {
        "tipo_cierre_id", "user_id", "clasificacion_tipo_soporte_id", "clasificacion_aplicacion_id",
        "clasificacion_modulo_id", "clasificacion_proyecto_id", "company_id", "stage_id", "partner_id",
        "canal_atencion_id"
    }
    # Obtener la longitud de p_tickets fuera del bucle
    total_tickets = len(p_tickets)

    # Recorrer la estructura original y realizar los ajustes
    for contador, ticket in enumerate(p_tickets, start=1):
        if g_debug:
            print(
                f"Formateando registro INI # {contador:07,} de {total_tickets:07,} "
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

        new_ticket = {}

        for key, value in ticket.items():
            key = key.lower()
            seguir_procesando = True

            # Datos que son estructuras y deben dejarse como registros simples
            if key in estructura_claves:
                new_ticket, seguir_procesando = formatear_estructura(key, value, new_ticket, seguir_procesando)

            # Fechas UTC
            if seguir_procesando and (
                ("date" in key or "fecha" in key)
                and key not in {"timesheet_date", "fecha_operacion"}
                and "flag" not in key
            ):
                new_ticket, seguir_procesando, es_fecha = formatear_fecha_utc(key, value, new_ticket, seguir_procesando)

            # En caso el campo no cumpla con ninguna condición especial debe agregarse al ticket
            if seguir_procesando:
                new_ticket[key] = value

        if new_ticket:
            # cambio fecha excel
            new_ticket = ajustar_ticket_excel(new_ticket)
            tickets_ajustados.append(new_ticket)
        else:
            ticket = ajustar_ticket_excel(ticket)
            tickets_ajustados.append(ticket)

        # Ajustar los nombres a lo requerido por Canella y que sean más user friendly
        #if g_debug:
        #    print(f"*** Antes    de llamar a formatear_nombre {({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})}")

        tickets_ajustados = formatear_nombre (tickets_ajustados)

        #if g_debug:
        #     print(f"*** Después de llamar a formatear_nombre {({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})}")

        if g_debug:
                print(f"Formateando registro FIN # {contador:07,} de {len(p_tickets):07,}  {({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})}\n")

    # Ajustar el orden de los campos dependiendo del tipo de registro
    # if g_debug:
    #     print(f"Voy a colocar p_tipo_registro\n")
    #     print(f"Antes de ordenar_nombre.  p_tipo_registro ***{p_tipo_registro}***")



    tickets_ajustados = ordenar_nombre (tickets_ajustados, p_tipo_registro)

    #if g_debug:
    #    print(f"Después de ordenar_nombre.  p_tipo_registro ***{p_tipo_registro}***")

    # Imprimir los tickets modificados
    if g_debug:
        #print("**************************************************************")
        #print("**************************************************************")
        print(f"Finalizado formatear_info.  ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})")
        # print(f"Estos son los registros modificados\n")
        # for ticket in tickets_ajustados:
        #     print(ticket)
        #print("**************************************************************")
        #print("**************************************************************\n")

    return tickets_ajustados  # formatear_info

def convertir_a_json (p_tickets):
    global g_todo_ok, g_datos_conexion, g_msj, g_debug

    if g_debug:
        print(f"\nIniciando convertir_a_json  ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})")

    ticket_tmp = []
    ticket_tmp = json.dumps(p_tickets, indent=4, ensure_ascii=False)

    if g_debug:
        print(f"\nFinalizó convertir_A_json  ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})")
        # print(f"\nJSON \n\n {ticket_tmp}\n\n Fin de datos")
    
    return ticket_tmp

def crear_salida (p_tickets_json):
    global g_todo_ok, g_datos_conexion, g_msj, g_debug

    if g_debug:
        print(f"\nIniciando crear_salida  ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})")

    data = json.loads(p_tickets_json)

    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
        

        if g_debug:
            print(f"Obtener nombres de campos  ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})")

        # Obtener los nombres de los campos
        fields = data[0].keys()

        # Crear la salida
        output = []

        if g_debug:
            print(f"Añadir los nombres de los campos a la salida  ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})")
        # Añadir los nombres de los campos a la salida
        output.append("|NT|".join(fields))

        if g_debug:
            print(f"Añadir cada registro a la salida (ciclo)  ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})")

        # Añadir cada registro a la salida
        for record in data:
            for key in record:
                if isinstance(record[key], str):
                    record[key] = record[key].replace('\n', ' ** ')

            row = [str(record.get(field, '')) for field in fields]
            output.append("|NT|".join(row))
    return output

################################################################################################################
# Lógica principal
################################################################################################################
def main(pURL, pDB, pUserName, pPassword, pFechaDesde, pFechaHasta, pMinutos, pDebug) -> tuple [bool, dict, str]:
    """ Retorna todo_ok, 
    """
    global g_todo_ok, g_datos_conexion, g_msj, g_debug

    g_debug = pDebug
    
    try:
        # Autenticación con Odoo
        autenticar_odoo(pURL, pDB, pUserName, pPassword)
        if (not g_todo_ok):
            print (f"(ERROR) (010) error de autenticación|{g_todo_ok}|{datos_conexion}|{msj}|")
            return g_todo_ok, g_datos_conexion, g_msj
       
        # Convertir pFechaDesde y pFechaHasta a UTC 0 desde UTC -6 (Guatemala)
        p_fecha_desde_utc = convertir_gtc_a_utc(pFechaDesde, "INI")
        p_fecha_hasta_utc = convertir_gtc_a_utc(pFechaHasta, "FIN")

        # Obtener los tickets en el rango de fechas
        tickets = []
        #tickets = obtener_tickets(p_fecha_desde_utc, p_fecha_hasta_utc)
        tickets = obtener_tickets_2(p_fecha_desde_utc, p_fecha_hasta_utc,pFechaDesde, pFechaHasta)

        # Cálculo de tiempo_abierto
        tickets = calcular_tiempo_abierto(tickets)

        # Agregar partes de horas a los tickets
        tickets_timesheets = []
        #tickets_timesheets = agregar_partes_horas(tickets)
        tickets_timesheets = agregar_partes_horas_por_lotes(tickets, pFechaDesde, pFechaHasta)

        # Esta estructura debe tener un registro por ticket donde se resuman los partes de horas
        tickets_sumarizados = []
        tickets_sumarizados = sumarizar_partes_horas(tickets_timesheets, pMinutos)

        # Colocar nombres oficiales a los campos, ajustes utc a fechas, orden de los campos
        # Dividir las estrucutras código-nombre y dejar solo el nombre (contenido)
        # Ordena los campos
        tickets_timesheets = formatear_info(tickets_timesheets,"NORMAL")
        tickets_sumarizados = formatear_info(tickets_sumarizados,"RESUMEN")

        # Convertir a JSON la información
        tickets_timesheets_json = convertir_a_json(tickets_timesheets)
        tickets_sumarizados_json = convertir_a_json(tickets_sumarizados)

        # Crear y presentar la salida normal
        if g_debug:
            print(f"************************  MARCA MARCA MARCA MARCA MARCA   ************************")
            print(f"************************  MARCA MARCA MARCA MARCA MARCA   ************************")
        salida = []
        salida = crear_salida(tickets_timesheets_json)
        for linea in salida:
            print(linea)

        # Crear y presentar la salida sumarizada
        salida = []
        salida = crear_salida(tickets_sumarizados_json)
        print("|||RESUMEN|||")
        for linea in salida:
            print(linea)

        return

    # EXCEPCIONES - EXCEPCIONES - EXCEPCIONES - EXCEPCIONES - EXCEPCIONES - EXCEPCIONES - EXCEPCIONES - EXCEPCIONES - EXCEPCIONES - 
    except xmlrpc.client.ProtocolError as error:
        asigna_error(f"Error de protocolo.  {error}|")
        print (f"|Todo Ok: {g_todo_ok}|conexión: {g_datos_conexion}|msj: {g_msj}|")            
        #return g_todo_ok, g_datos_conexion, g_msj
    except xmlrpc.client.Fault as error:
        asigna_error(f"Error de RPC: {error}")
        print (f"|Todo Ok: {g_todo_ok}|conexión: {g_datos_conexion}|msj: {g_msj}|")            
        #return g_todo_ok, g_datos_conexion, g_msj
    except Exception as error:
        asigna_error(f"Error general: {error}")
        print (f"|Todo Ok: {g_todo_ok}|conexión: {g_datos_conexion}|msj: {g_msj}|")            
        #return g_todo_ok, g_datos_conexion, g_msj

################################################################################################################
# FIN - Lógica principal
################################################################################################################


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script para obtener partes de horas desde Odoo.")
    parser.add_argument("pFechaDesde", help="Fecha de inicio para filtrar partes de horas (formato: YYYY-MM-DD)")
    parser.add_argument("pFechaHasta", help="Fecha de fin para filtrar partes de horas (formato: YYYY-MM-DD)")
    parser.add_argument('pMinutos', type=float, nargs='?', default=0, help="Número (base 10) que representa minutos (predeterminado: 0)")
    parser.add_argument('pDebug', type=str2bool, nargs='?', const=True, default=False, help="True - Despliega mensajes de seguimiento | False - para correr en producción")
    parser.set_defaults(pFechaDesde="2020-01-01", pFechaHasta="2999-12-31", pDebug=False)

    args = parser.parse_args()

    args.pDebug = str2bool(args.pDebug)

    _server = "DESA"
    #_server = "PROD"

    if _server == "DESA":
        if args.pDebug:
            print("Base de datos:  DESA DESA DESA DESA DESA DESA DESA DESA")

        _pURL = "https://canella-canellatest2-17948159.dev.odoo.com"
        _pDB = "canella-pruebacanella-14553139"
        _pUserName = "odoo_reportes@canella.com.gt"
        _pPassword = "2adb5989440eaad90ad2b706d69e311757d6d389"
    else:
        if args.pDebug:
            print("Base de datos:  PROD PROD PROD PROD PROD PROD")

        _pURL = "https://canella.odoo.com"
        _pDB = "piensom-canella1-main-7955386"
        _pUserName = "odoo_reportes@canella.com.gt"
        _pPassword = "2adb5989440eaad90ad2b706d69e311757d6d389"

    
    # Puedes ahora pasar args.pMinutos a la función main si es necesario
    main(_pURL, _pDB, _pUserName, _pPassword, args.pFechaDesde, args.pFechaHasta, args.pMinutos, args.pDebug )
