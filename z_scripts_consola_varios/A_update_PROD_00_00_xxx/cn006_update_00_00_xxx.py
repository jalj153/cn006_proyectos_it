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



################################################################################################################
#region Procesos específicos
################################################################################################################
     ############################################################################################################
    #region actualizar_fecha_gerencia
def actualizar_fecha_gerencia(p_tools: cCN006_globales):
    """Actualiza el campo cn006_fecha_gerencia_oficial
    con el valor de cn006_fecha_entrega_usuario_oficial
    para todos los proyectos donde cn006_project = True.
    """

    try:
        p_tools.msj_debug(f"\n\n>>>>>***********************************************************")
        p_tools.msj_debug(f"*****  INICIANDO actualizar_fecha_gerencia\n\n")

        models = xmlrpc.client.ServerProxy(f"{p_tools.cnx_url}/xmlrpc/2/object")

        # Buscar todos los proyectos donde cn006_project = True
        project_ids = models.execute_kw(
            p_tools.cnx_db, p_tools.cnx_uid, p_tools.cnx_password,
            'project.project', 'search',
            [[('cn006_project', '=', True)]]
        )

        if not project_ids:
            p_tools.msj_debug("No se encontraron proyectos con cn006_project=True.")
            return

        # Leer los valores actuales de cn006_fecha_entrega_usuario_oficial para los proyectos encontrados
        proyectos = models.execute_kw(
            p_tools.cnx_db, p_tools.cnx_uid, p_tools.cnx_password,
            'project.project', 'read',
            [project_ids, ['cn006_fecha_entrega_usuario_oficial']]
        )

        # Actualizar el campo cn006_fecha_gerencia_oficial con el valor de cn006_fecha_entrega_usuario_oficial
        for proyecto in proyectos:
            project_id = proyecto.get('id')
            fecha_entrega = proyecto.get('cn006_fecha_entrega_usuario_oficial')

            if fecha_entrega:
                try:
                    result = models.execute_kw(
                        p_tools.cnx_db, p_tools.cnx_uid, p_tools.cnx_password,
                        'project.project', 'write',
                        [[project_id], {'cn006_fecha_gerencia_oficial': fecha_entrega}]
                    )
                    if result:
                        p_tools.msj_debug(f"Proyecto {project_id} actualizado con fecha: {fecha_entrega}")
                    else:
                        p_tools.msj_debug(f"No se pudo actualizar el proyecto {project_id}.")
                except Exception as e:
                    p_tools.msj_debug(f"Error al actualizar el proyecto {project_id}: {e}")
            else:
                p_tools.msj_debug(f"El proyecto {project_id} no tiene definida la fecha de entrega de usuario oficial.")

        p_tools.msj_debug(f"\n\n*****  FINALIZADO actualizar_fecha_gerencia\n\n")
        p_tools.msj_debug(f">>>>>***********************************************************\n")

    except Exception as e:
        p_tools.msj_debug(f"\n\n*****   Error en método (actualizar_fecha_gerencia):\n>>>>>>>>\n{e}")
        return []

    #endregion Actualizar actualizar_fecha_gerencia
    ############################################################################################################   

    ############################################################################################################
    #region agregar_codigo_stod_a_proyectos
def agregar_codigo_stod_a_proyectos(p_tools: cCN006_globales):
    """Actualiza el campo cn006_stod_codigo en project.project según la lista proporcionada."""

    try:
        p_tools.msj_debug(f"\n\n>>>>>***********************************************************")
        p_tools.msj_debug(f"*****  INICIANDO agregar_codigo_stod_a_proyectos\n\n")

        models = xmlrpc.client.ServerProxy(f"{p_tools.cnx_url}/xmlrpc/2/object")

        # Lista de pares: proyectos_odoo -> proyectos_stod
        proyectos_a_actualizar = [
            (8250, 279), (8269, 290), (8303, 292), (8263, 296), (8302, 297), (8259, 298), (8260, 299), (8264, 301),
            (8262, 302), (8330, 303), (8261, 304), (8258, 307), (8252, 308), (8253, 310), (8247, 313), (8331, 319),
            (8270, 321), (8316, 325), (8288, 329), (8238, 330), (8304, 332), (8276, 334), (8268, 335), (8277, 336),
            (8273, 338), (8278, 339), (8280, 340), (8306, 342), (8305, 344), (8294, 361), (8256, 362), (8247, 363),
            (8301, 366), (8281, 369), (8299, 370), (8300, 371), (8298, 372)
        ]

        # Actualizar los proyectos con los códigos STOD
        for project_id, stod_code in proyectos_a_actualizar:
            try:
                p_tools.msj_debug(f"Actualizando proyecto ID: {project_id} con STOD: {stod_code}")

                # Verificar si el proyecto existe antes de actualizar
                project_exists = models.execute_kw(
                    p_tools.cnx_db, p_tools.cnx_uid, p_tools.cnx_password,
                    'project.project', 'search',
                    [[('id', '=', project_id)]]
                )

                if project_exists:
                    result = models.execute_kw(
                        p_tools.cnx_db, p_tools.cnx_uid, p_tools.cnx_password,
                        'project.project', 'write',
                        [[project_id], {'cn006_stod_codigo': stod_code}]
                    )
                    if result:
                        p_tools.msj_debug(f"Proyecto {project_id} actualizado correctamente.")
                    else:
                        p_tools.msj_debug(f"No se pudo actualizar el proyecto {project_id}.")
                else:
                    p_tools.msj_debug(f"El proyecto con ID {project_id} no existe.")

            except Exception as e:
                p_tools.msj_debug(f"Error al actualizar el proyecto {project_id}: {e}")

        p_tools.msj_debug(f"\n\n*****  FINALIZADO agregar_codigo_stod_a_proyectos\n\n")
        p_tools.msj_debug(f">>>>>***********************************************************\n")

    except Exception as e:
        p_tools.msj_debug(f"\n\n*****   Error en método (agregar_codigo_stod_a_proyectos):\n>>>>>>>>\n{e}")
        return []
    
    #endregion Actualizar STOD_codigo en proyectos existentes
    ############################################################################################################

    ############################################################################################################
    #region agregar_proyectos
def agregar_proyectos(p_tools: cCN006_globales):
    """Actualiza el campo cn006_fecha_gerencia_oficial
    con el valor de cn006_fecha_entrega_usuario_oficial
    para todos los proyectos donde cn006_project = True.
    """

    try:
        p_tools.msj_debug(f"\n\n>>>>>***********************************************************")
        p_tools.msj_debug(f"*****  INICIANDO agregar_proyectos\n\n")

        models = xmlrpc.client.ServerProxy(f"{p_tools.cnx_url}/xmlrpc/2/object")

        # Buscar todos los proyectos donde cn006_project = True
        project_ids = models.execute_kw(
            p_tools.cnx_db, p_tools.cnx_uid, p_tools.cnx_password,
            'project.project', 'search',
            [[('cn006_project', '=', True)]]
        )

        
        p_tools.msj_debug(f"\n\n*****  FINALIZADO agregar_proyectos\n\n")
        p_tools.msj_debug(f">>>>>***********************************************************\n")

    except Exception as e:
        p_tools.msj_debug(f"\n\n*****   Error en método (agregar_proyectos):\n>>>>>>>>\n{e}")
        return []

    #endregion agregar_proyectos
    ############################################################################################################   

#endregion Procesos específicos
################################################################################################################

################################################################################################################
#region Lógica principal
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
        tools.msj_debug(f"\n030 - Llamada autenticar_odoo")

        if (not tools.autenticar_odoo()):
            print (f"(ERROR-040) Error de autenticación")
            return
        
        tools.msj_debug(f"050 - Retorno autenticar_odoo")
        #endregion Autenticación con Odoo

        #***********************************************************
        #region Actualizar cn006_fecha_gerencia
        tools.msj_debug(f"\n060 - Llamada actualizar_fecha_gerencia")
        actualizar_fecha_gerencia(tools)
        tools.msj_debug(f"070 - Retorno actualizar_fecha_gerencia")
        #endregion Actualizar cn006_fecha_gerencia
        #***********************************************************
        
        #***********************************************************
        #region Actualizar STOD_codigo en proyectos existentes
        tools.msj_debug(f"\n080 - Llamada agregar_codigo_stod_a_proyectos")
        agregar_codigo_stod_a_proyectos(tools)
        tools.msj_debug(f"090 - Retorno agregar_codigo_stod_a_proyectos")
        #endregion Actualizar STOD_codigo en proyectos existentes
        #***********************************************************

        #***********************************************************
        #region Agregar proyectos
        #endregion Agregar proyectos
        #***********************************************************



        

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
#endregion Lógica principal
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
