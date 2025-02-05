from cn006_kpis_globales import cCN006_globales
import xlsxwriter
import io



import xmlrpc.client
import json
import argparse
import pytz
from datetime import datetime
from collections import defaultdict
import codecs


#region EXPLICACIÓN DEL PROCESO
"""  ******* EXPLICACIÓN DEL PROCESO
    1. Obtener todos los proyectos de TI (cn006_project = True)
    2. Obtener todos los tickets de esos proyectos
    3. Combinar los tickets con los proyectos
************************************************************************  """
#endregion

def msj_debug (p_msj, p_tools: cCN006_globales):
    if p_tools.g_debug:
        print(p_msj)
    return

################################################################################################################
# Extracción de información
################################################################################################################

#region OBTENER PROYECTOS
def obtener_proyectos(p_tools: cCN006_globales):
    models = xmlrpc.client.ServerProxy(f"{p_tools.cnx_url}/xmlrpc/2/object")

    # Obtener proyectos donde cn006_project = True
    # agregar el campo cn006_emergente
    proyectos = models.execute_kw(
                                    p_tools.cnx_db, p_tools.cnx_uid, p_tools.cnx_password,
                                    'project.project', 'search_read', 
                                    [[('cn006_project', '=', True)]], 
                                    {'fields': [
                                        'id', 'name', 'user_id', 'active', 
                                        'company_id', 'partner_id', 'date_start', 'date',
                                        'description',
                                        'cn006_clasificacion_id', 
                                        'cn006_grado_avance_id', 'cn006_grado_complejidad_id', 'cn006_nivel_importancia_id', 'cn006_nivel_urgencia_id', 'cn006_tamano_id', 
                                        'cn006_project',
                                        'cn006_fecha_creacion_sistema', 'cn006_fecha_creacion_oficial', 'cn006_fecha_inicio_oficial', 'cn006_fecha_inicio_sistema', 
                                        'cn006_fecha_entrega_informatica_estimada', 'cn006_fecha_entrega_informatica_oficial', 'cn006_fecha_entrega_informatica_sistema', 
                                        'cn006_fecha_entrega_usuario_estimada', 'cn006_fecha_entrega_usuario_oficial', 'cn006_fecha_entrega_usuario_sistema', 
                                        'cn006_fecha_cierre_estimada', 'cn006_fecha_cierre_oficial', 'cn006_fecha_cierre_sistema',
                                        'create_date', 'create_uid', 'write_date', 'write_uid',
                                        'timesheet_ids', 'task_ids'
                                        ]
                                    }
                                )
    
    # Ajustando los campos para que sean manejables en excel
    # Lista de campos tipo fecha
    campos_fecha = [
        'date_start', 'date',
        'cn006_fecha_creacion_sistema', 'cn006_fecha_creacion_oficial', 
        'cn006_fecha_inicio_oficial', 'cn006_fecha_inicio_sistema', 
        'cn006_fecha_entrega_informatica_estimada', 'cn006_fecha_entrega_informatica_oficial', 
        'cn006_fecha_entrega_informatica_sistema', 'cn006_fecha_entrega_usuario_estimada', 
        'cn006_fecha_entrega_usuario_oficial', 'cn006_fecha_entrega_usuario_sistema', 
        'cn006_fecha_cierre_estimada', 'cn006_fecha_cierre_oficial', 
        'cn006_fecha_cierre_sistema'
    ]

    for proyecto in proyectos:
        #region Campos que son estructura
        if proyecto['user_id']:
            proyecto['user_id_name'] = proyecto['user_id'][1]
            proyecto['user_id'] = proyecto['user_id'][0]
        else:
            proyecto['user_id_name'] = None
            proyecto['user_id'] = None

        if proyecto['company_id']:
            proyecto['company_id_name'] = proyecto['company_id'][1]
            proyecto['company_id'] = proyecto['company_id'][0]
        else:
            proyecto['company_id_name'] = None
            proyecto['company_id'] = None

        if proyecto['partner_id']:
            proyecto['partner_id_name'] = proyecto['partner_id'][1]
            proyecto['partner_id'] = proyecto['partner_id'][0]
        else:
            proyecto['partner_id_name'] = None
            proyecto['partner_id'] = None

        if proyecto['cn006_clasificacion_id']:
            proyecto['cn006_clasificacion_id_name'] = proyecto['cn006_clasificacion_id'][1]
            proyecto['cn006_clasificacion_id'] = proyecto['cn006_clasificacion_id'][0]
        else:
            proyecto['cn006_clasificacion_id_name'] = None
            proyecto['cn006_clasificacion_id'] = None
        
        if proyecto['cn006_grado_avance_id']:
            proyecto['cn006_grado_avance_id_name'] = proyecto['cn006_grado_avance_id'][1]
            proyecto['user_id'] = proyecto['cn006_grado_avance_id'][0]
        else:
            proyecto['cn006_grado_avance_id_name'] = None
            proyecto['cn006_grado_avance_id'] = None

        if proyecto['cn006_grado_complejidad_id']:
            proyecto['cn006_grado_complejidad_name'] = proyecto['cn006_grado_complejidad_id'][1]
            proyecto['cn006_grado_complejidad_id'] = proyecto['cn006_grado_complejidad_id'][0]
        else:
            proyecto['cn006_grado_complejidad_id_name'] = None
            proyecto['cn006_grado_complejidad_id'] = None
        
        if proyecto['cn006_nivel_importancia_id']:
            proyecto['cn006_nivel_importancia_id_name'] = proyecto['cn006_nivel_importancia_id'][1]
            proyecto['cn006_nivel_importancia_id'] = proyecto['cn006_nivel_importancia_id'][0]
        else:
            proyecto['cn006_nivel_importancia_id_name'] = None
            proyecto['cn006_nivel_importancia_id'] = None

        if proyecto['cn006_nivel_urgencia_id']:
            proyecto['cn006_nivel_urgencia_id_name'] = proyecto['cn006_nivel_urgencia_id'][1]
            proyecto['cn006_nivel_urgencia_id'] = proyecto['cn006_nivel_urgencia_id'][0]
        else:
            proyecto['cn006_nivel_urgencia_id_name'] = None
            proyecto['cn006_nivel_urgencia_id'] = None

        if proyecto['cn006_tamano_id']:
            proyecto['cn006_tamano_id_name'] = proyecto['cn006_tamano_id'][1]
            proyecto['cn006_tamano_id'] = proyecto['cn006_tamano_id'][0]
        else:
            proyecto['cn006_tamano_id_name'] = None
            proyecto['cn006_tamano_id'] = None
        #endregion Campos que son estructura

        #region Manejo de fechas
        for campo in campos_fecha:
            fecha = proyecto.get(campo)

            if not fecha:
                proyecto[campo] = None  # Si está en False, poner None
            else:
                # Convertir de string (Odoo) a datetime (Python) y dejarlo listo para Excel
                proyecto[campo] = datetime.strptime(fecha, "%Y-%m-%d")
        #endregion Manejo de fechas

    return proyectos


#endregion OBTENER PROYECTOS



################################################################################################################
# Lógica principal
################################################################################################################
def main(p_ambiente, p_debug) :
    """ Retorna todo_ok, 
    """
    
    
    try:

        #region Instanciar tools
        if p_debug:
            print("010 -  Llamada a inicializar clase")        

        tools = cCN006_globales(p_ambiente, p_debug)
        
        msj_debug("020 -  Retorno de inicializar clase", tools)
        #endregion Instanciar tools

        #region Autenticación con Odoo
        
        msj_debug(f"030 - Llamada autenticar_odoo", tools)

        if (not tools.autenticar_odoo()):
            print (f"(ERROR-010) Error de autenticación")
            return
        
        msj_debug(f"040 - Retorno autenticar_odoo", tools)
        #endregion Autenticación con Odoo
      
        #region Obtener proyectos que se procesarán
        msj_debug(f"050 - Llamando obtener_proyectos", tools)
        proyectos = []
        proyectos = obtener_proyectos(tools)
        msj_debug(f"060 - Regresando obtener_proyectos", tools)

        if len(proyectos) > 0:
            msj_debug(f"Se ecnontraron ({len(proyectos)}) registros de proyectos", tools)
        else:
            msj_debug(f"*** NO SE ENCONTRARON REGISTROS DE PROYECTOS", tools)
        
        # for proyecto in proyectos:
        #     print(f"ID: {proyecto['id']}, Nombre: {proyecto['name']}, Responsable: {proyecto.get('user_id', 'N/A')}")
        #endregion Obtener proyectos que se procesarán

    
        #region Obtener los IDs de partes de horas asociadas a proyectos
        msj_debug(f"070 - Listado de timesheets de todos los proyectos", tools)
        partes_horas_proyectos = []

        for proyecto in proyectos:
            partes_horas_proyectos.extend(proyecto.get('timesheet_ids', []))

        msj_debug(f"En total hay ({len(partes_horas_proyectos)}) partes de horas de proyectos\n", tools)
        #endregion Obtener los IDs de partes de horas asociadas a proyectos

        #region obtener datos de los partes de horas
        if not partes_horas_proyectos:
            print("No hay partes de horas para consultar.")
            return []


        msj_debug("Previo a consulta de detalle partes de horas en la base de datos", tools)
        detalles_partes_horas = []
        models = xmlrpc.client.ServerProxy(f"{tools.cnx_url}/xmlrpc/2/object")
        detalles_partes_horas = models.execute_kw(
            tools.cnx_db, tools.cnx_uid, tools.cnx_password,
            'account.analytic.line', 'search_read',
            [[('id', 'in', partes_horas_proyectos)]],
            {'fields': ['project_id','id', 'name', 'date', 'unit_amount', 'amount', 'user_id', 'account_id', 'task_id']}

        )

        detalles_partes_horas = [
            {f'ph_{key}': value for key, value in detalle.items()}
            for detalle in detalles_partes_horas
            ]   


        msj_debug("regreso de consulta de detalle de partes de horas en la base de datos", tools)

        for detalle in detalles_partes_horas:
            fecha = detalle.get('date')
            if not fecha:
                detalle['date'] = None  # Si está en False, poner None
            else:
                # Convertir de string (Odoo) a datetime (Python) y dejarlo listo para Excel
                detalle['date'] = datetime.strptime(fecha, "%Y-%m-%d")
            

        msj_debug("Estos son los registros de partes de horas", tools)
        for detalle in detalles_partes_horas:
            print(f"\n{detalle}")
        #endregion obtener datos de los partes de horas

        #region Unificar proyectos con sus partes de horas para el EXCEL
        
        proyectos_info_total = []

        for proyecto in proyectos:
            #partes_horas = [parte for parte in detalles_partes_horas if parte["ph_project_id"] == proyecto["id"]]
            partes_horas = [parte for parte in detalles_partes_horas if parte["ph_project_id"][0] == proyecto["id"]]

            # Escenario 1: Proyecto sin partes de horas
            if not partes_horas:
                proyectos_info_total.append({**proyecto, 
                                             "ph_project_id": None, 
                                             "ph_id": None, 
                                             "ph_name": None, 
                                             "ph_date": None,
                                             "ph_unit_amount": None, 
                                             "ph_amount": None,
                                             "ph_user_id": None, 
                                             "ph_account_id": None, 
                                             "ph_task_id": None
                                            }
                                             )

            # Escenario 2 y 3: Proyecto con una o más partes de horas
            else:
                for parte in partes_horas:
                    parte_convertida = parte.copy()
                    # Conversión de horas decimales a formato de tiempo para Excel
                    if parte_convertida.get("ph_unit_amount") is not None:
                        parte_convertida["ph_unit_amount"] = parte_convertida["ph_unit_amount"] / 24
                    
                    proyectos_info_total.append({**proyecto, **parte_convertida})

                    

        # Resultado final
        msj_debug(f"En total hay {len(proyectos_info_total)} registros combinados", tools)

        # for fila in proyectos_info_total:
        #     print(fila)

        #region Generar Excel
        msj_debug("Generando archivo excel", tools)
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet("Proyectos")
        
        # Encabezados
        msj_debug("Encabezado", tools)
        headers = list(proyectos_info_total[0].keys()) if proyectos_info_total else []
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)
        
        # Datos
        msj_debug("Detalle", tools)
        for row, proyecto in enumerate(proyectos_info_total, start=1):
            for col, header in enumerate(headers):
                valor = proyecto.get(header, "")
                if isinstance(valor, list):  
                    valor = ", ".join(map(str, valor))  # Convertir la lista en una cadena separada por comas
                worksheet.write(row, col, valor)

        
        msj_debug("workbook.close", tools)
        workbook.filename = "cn006_kpi.xlsx"
        workbook.close()
        msj_debug("output.seek", tools)
        output.seek(0)
        #endregion Generar Excel

        msj_debug(f"080 - Regresando agregar_partes_horas_por_lotes", tools)

        return detalles_partes_horas

    except Exception as e:
        print(f"\n\n*****   Error general en el proceso:\n>>>>>>>>\n{e}")
        return []


    # EXCEPCIONES - EXCEPCIONES - EXCEPCIONES - EXCEPCIONES - EXCEPCIONES - EXCEPCIONES - EXCEPCIONES - EXCEPCIONES - EXCEPCIONES - 
    except xmlrpc.client.ProtocolError as error:
        tools.asigna_error(f"Error de protocolo.  {error}|")
        print (f"|Todo Ok: {tools.g_todo_ok}\n*|* conexión: {tools.formatear_datos_conexion()}\n*|* msj: {tools.g_msj}|")            
        #return g_todo_ok, g_datos_conexion, g_msj
    except xmlrpc.client.Fault as error:
        tools.asigna_error(f"Error de RPC: {error}")
        print (f"|Todo Ok: {tools.g_todo_ok}\n*|* conexión: {tools.formatear_datos_conexion()}\n*|* msj: {tools.g_msj}|")            
        #return g_todo_ok, g_datos_conexion, g_msj
    except Exception as error:
        tools.asigna_error(f"Error general: {error}")
        print (f"|Todo Ok: {tools.g_todo_ok}\n*|* conexión: {tools.formatear_datos_conexion()}\n*|* msj: {tools.g_msj}|")            
        #return g_todo_ok, g_datos_conexion, g_msj

################################################################################################################
# FIN - Lógica principal
################################################################################################################


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script para obtener partes de horas desde Odoo.")

    # Instanciar cCN006_globales antes de usar str2bool
    tmp = cCN006_globales("DESA", False )

    parser.add_argument('--pAmbiente', type=str,                      nargs='?', const="DESA", default="DESA", help="Ambiente para ejecutar (DESA/PROD)")
    parser.add_argument('--pDebug',    type=tmp.str2bool, nargs='?', const=True,   default=False,  help="True - Despliega mensajes de seguimiento | False - para correr en producción")

    parser.set_defaults(pAmbiente="DESA", pDebug=False)

    args = parser.parse_args()
    args.pAmbiente = args.pAmbiente.upper()

    del tmp

    # Pasar la instancia globales a main
    main(args.pAmbiente, args.pDebug)
