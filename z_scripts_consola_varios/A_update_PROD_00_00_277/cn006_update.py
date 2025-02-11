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

def agregar_etapas_proyectos_a_proyectos(p_tools: cCN006_globales):
    """Agrega todas las etapas de proyectos CN006 a los proyectos CN006"""
    try:
        p_tools.msj_debug(f"\n\n>>>>>***********************************************************")
        p_tools.msj_debug(f">>>>>***********************************************************")
        p_tools.msj_debug(f">>>>>***********************************************************")
        p_tools.msj_debug(f"*****  INICIANDO agregar_etapas_a_proyectos")

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

        p_tools.msj_debug(f"\n\n*****  FINALIZADO agregar_etapas_a_proyectos")
        p_tools.msj_debug(f">>>>>***********************************************************")
        p_tools.msj_debug(f">>>>>***********************************************************")
        p_tools.msj_debug(f">>>>>***********************************************************\n")

    except Exception as e:
        print(f"\n\n*****   Error en agregar_etapas_a_proyectos:\n>>>>>>>>\n{e}")
        return []


def agregar_etapas_tareas_a_proyectos(p_tools: cCN006_globales):
    """Agrega todas las etapas de tareas CN006 a los proyectos CN006"""
    try:
        p_tools.msj_debug(f"\n\n>>>>>***********************************************************")
        p_tools.msj_debug(f">>>>>***********************************************************")
        p_tools.msj_debug(f">>>>>***********************************************************")
        p_tools.msj_debug(f"*****  INICIANDO agregar_etapas_tareas_a_proyectos\n\n")

        models = xmlrpc.client.ServerProxy(f"{p_tools.cnx_url}/xmlrpc/2/object")

        p_tools.msj_debug(f"Obtener todas las etapas de tareas con cn006_task_type = True")
        task_stage_ids = models.execute_kw(
            p_tools.cnx_db, p_tools.cnx_uid, p_tools.cnx_password,
            'project.task.type', 'search',
            [[('cn006_task_type', '=', True)]]
        )
        p_tools.msj_debug(f"Finalizó obtención etapas de tareas con cn006_task_type = True")
        p_tools.msj_debug(f"Registros obtenidos: {len(task_stage_ids)}\n")

        p_tools.msj_debug(f"Obtener todos los proyectos con cn006_project = True")
        project_ids = models.execute_kw(
            p_tools.cnx_db, p_tools.cnx_uid, p_tools.cnx_password,
            'project.project', 'search',
            [[('cn006_project', '=', True)]]
        )
        p_tools.msj_debug(f"Finalizó obtención todos los proyectos con cn006_project = True")
        p_tools.msj_debug(f"Registros obtenidos: {len(project_ids)}\n")

        p_tools.msj_debug(f"\nINICIO - Ciclo para asignar ({len(project_ids)}) proyectos a cada una de las etapas  ({len(task_stage_ids)})")
        if task_stage_ids and project_ids:
            # Asignar los proyectos a cada etapa de tarea
            for stage_id in task_stage_ids:
                models.execute_kw(
                    p_tools.cnx_db, p_tools.cnx_uid, p_tools.cnx_password,
                    'project.task.type', 'write',
                    [[stage_id], {'project_ids': [(6, 0, project_ids)]}]
                )
            p_tools.msj_debug(f"FINALIZADO - Ciclo para asignar ({len(project_ids)}) proyectos a cada una de las etapas  ({len(task_stage_ids)})\n")
            p_tools.msj_debug(f"Se han asignado {len(project_ids)} proyectos a {len(task_stage_ids)} etapas de tareas.")
        else:
            p_tools.msj_debug("No se encontraron proyectos o etapas de tareas con los criterios especificados.")


        p_tools.msj_debug(f"\n\n*****  FINALIZADO agregar_etapas_tareas_a_proyectos\n\n")
        p_tools.msj_debug(f">>>>>***********************************************************")
        p_tools.msj_debug(f">>>>>***********************************************************")
        p_tools.msj_debug(f">>>>>***********************************************************\n")

    except Exception as e:
        print(f"\n\n*****   Error en agregar_etapas_a_proyectos:\n>>>>>>>>\n{e}")
        return []

def actualizar_etapas_tareas_y_tipificacion(p_tools):
    """Agrega todas las etapas de tareas CN006 a los proyectos CN006 y actualiza la tipificación."""
    try:
        p_tools.msj_debug(f"\n\n>>>>>***********************************************************")
        p_tools.msj_debug(f">>>>>***********************************************************")
        p_tools.msj_debug(f">>>>>***********************************************************")
        p_tools.msj_debug(f"*****  INICIANDO actualizar_etapas_tareas_y_tipificacion\n\n")

        models = xmlrpc.client.ServerProxy(f"{p_tools.cnx_url}/xmlrpc/2/object")

        # Obtener todos los proyectos donde cn006_project = True
        p_tools.msj_debug("Obteniendo proyectos con cn006_project = True...")
        project_ids = models.execute_kw(
            p_tools.cnx_db, p_tools.cnx_uid, p_tools.cnx_password,
            'project.project', 'search',
            [[('cn006_project', '=', True)]]
        )

        if not project_ids:
            p_tools.msj_debug("No se encontraron proyectos CN006. Finalizando...")
            return

        # Obtener todas las tareas de esos proyectos
        p_tools.msj_debug("Obteniendo todas las tareas de los proyectos CN006...")
        task_ids = models.execute_kw(
            p_tools.cnx_db, p_tools.cnx_uid, p_tools.cnx_password,
            'project.task', 'search_read',
            [[('project_id', 'in', project_ids)]],
            {'fields': ['id', 'name', 'stage_id']}
        )

        if not task_ids:
            p_tools.msj_debug("No se encontraron tareas en los proyectos CN006. Finalizando...")
            return

        # Definir mapeo de stages
        stage_mapping = {
            564: 643,
            638: 644,
            565: 645,
            566: 647
        }
        cn006_tipificacion_id = 2  # ID de la tipificación DESARROLLO

        # Procesar y actualizar tareas
        tareas_actualizadas = 0
        for task in task_ids:
            task_id = task['id']
            task_name = task['name']
            stage_id = task['stage_id'][0] if task['stage_id'] else None

            if stage_id in stage_mapping:
                new_stage_id = stage_mapping[stage_id]

                # Actualizar la tarea con el nuevo stage y la tipificación
                models.execute_kw(
                    p_tools.cnx_db, p_tools.cnx_uid, p_tools.cnx_password,
                    'project.task', 'write',
                    [[task_id], {'stage_id': new_stage_id, 'cn006_tipificacion_id': cn006_tipificacion_id}]
                )

                tareas_actualizadas += 1
                p_tools.msj_debug(f"Tarea {task_id} ({task_name}) actualizada: {stage_id} → {new_stage_id}, Tipificación → {cn006_tipificacion_id}")
            else:
                p_tools.msj_debug(f"⚠️ Tarea {task_id} ({task_name}) en stage {stage_id}, fuera del rango mapeado. No se actualiza.")

        p_tools.msj_debug(f"\n\n✅ Proceso finalizado. Tareas actualizadas: {tareas_actualizadas}\n")
        p_tools.msj_debug(f">>>>>***********************************************************")
        p_tools.msj_debug(f">>>>>***********************************************************")
        p_tools.msj_debug(f">>>>>***********************************************************\n")

    except Exception as e:
        print(f"\n\n*****   Error en actualizar_etapas_tareas_y_tipificacion:\n>>>>>>>>\n{e}")

def convertir_subtareas_a_tareas(p_tools: cCN006_globales):
    """Convierte todas las subtareas de proyectos CN006=True en tareas normales"""
    try:
        p_tools.msj_debug(f"\n\n>>>>>***********************************************************")
        p_tools.msj_debug(f">>>>>***********************************************************")
        p_tools.msj_debug(f">>>>>***********************************************************")
        p_tools.msj_debug(f"*****  INICIANDO convertir_subtareas_a_tareas\n\n")

        models = xmlrpc.client.ServerProxy(f"{p_tools.cnx_url}/xmlrpc/2/object")

        # Obtener todas las tareas de proyectos donde cn006_project = True y que sean subtareas
        p_tools.msj_debug(f"Obteniendo todas las subtareas de proyectos CN006")
        task_ids = models.execute_kw(
            p_tools.cnx_db, p_tools.cnx_uid, p_tools.cnx_password,
            'project.task', 'search',
            [[('project_id.cn006_project', '=', True), ('parent_id', '!=', False)]]
        )
        
        if not task_ids:
            p_tools.msj_debug(f"No se encontraron subtareas para convertir.")
        else:
            p_tools.msj_debug(f"Se encontraron {len(task_ids)} subtareas a convertir.")
            
            # Actualizar las tareas para eliminar el parent_id
            success = models.execute_kw(
                p_tools.cnx_db, p_tools.cnx_uid, p_tools.cnx_password,
                'project.task', 'write',
                [task_ids, {'parent_id': False}]
            )
            
            if success:
                p_tools.msj_debug(f"Se convirtieron correctamente {len(task_ids)} subtareas en tareas normales.")
            else:
                p_tools.msj_debug(f"Error al actualizar algunas tareas.")
        
        p_tools.msj_debug(f"\n\n*****  FINALIZADO convertir_subtareas_a_tareas\n\n")
        p_tools.msj_debug(f">>>>>***********************************************************")
        p_tools.msj_debug(f">>>>>***********************************************************")
        p_tools.msj_debug(f">>>>>***********************************************************\n")

    except Exception as e:
        p_tools.msj_debug(f"\n\n*****   Error en convertir_subtareas_a_tareas:\n>>>>>>>>\n{e}")
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
        
        # Agrega todas las etapas_proyectos CN006 a proyectos CN006
        # Ejecutado
        # agregar_etapas_proyectos_a_proyectos(tools)

        # Agrega todas las etapas_tareas CN006 a proyectos CN006
        # Ejecutado
        # agregar_etapas_tareas_a_proyectos (tools)

        # Combinar todos los proyectos CN006 en D25, D50, D75, D100 para DESARROLLO
        # Esto se hizo manualmente porque son pocos proyectos

        # Mover las tareas de proyectos CN006 de etapas anteriores a las nuevas etapas de tarea
        # Ejecutado
        # actualizar_etapas_tareas_y_tipificacion(tools)


        # Convertir los subtasks de proyecto CN006 en tareas normales
        # convertir_subtareas_a_tareas(tools)

        

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
