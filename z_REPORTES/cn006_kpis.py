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
        
        for proyecto in proyectos:
            print(f"ID: {proyecto['id']}, Nombre: {proyecto['name']}, Responsable: {proyecto.get('user_id', 'N/A')}")
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


        msj_debug("Previo a consulta en la base de datos", tools)
        models = xmlrpc.client.ServerProxy(f"{tools.cnx_url}/xmlrpc/2/object")
        detalles_partes_horas = models.execute_kw(
            tools.cnx_db, tools.cnx_uid, tools.cnx_password,
            'account.analytic.line', 'search_read',
            [[('id', 'in', partes_horas_proyectos)]],
            {'fields': ['id', 'name', 'date', 'unit_amount', 'amount', 'user_id', 'account_id','project_id', 'task_id']}

        )

        msj_debug("regreso de consulta en la base de datos", tools)

        msj_debug("Estos son los registros de partes de horas", tools)
        for detalle in detalles_partes_horas:
            print(f"\n{detalle}")
        #endregion obtener datos de los partes de horas

        #region Unificar proyectos con sus partes de horas
        proyectos_info_total = []

        msj_debug("*****  Para verificar datos antes del merge", tools)
        msj_debug("\n\n\nProyectos\n", tools)
        for x in proyectos:
            print(x)

        msj_debug("\n\n\nPartes de horas\n", tools)
        for x in detalles_partes_horas:
            print(x)

        # Crear un diccionario con los proyectos por ID
        proyectos_dict = {p['id']: p for p in proyectos}

        msj_debug("Unificando la información de proyectos y partes de horas", tools)

        # Recorrer todas las partes de horas y combinarlas con su proyecto
        for parte in detalles_partes_horas:
            proyecto_id = parte.get('project_id')  # Usar project_id en lugar de account_id

            if isinstance(proyecto_id, list) and len(proyecto_id) > 0:
                proyecto_id = proyecto_id[0]  # Extraer solo el ID del proyecto

            # Obtener la información del proyecto desde proyectos_dict usando el project_id
            proyecto = proyectos_dict.get(proyecto_id, {})

            # Merge de proyecto con parte de horas
            proyectos_info_total.append({**proyecto, **parte})  # Añadir la parte de horas al proyecto

        # Para proyectos sin partes de horas, aseguramos que sean agregados con una lista vacía de partes de horas
        for proyecto_id, proyecto in proyectos_dict.items():
            # Verificar si ya se ha agregado un proyecto con partes de horas
            if not any(proyecto_id == parte.get('project_id')[0] for parte in detalles_partes_horas):
                # Si no tiene partes de horas, agregar el proyecto con una lista vacía de partes de horas
                proyectos_info_total.append({**proyecto, **{'partes_horas': []}})

        msj_debug("FIN Unificando la información de proyectos y partes de horas", tools)
        msj_debug("\n\n\nInformación en proyectos_info_total\n", tools)
        for info in proyectos_info_total:
            print(info)
        #endregion Unificar proyectos con sus partes de horas


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
        workbook.filename = "cn006_test.xlsx"
        workbook.close()
        msj_debug("output.seek", tools)
        output.seek(0)
        #endregion Generar Excel

        return detalles_partes_horas

    except Exception as e:
        print(f"\n\n*****   Error general en el proceso:\n>>>>>>>>\n{e}")
        return []



        msj_debug(f"080 - Regresando agregar_partes_horas_por_lotes", tools)

        

        return

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
