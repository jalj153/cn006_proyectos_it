import sys
import os
import xmlrpc.client

import argparse

from datetime import datetime
from collections import defaultdict


#sys.path.append(os.path.abspath(".."))  # Agrega el directorio superior al path

# Obtener la ruta absoluta del directorio del script
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(script_dir, "..")))

from cn006_kpis_globales import cCN006_globales



#region EXPLICACIÓN DEL PROCESO
"""  ******* EXPLICACIÓN DEL PROCESO
    
************************************************************************  """
#endregion

################################################################################################################
# Procesos específicos
################################################################################################################

def asignar_etapas_a_proyectos(p_tools):
    """Asignar todas las etapas de tareas que tienen cn006_task_type = True a los proyectos que les falta alguna etapa."""
    models = xmlrpc.client.ServerProxy(f"{p_tools.cnx_url}/xmlrpc/2/object")

    # Obtener las etapas de tareas con cn006_task_type = True
    p_tools.msj_debug(f"Obtener etapas: Previo a etapas tarea")
    etapa_model = 'project.task.type'
    etapa_ids = models.execute_kw(
        p_tools.cnx_db, 
        p_tools.cnx_uid, 
        p_tools.cnx_password,
        etapa_model, 
        'search',
        [[('cn006_task_type', '=', True)]]
    )
    p_tools.msj_debug(f"Obtener etapas: ya consultó etapas tarea.  Hay {len(etapa_ids)} etapas.")
    
    # Obtener todos los proyectos
    p_tools.msj_debug(f"Obtener proyectos: Previo a proyectos")
    proyecto_model = 'project.project'
    proyectos_ids = models.execute_kw(
        p_tools.cnx_db, 
        p_tools.cnx_uid, 
        p_tools.cnx_password,
        proyecto_model, 'search',
        [[('cn006_project', '=', True)]]
    )
    p_tools.msj_debug(f"Obtener proyectos: ya consultó los proyectos. Hay {len(proyectos_ids)} proyectos.")
    
    etapa_model = 'project.task.type'

    for etapa in etapa_ids:
        p_tools.msj_debug(f"Verificando etapa {etapa}")

        # Obtener los proyectos que ya tienen esta etapa asignada
        etapa_data = models.execute_kw(
            p_tools.cnx_db,
            p_tools.cnx_uid,
            p_tools.cnx_password,
            etapa_model, 'read',
            [etapa], {'fields': ['project_ids']}
        )

        proyectos_asignados = set(etapa_data[0]['project_ids']) if etapa_data else set()
        proyectos_faltantes = set(proyectos_ids) - proyectos_asignados
        p_tools.msj_debug(f"Hay {len(proyectos_faltantes)} proyectos faltantes en la etapa {etapa}.")

        if proyectos_faltantes:
            models.execute_kw(
                p_tools.cnx_db,
                p_tools.cnx_uid,
                p_tools.cnx_password,
                etapa_model, 'write',
                [[etapa], {'project_ids': [(4, proyecto) for proyecto in proyectos_faltantes]}]
            )
            p_tools.msj_debug(f"Se asignaron {len(proyectos_faltantes)} proyectos a la etapa {etapa}.")
        else:
            p_tools.msj_debug(f"La etapa {etapa} ya está asignada a todos los proyectos.")

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

        #region asignar etapas a proyectos
        tools.msj_debug(f"040 - Llamando asignar_etapas_a_proyectos")
        asignar_etapas_a_proyectos(tools)
        tools.msj_debug(f"050 - Retornó de asignar_etapas_a_proyectos")
        #endregion  asignar etapas a proyectos
        
        #endregion XMLs que se necesitan    

        return

    except Exception as e:
        print(f"\n\n*****   Error general (main) en el proceso:\n>>>>>>>>\n{e}")
        return []


    # EXCEPCIONES - EXCEPCIONES - EXCEPCIONES - EXCEPCIONES - EXCEPCIONES - EXCEPCIONES - EXCEPCIONES - EXCEPCIONES - EXCEPCIONES - 
    except xmlrpc.client.ProtocolError as error:
        tools.asigna_error(f"Error de protocolo.  {error}|")
        print (f"|Todo Ok: {tools.g_todo_ok}\n*|* conexión: {tools.formatear_datos_conexion()}\n*|* msj: {tools.g_msj}|")            
    except xmlrpc.client.Fault as error:
        tools.asigna_error(f"Error de RPC: {error}")
        print (f"|Todo Ok: {tools.g_todo_ok}\n*|* conexión: {tools.formatear_datos_conexion()}\n*|* msj: {tools.g_msj}|")            
    except Exception as error:
        tools.asigna_error(f"Error general: {error}")
        print (f"|Todo Ok: {tools.g_todo_ok}\n*|* conexión: {tools.formatear_datos_conexion()}\n*|* msj: {tools.g_msj}|")            

################################################################################################################
# FIN - Lógica principal
################################################################################################################


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script para asignar etapas de tareas a proyectos.")

    # Instanciar cCN006_globales antes de usar str2bool
    tmp = cCN006_globales("DESA", False )

    parser.add_argument('--pAmbiente', type=str,                      nargs='?', const="DESA", default="DESA", help="Ambiente para ejecutar (DESA/PROD)")
    parser.add_argument('--pDebug',    type=tmp.str2bool, nargs='?', const=True,   default=True,  help="True - Despliega mensajes de seguimiento | False - para correr en producción")

    parser.set_defaults(pAmbiente="DESA", pDebug=False)

    args = parser.parse_args()
    args.pAmbiente = args.pAmbiente.upper()

    del tmp

    if args.pAmbiente not in ["DESA", "PROD"]:
        raise ValueError("El valor de pAmbiente debe ser 'DESA' o 'PROD'.")

    # Pasar la instancia globales a main
    main(args.pAmbiente, args.pDebug)
