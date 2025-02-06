import sys
import os
sys.path.append(os.path.abspath(".."))  # Agrega el directorio superior al path


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
    1. En la actualización a producción hay varios cambios a la base de datos.  Es importante hacer actualizaciones.
    2. Pasos que se realizarán
        a. 
************************************************************************  """
#endregion

################################################################################################################
# Procesos específicos
################################################################################################################

def agregar_etapas_a_proyectos(p_tools: cCN006_globales):
    try:
        p_tools.msj_debug(f"\n\n*****  INICIANDO agregar_etapas_a_proyectos")

        models = xmlrpc.client.ServerProxy(f"{p_tools.cnx_url}/xmlrpc/2/object")

        p_tools.msj_debug(f"\nINICIO - Obtener todos los proyectos donde cn006_project = True")
        proyectos = models.execute_kw(
            p_tools.cnx_db, p_tools.cnx_uid, p_tools.cnx_password,
            'project.project', 'search_read',
            [[('cn006_project', '=', True)]],
            {'fields': ['id']}
        )
        p_tools.msj_debug(f"FINALIZADO - Obtener todos los proyectos donde cn006_project = True")
        p_tools.msj_debug(f"Se identificaron {len(proyectos)} del módulo CN006\n")

        p_tools.msj_debug(f"INICIO - Obtener todas las etapas de tarea donde cn006_task_type = True")
        etapas_tareas = models.execute_kw(
            p_tools.cnx_db, p_tools.cnx_uid, p_tools.cnx_password,
            'project.task.type', 'search_read',
            [[('cn006_task_type', '=', True)]],
            {'fields': ['id']}
        )
        p_tools.msj_debug(f"FINALIZADO - Obtener todas las etapas de tarea donde cn006_task_type = True")
        p_tools.msj_debug(f"Se identificaron {len(etapas_tareas)} del módulo CN006\n")

        # Extraer los IDs de proyectos y etapas
        proyecto_ids = [p['id'] for p in proyectos]
        etapa_ids = [e['id'] for e in etapas_tareas]

        # Asignar todas las etapas a cada proyecto
        p_tools.msj_debug(f"Se asignarán ({len(etapas_tareas)}) etapas de tareas a cada uno de los proyectos ({len(proyectos)})")
        p_tools.msj_debug(f"INICIO - Ciclo para asignar ({len(etapas_tareas)}) etapas de tareas a cada uno de los proyectos ({len(proyectos)})")
        
        for proyecto_id in proyecto_ids:
            models.execute_kw(
                p_tools.cnx_db, p_tools.cnx_uid, p_tools.cnx_password,
                'project.project', 'write',
                [[proyecto_id], {'type_ids': [(6, 0, etapa_ids)]}]
            )

        p_tools.msj_debug(f"FINALIZADO - Ciclo para asignar ({len(etapas_tareas)}) etapas de tareas a cada uno de los proyectos ({len(proyectos)})")
        p_tools.msj_debug(f"Se asignaron {len(etapa_ids)} etapas a {len(proyecto_ids)} proyectos.\n")

        p_tools.msj_debug(f"*****  FINALIZADO agregar_etapas_a_proyectos\n\n")

    except Exception as e:
        print(f"\n\n*****   Error en agregar_etapas_a_proyectos:\n>>>>>>>>\n{e}")
        return []


################################################################################################################
# Lógica principal
################################################################################################################
def main(p_ambiente, p_debug) :
    try:

        #region Instanciar tools
        if p_debug:
            print("010 -  Llamada a inicializar clase")        

        tools = cCN006_globales(p_ambiente, p_debug)
        
        tools.msj_debug("020 -  Retorno de inicializar clase")
        #endregion Instanciar tools

        #region Autenticación con Odoo
        tools.msj_debug(f"010 - Llamada autenticar_odoo")

        if (not tools.autenticar_odoo()):
            print (f"(ERROR-020) Error de autenticación")
            return
        
        tools.msj_debug(f"030 - Retorno autenticar_odoo")
        #endregion Autenticación con Odoo

        #region Realizar actualizaciones
        
        agregar_etapas_a_proyectos(tools)

        #endregion Realizar actualizaciones

        return

    except Exception as e:
        print(f"\n\n*****   Error general (main) en el proceso:\n>>>>>>>>\n{e}")
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

    if args.pAmbiente not in ["DESA", "PROD"]:
        raise ValueError("El valor de pAmbiente debe ser 'DESA' o 'PROD'.")

    # Pasar la instancia globales a main
    main(args.pAmbiente, args.pDebug)
