import sys
import os
import io

import openpyxl
#from openpyxl.utils import get_column_letter
#from openpyxl.worksheet.table import Table, TableStyleInfo

import xmlrpc.client
import json
import argparse
import locale

import pytz
from pytz import timezone
from datetime import datetime, timedelta
from collections import defaultdict
import codecs

sys.path.append(os.path.abspath(".."))  # Agrega el directorio superior al path
from cn006_kpis_globales import cCN006_globales



######################################################################################################
#region GLOBALES
    ######################################################################################################
    #region Variables tipo fecha
COLUMNAS_FECHA = {
    "ph_date", "proy_cn006_fecha_cierre_estimada", "proy_cn006_fecha_cierre_oficial",
    "proy_cn006_fecha_cierre_sistema", "proy_cn006_fecha_creacion_oficial",
    "proy_cn006_fecha_creacion_sistema", "proy_cn006_fecha_entrega_informatica_estimada",
    "proy_cn006_fecha_entrega_informatica_oficial", "proy_cn006_fecha_entrega_informatica_sistema",
    "proy_cn006_fecha_entrega_usuario_estimada", "proy_cn006_fecha_entrega_usuario_oficial",
    "proy_cn006_fecha_entrega_usuario_sistema", "proy_cn006_fecha_inicio_oficial",
    'proy_cn006_fecha_gerencia_estimada','proy_cn006_fecha_gerencia_oficial','proy_cn006_fecha_gerencia_sistema',
    "proy_cn006_fecha_inicio_sistema", "proy_date", "proy_date_start",
    'Fecha Creación', 'Fecha Inicio', 'Fecha Informática', 'Fecha Gerencia', 'Fecha Cierre'
}

COLUMNAS_FECHA_HORA = {
    "ph_create_date", "ph_write_date", "proy_create_date", "proy_write_date"
}

DIAS_SEMANA = {1: "LUN", 2: "MAR", 3: "MIE", 4: "JUE", 5: "VIE", 6: "SAB", 7: "DOM"}
MESES = {
    1: "ENE", 2: "FEB", 3: "MAR", 4: "ABR", 5: "MAY", 6: "JUN",
    7: "JUL", 8: "AGO", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DIC"
}
    #endregion Variables tipo fecha
    ######################################################################################################
#endregion GLOBALES
######################################################################################################

def msj_debug (p_msj, p_tools: cCN006_globales):
    if p_tools.g_debug:
        print(p_msj)
    return

################################################################################################################
# Extracción de información
################################################################################################################

######################################################################################################
#region OBTENER PROYECTOS
def actualizar_fecha_gerencia(p_tools: cCN006_globales):
    models = xmlrpc.client.ServerProxy(f"{p_tools.cnx_url}/xmlrpc/2/object")

    # Obtener proyectos que cumplen las condiciones especificadas
    #  ('cn006_fecha_gerencia_oficial', '=', False),
    proyectos = models.execute_kw(
        p_tools.cnx_db, p_tools.cnx_uid, p_tools.cnx_password,
        'project.project', 'search_read',
        [[
            ('cn006_project', '=', True),
            ('cn006_stod_codigo', '!=', False),
            ('cn006_stod_codigo', '!=', 0)
        ]],
        {'fields': [
            'id', 'cn006_stod_codigo'
        ]}
    )

    ############################################################################################################
    #region Datos de referencia
    referencias = [
        {'cn006_stod_codigo': 275, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-01-31', 'cn006_fecha_gerencia_oficial': '2025-01-31'},
        {'cn006_stod_codigo': 276, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-10-31', 'cn006_fecha_gerencia_oficial': '2025-10-30'},
        {'cn006_stod_codigo': 277, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 2, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-01-31', 'cn006_fecha_gerencia_oficial': '2025-01-31'},
        {'cn006_stod_codigo': 278, 'cn006_emergente': True, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 3, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-01-28', 'cn006_fecha_gerencia_oficial': '2025-02-28'},
        {'cn006_stod_codigo': 279, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 3, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-02-28', 'cn006_fecha_gerencia_oficial': '2025-02-28'},
        {'cn006_stod_codigo': 280, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 3, 'cn006_nivel_urgencia_id': 3, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-03-28', 'cn006_fecha_gerencia_oficial': '2025-03-28'},
        {'cn006_stod_codigo': 281, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-03-28', 'cn006_fecha_gerencia_oficial': '2025-03-28'},
        {'cn006_stod_codigo': 282, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 3, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-02-28', 'cn006_fecha_gerencia_oficial': '2025-02-28'},
        {'cn006_stod_codigo': 283, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 2, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-01-31', 'cn006_fecha_gerencia_oficial': '2025-01-31'},
        {'cn006_stod_codigo': 284, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-04-30', 'cn006_fecha_gerencia_oficial': '2025-04-30'},
        {'cn006_stod_codigo': 285, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-01-31', 'cn006_fecha_gerencia_oficial': '2025-01-31'},
        {'cn006_stod_codigo': 286, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 2, 'cn006_nivel_urgencia_id': 2, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-02-28', 'cn006_fecha_gerencia_oficial': '2025-02-28'},
        {'cn006_stod_codigo': 287, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 2, 'cn006_nivel_urgencia_id': 2, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-02-28', 'cn006_fecha_gerencia_oficial': '2025-02-28'},
        {'cn006_stod_codigo': 288, 'cn006_emergente': True, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-01-31', 'cn006_fecha_gerencia_oficial': '2025-03-28'},
        {'cn006_stod_codigo': 289, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 3, 'cn006_nivel_urgencia_id': 3, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-03-28', 'cn006_fecha_gerencia_oficial': '2025-03-28'},
        {'cn006_stod_codigo': 290, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-01-31', 'cn006_fecha_gerencia_oficial': '2025-01-31'},
        {'cn006_stod_codigo': 291, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 3, 'cn006_nivel_urgencia_id': 3, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-04-14', 'cn006_fecha_gerencia_oficial': '2025-04-14'},
        {'cn006_stod_codigo': 292, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 2, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-01-31', 'cn006_fecha_gerencia_oficial': '2025-01-31'},
        {'cn006_stod_codigo': 293, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 2, 'cn006_nivel_urgencia_id': 2, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-03-28', 'cn006_fecha_gerencia_oficial': '2025-04-28'},
        {'cn006_stod_codigo': 294, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 2, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-04-14', 'cn006_fecha_gerencia_oficial': '2025-05-14'},
        {'cn006_stod_codigo': 295, 'cn006_emergente': True, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-02-14', 'cn006_fecha_gerencia_oficial': '2025-02-14'},
        {'cn006_stod_codigo': 296, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 3, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-03-14', 'cn006_fecha_gerencia_oficial': '2025-04-14'},
        {'cn006_stod_codigo': 297, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-02-14', 'cn006_fecha_gerencia_oficial': '2025-02-14'},
        {'cn006_stod_codigo': 298, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-02-03', 'cn006_fecha_gerencia_oficial': '2025-01-31'},
        {'cn006_stod_codigo': 299, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-02-14', 'cn006_fecha_gerencia_oficial': '2025-02-14'},
        {'cn006_stod_codigo': 300, 'cn006_emergente': True, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 2, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-03-10', 'cn006_fecha_gerencia_oficial': '2025-03-10'},
        {'cn006_stod_codigo': 301, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 3, 'cn006_nivel_urgencia_id': 3, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-03-28', 'cn006_fecha_gerencia_oficial': '2025-05-14'},
        {'cn006_stod_codigo': 302, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 3, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-02-28', 'cn006_fecha_gerencia_oficial': '2025-03-10'},
        {'cn006_stod_codigo': 303, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-02-28', 'cn006_fecha_gerencia_oficial': '2025-04-28'},
        {'cn006_stod_codigo': 304, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 3, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-02-14', 'cn006_fecha_gerencia_oficial': '2025-05-14'},
        {'cn006_stod_codigo': 305, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-03-10', 'cn006_fecha_gerencia_oficial': '2025-04-10'},
        {'cn006_stod_codigo': 307, 'cn006_emergente': True, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 2, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-01-31', 'cn006_fecha_gerencia_oficial': '2025-04-28'},
        {'cn006_stod_codigo': 308, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 3, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-02-28', 'cn006_fecha_gerencia_oficial': '2025-03-10'},
        {'cn006_stod_codigo': 309, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-01-31', 'cn006_fecha_gerencia_oficial': '2025-01-31'},
        {'cn006_stod_codigo': 310, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 2, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-02-24', 'cn006_fecha_gerencia_oficial': '2025-02-24'},
        {'cn006_stod_codigo': 312, 'cn006_emergente': True, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 2, 'cn006_nivel_urgencia_id': 2, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-01-31', 'cn006_fecha_gerencia_oficial': '2025-05-14'},
        {'cn006_stod_codigo': 313, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-02-21', 'cn006_fecha_gerencia_oficial': '2025-04-10'},
        {'cn006_stod_codigo': 314, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 2, 'cn006_nivel_urgencia_id': 2, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-02-14', 'cn006_fecha_gerencia_oficial': '2025-03-10'},
        {'cn006_stod_codigo': 315, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 3, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-02-28', 'cn006_fecha_gerencia_oficial': '2025-03-10'},
        {'cn006_stod_codigo': 316, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 2, 'cn006_nivel_urgencia_id': 2, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-02-14', 'cn006_fecha_gerencia_oficial': '2025-03-10'},
        {'cn006_stod_codigo': 317, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-02-14', 'cn006_fecha_gerencia_oficial': '2025-02-14'},
        {'cn006_stod_codigo': 318, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 2, 'cn006_nivel_urgencia_id': 2, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-02', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-02-24', 'cn006_fecha_gerencia_oficial': '2025-02-24'},
        {'cn006_stod_codigo': 319, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-03-28', 'cn006_fecha_gerencia_oficial': '2025-04-28'},
        {'cn006_stod_codigo': 320, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 3, 'cn006_nivel_urgencia_id': 3, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-04-14', 'cn006_fecha_gerencia_oficial': '2025-04-14'},
        {'cn006_stod_codigo': 321, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-01-31', 'cn006_fecha_gerencia_oficial': '2025-01-31'},
        {'cn006_stod_codigo': 322, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 3, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-04-14', 'cn006_fecha_gerencia_oficial': '2025-04-14'},
        {'cn006_stod_codigo': 323, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 3, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-03-28', 'cn006_fecha_gerencia_oficial': '2025-04-28'},
        {'cn006_stod_codigo': 324, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 2, 'cn006_nivel_urgencia_id': 2, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-03-28', 'cn006_fecha_gerencia_oficial': '2025-05-14'},
        {'cn006_stod_codigo': 325, 'cn006_emergente': True, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-01-31', 'cn006_fecha_gerencia_oficial': '2025-04-10'},
        {'cn006_stod_codigo': 326, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 2, 'cn006_nivel_urgencia_id': 2, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-03-28', 'cn006_fecha_gerencia_oficial': '2025-04-14'},
        {'cn006_stod_codigo': 327, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-02-14', 'cn006_fecha_gerencia_oficial': '2025-02-14'},
        {'cn006_stod_codigo': 328, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 2, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-01-31', 'cn006_fecha_gerencia_oficial': '2025-01-31'},
        {'cn006_stod_codigo': 329, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 2, 'cn006_nivel_urgencia_id': 2, 'cn006_tamano': 'PEQUEÑO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-02-14', 'cn006_fecha_gerencia_oficial': '2025-03-10'},
        {'cn006_stod_codigo': 330, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 2, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-03-28', 'cn006_fecha_gerencia_oficial': '2025-03-28'},
        {'cn006_stod_codigo': 331, 'cn006_emergente': True, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-01-31', 'cn006_fecha_gerencia_oficial': '2025-04-14'},
        {'cn006_stod_codigo': 332, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 2, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-02-14', 'cn006_fecha_gerencia_oficial': '2025-03-10'},
        {'cn006_stod_codigo': 333, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 2, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-01-31', 'cn006_fecha_gerencia_oficial': '2025-01-31'},
        {'cn006_stod_codigo': 334, 'cn006_emergente': True, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 3, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-01-31', 'cn006_fecha_gerencia_oficial': '2025-03-31'},
        {'cn006_stod_codigo': 335, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-01-31', 'cn006_fecha_gerencia_oficial': '2025-01-31'},
        {'cn006_stod_codigo': 336, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 3, 'cn006_nivel_urgencia_id': 2, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-02-28', 'cn006_fecha_gerencia_oficial': '2025-02-28'},
        {'cn006_stod_codigo': 337, 'cn006_emergente': True, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-01-24', 'cn006_fecha_gerencia_oficial': '2025-03-24'},
        {'cn006_stod_codigo': 338, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-01-31', 'cn006_fecha_gerencia_oficial': '2025-01-31'},
        {'cn006_stod_codigo': 339, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 2, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-02-28', 'cn006_fecha_gerencia_oficial': '2025-02-28'},
        {'cn006_stod_codigo': 340, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-02-28', 'cn006_fecha_gerencia_oficial': '2025-02-28'},
        {'cn006_stod_codigo': 341, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-07-31', 'cn006_fecha_gerencia_oficial': '2025-07-31'},
        {'cn006_stod_codigo': 342, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 3, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-03-28', 'cn006_fecha_gerencia_oficial': '2025-03-28'},
        {'cn006_stod_codigo': 343, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-04-13', 'cn006_fecha_gerencia_oficial': '2025-04-13'},
        {'cn006_stod_codigo': 344, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 3, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-02-28', 'cn006_fecha_gerencia_oficial': '2025-03-10'},
        {'cn006_stod_codigo': 345, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-04-13', 'cn006_fecha_gerencia_oficial': '2025-05-13'},
        {'cn006_stod_codigo': 346, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-01-31', 'cn006_fecha_gerencia_oficial': '2025-01-31'},
        {'cn006_stod_codigo': 347, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 3, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-02-28', 'cn006_fecha_gerencia_oficial': '2025-04-14'},
        {'cn006_stod_codigo': 348, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-01-31', 'cn006_fecha_gerencia_oficial': '2025-01-31'},
        {'cn006_stod_codigo': 349, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 3, 'cn006_nivel_urgencia_id': 3, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-03-10', 'cn006_fecha_gerencia_oficial': '2025-03-10'},
        {'cn006_stod_codigo': 350, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-02-14', 'cn006_fecha_gerencia_oficial': '2025-02-14'},
        {'cn006_stod_codigo': 351, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 3, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-02-28', 'cn006_fecha_gerencia_oficial': '2025-04-10'},
        {'cn006_stod_codigo': 352, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'GRANDE', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-01-31', 'cn006_fecha_gerencia_oficial': '2025-01-31'},
        {'cn006_stod_codigo': 353, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-01-31', 'cn006_fecha_gerencia_oficial': '2025-01-31'},
        {'cn006_stod_codigo': 354, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-03-31', 'cn006_fecha_gerencia_oficial': '2025-03-31'},
        {'cn006_stod_codigo': 359, 'cn006_emergente': True, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'BAJA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'PEQUEÑO', 'cn006_fecha_creacion_oficial': '2025-01-20', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-01-31', 'cn006_fecha_gerencia_oficial': '2025-01-31'},
        {'cn006_stod_codigo': 360, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 2, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-02-10', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-03-31', 'cn006_fecha_gerencia_oficial': '2025-03-31'},
        {'cn006_stod_codigo': 361, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-30', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-04-30', 'cn006_fecha_gerencia_oficial': '2025-04-30'},
        {'cn006_stod_codigo': 362, 'cn006_emergente': True, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 2, 'cn006_tamano': 'PEQUEÑO', 'cn006_fecha_creacion_oficial': '2025-01-20', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-01-24', 'cn006_fecha_gerencia_oficial': '2025-01-27'},
        {'cn006_stod_codigo': 363, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 2, 'cn006_nivel_urgencia_id': 2, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-22', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-02-05', 'cn006_fecha_gerencia_oficial': '2025-02-06'},
        {'cn006_stod_codigo': 366, 'cn006_emergente': True, 'cn006_clasificacion': 'REPORTE', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 0, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-01-31', 'cn006_fecha_gerencia_oficial': '2025-01-31'},
        {'cn006_stod_codigo': 367, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'BAJA', 'cn006_nivel_importancia_id': 2, 'cn006_nivel_urgencia_id': 2, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-28', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-02-28', 'cn006_fecha_gerencia_oficial': '2025-03-07'},
        {'cn006_stod_codigo': 368, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'BAJA', 'cn006_nivel_importancia_id': 1, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'PEQUEÑO', 'cn006_fecha_creacion_oficial': '2024-12-27', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-02-07', 'cn006_fecha_gerencia_oficial': '2025-02-07'},
        {'cn006_stod_codigo': 369, 'cn006_emergente': False, 'cn006_clasificacion': 'REPORTE', 'cn006_grado_complejidad': 'BAJA', 'cn006_nivel_importancia_id': 2, 'cn006_nivel_urgencia_id': 2, 'cn006_tamano': 'PEQUEÑO', 'cn006_fecha_creacion_oficial': '2025-01-28', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-02-12', 'cn006_fecha_gerencia_oficial': '2025-02-12'},
        {'cn006_stod_codigo': 370, 'cn006_emergente': True, 'cn006_clasificacion': 'SOPORTE/CAPACITACIÓN', 'cn006_grado_complejidad': 'BAJA', 'cn006_nivel_importancia_id': 0, 'cn006_nivel_urgencia_id': 2, 'cn006_tamano': 'PEQUEÑO', 'cn006_fecha_creacion_oficial': '2025-01-21', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-01-21', 'cn006_fecha_gerencia_oficial': '2025-01-31'},
        {'cn006_stod_codigo': 371, 'cn006_emergente': True, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 0, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-06', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-01-31', 'cn006_fecha_gerencia_oficial': '2025-01-31'},
        {'cn006_stod_codigo': 372, 'cn006_emergente': True, 'cn006_clasificacion': 'SOPORTE/CAPACITACIÓN', 'cn006_grado_complejidad': 'BAJA', 'cn006_nivel_importancia_id': 0, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'PEQUEÑO', 'cn006_fecha_creacion_oficial': '2025-01-16', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-01-18', 'cn006_fecha_gerencia_oficial': '2025-01-18'},
        {'cn006_stod_codigo': 373, 'cn006_emergente': True, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 0, 'cn006_nivel_urgencia_id': 1, 'cn006_tamano': 'MEDIANO', 'cn006_fecha_creacion_oficial': '2025-01-01', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-01-15', 'cn006_fecha_gerencia_oficial': '2025-01-18'},
        {'cn006_stod_codigo': 374, 'cn006_emergente': False, 'cn006_clasificacion': 'PROCESO', 'cn006_grado_complejidad': 'MEDIA', 'cn006_nivel_importancia_id': 3, 'cn006_nivel_urgencia_id': 2, 'cn006_tamano': 'GRANDE', 'cn006_fecha_creacion_oficial': '2025-01-31', 'cn006_fecha_inicio_oficial': '1900-01-01', 'cn006_fecha_entrega_informatica_oficial': '2025-02-28', 'cn006_fecha_gerencia_oficial': '2025-02-28'}
    ]
    #endregion Datos de referencia
    ############################################################################################################

    # Crear un diccionario para acceder rápidamente a las referencias por código
    ref_dict = {ref['cn006_stod_codigo']: ref for ref in referencias}

    # Actualizar proyectos con los datos correspondientes
    contador = 0
    for proyecto in proyectos:
        stod_codigo = proyecto.get('cn006_stod_codigo')
        if stod_codigo in ref_dict:
            contador += 1
            msj_debug(f"Actualizando ({contador}): STOD {stod_codigo}", p_tools)
            datos = ref_dict[stod_codigo]
            update_vals = {
                'cn006_emergente': datos['cn006_emergente'],
                'cn006_clasificacion_id': datos['cn006_clasificacion'],
                'cn006_grado_complejidad_id': datos['cn006_grado_complejidad'],
                'cn006_nivel_importancia_id': datos['cn006_nivel_importancia_id'],
                'cn006_nivel_urgencia_id': datos['cn006_nivel_urgencia_id'],
                'cn006_tamano_id': datos['cn006_tamano'],
                'cn006_fecha_creacion_oficial': datos['cn006_fecha_creacion_oficial'],
                'cn006_fecha_inicio_oficial': datos['cn006_fecha_inicio_oficial'],
                'cn006_fecha_entrega_informatica_oficial': datos['cn006_fecha_entrega_informatica_oficial'],
                'cn006_fecha_gerencia_oficial': datos['cn006_fecha_gerencia_oficial']
            }

            models.execute_kw(
                p_tools.cnx_db, p_tools.cnx_uid, p_tools.cnx_password,
                'project.project', 'write',
                [[proyecto['id']], update_vals]
            )

    return

#endregion OBTENER PROYECTOS
######################################################################################################

################################################################################################################
# Lógica principal
################################################################################################################
def main(p_ambiente, p_debug) :
    """  ****************************************************************************************
    ACTUALIZAR FECHA GERENCIA PARA PROYECTOS cn006_project = True y con código STOD
    ****************************************************************************************  """

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
        proyectos = actualizar_fecha_gerencia(tools)
        msj_debug(f"060 - Regresando obtener_proyectos", tools)

        return 

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
