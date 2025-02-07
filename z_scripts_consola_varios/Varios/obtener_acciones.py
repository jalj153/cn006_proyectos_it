import sys
import os

#sys.path.append(os.path.abspath(".."))  # Agrega el directorio superior al path

# Obtener la ruta absoluta del directorio del script
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(script_dir, "..")))



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
    
************************************************************************  """
#endregion

################################################################################################################
# Procesos específicos
################################################################################################################

def obtener_acciones(p_action_xml_id, p_tools: cCN006_globales):
    print("\n***  Iniciando obtener_acciones")
    models = xmlrpc.client.ServerProxy(f"{p_tools.cnx_url}/xmlrpc/2/object")
    modulo_id, action_id = p_action_xml_id.split('.')

    # Buscar el ID real en ir.model.data
    model_data = models.execute_kw(
        p_tools.cnx_db, 
        p_tools.cnx_uid, 
        p_tools.cnx_password,
        'ir.model.data', 
        'search_read', 
        [[['module', '=', modulo_id], ['name', '=', action_id], ['model', '=', 'ir.actions.act_window']]],
        {'limit': 1, 'fields': ['res_id']}
    )

    if model_data:
        action_id = model_data[0]['res_id']

        # Buscar la acción en ir.actions.act_window usando el ID real
        action = models.execute_kw(
            p_tools.cnx_db, 
            p_tools.cnx_uid, 
            p_tools.cnx_password,
            'ir.actions.act_window', 
            'search_read', 
            [[['id', '=', action_id]]], 
            {'limit': 1}
        )
    else:
        action = None  # No se encontró la acción

    print(f"\n\n*****DETALLE DEL CONTENIDO DEL ACTION\n\n{action}\n\n**** FIN DEL ACTION")


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

        #region 
        #obtener_acciones("project.act_project_project_2_project_task_all", tools)
        obtener_acciones("cn006_proyectos_it.cn006_action_project_task_view_kanban", tools)
        
        #endregion
        
        #endregion XMLs que se necesitan    

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
