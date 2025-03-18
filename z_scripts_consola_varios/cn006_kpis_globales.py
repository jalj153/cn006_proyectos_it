from datetime import datetime
from typing import Literal

import argparse
import xmlrpc.client

class cCN006_globales:
    g_todo_ok = True
    g_datos_conexion = {}
    g_msj = ""
    g_debug = False

    cnx_url = ""
    cnx_db = ""
    cnx_user_name = ""
    cnx_password = ""
    cnx_uid = -1

    def __init__(self, p_ambiente: Literal[ 'DESA','PROD'], p_debug: bool = False):
        """
        Inicializa la clase con un ambiente específico.

        Parámetros:
            p_ambiente (str): 'PROD', 'DESA'

            p_debug: 
                True - Genera mensajes para debugear el código y el flujo
                False - No genera mensajes
        """

        self.g_debug = p_debug

        self.p_ambiente = p_ambiente.upper() if p_ambiente else ""
        self.cnx_ambiente = p_ambiente
        
        match p_ambiente:
            case "DESA":
                self.cnx_url = "https://canella-canellatest2-18823178.dev.odoo.com"
                self.cnx_db = "canella-canellatest2-18823178"
                self.cnx_user_name = "odoo_reportes@canella.com.gt"
                self.cnx_password = "2adb5989440eaad90ad2b706d69e311757d6d389"
            case "PROD":
                self.cnx_url = "https://canella.odoo.com"
                self.cnx_db = "piensom-canella1-main-7955386"
                self.cnx_user_name = "odoo_reportes@canella.com.gt"
                self.cnx_password = "2adb5989440eaad90ad2b706d69e311757d6d389"
            case _:
                self.cnx_ambiente = "ND"
        return
   
    def autenticar_odoo (self, p_context = None) -> bool: 
        if self.g_debug:
                print(f"\nIniciando autenticar_odoo ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})")

        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.cnx_url), context=p_context)
        uid = common.authenticate(self.cnx_db, self.cnx_user_name, self.cnx_password, {})
        self.cnx_uid = uid if uid else -1
        
        self.g_todo_ok = self.cnx_uid > -1

        if self.g_debug:
            if self.g_todo_ok:
                print(f"Autenticación exitosa ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})")
            else:
                print(f"Hubo un error al autenticar ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})")

            print(f"\nFinalizado autenticar_odoo\nDatos de autenticación:\n{self.formatear_datos_conexion()}")
        return self.g_todo_ok

    def asigna_error (self, p_msj: str):
        if self.g_debug:
            print(f"\n*** Voy a asignar error:\n")
            print(f"Este es el mensaje que recibo:\n******\n{p_msj}\******")

        self.g_todo_ok = False
        if self.g_msj:  # Si ya tiene valor, concatenar con formato
            self.g_msj += "\n>>>>>  *****\n" + p_msj
        else:  # Si está vacío, asignar directamente
            self.g_msj = p_msj
        return 

    def formatear_datos_conexion(self):
        conexion = f"URL ({self.cnx_url})\nDB ({self.cnx_db})\nUSUARIO ({self.cnx_user_name})\nUID ({self.cnx_uid})"
        return conexion

    def msj_debug (self, p_msj):
        if self.g_debug:
            print(p_msj)
        return


    def str2bool(self, v):
        if isinstance(v, bool):
            return v
        if v.lower() in ('yes', 'true', 't', 'y', '1','verdadero','v','si'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0','falso','f'):
            return False
        else:
            raise argparse.ArgumentTypeError(f'Se espera un valor que represente un booleano y se tiene ({v}).')



 

# def clean_newlines(record):
#     global g_todo_ok, g_datos_conexion, g_msj, g_debug
#     for key in record:
#         if isinstance(record[key], str):
#             record[key] = record[key].replace('\n', ' ** ')
#     return record





# def convertir_gtc_a_utc (p_fecha, p_tipo):
#     global g_todo_ok, datos_conexion, msj

#     if g_debug:
#         print(f"\nIniciando convertir_gtc_a_utc p_fecha: {p_fecha} p_tipo: {p_tipo}")

#     guatemala_tz = pytz.timezone('America/Guatemala')
#     utc_tz = pytz.utc
    
#     p_tipo = p_tipo.upper()

#     if len(p_fecha) == 10:
#         if p_tipo == "INI":
#             p_fecha = datetime.strptime(p_fecha + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
#         else:
#             p_fecha = datetime.strptime(p_fecha + ' 23:59:59', '%Y-%m-%d %H:%M:%S')



#     p_fecha = guatemala_tz.localize(p_fecha)
#     p_fecha = p_fecha.astimezone(utc_tz)

#     if g_debug:
#         print(f"\nFinalizado convertir_gtc_a_utc p_fecha: {p_fecha} p_tipo: {p_tipo}")

#     return p_fecha




