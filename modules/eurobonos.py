# ---- Libraries ----
import numpy as np
import pandas as pd
import datetime
from bizdays import Calendar

from Code.fechas import *


# ---- Calendarios ----

# Sección donde se cargan los calendarios necesarios en el proceso de generación
# de fechas cupón

mx_cal = Calendar.load(name = 'mx_calendar', filename = 'Data/df_holidays_mx.cal')

# ---- Funciones ----

    
# ---- Cálculo del Flujo i ----
# No se está incluyendo cuando es tasa variable 
    
def calcula_flujo_euro(vn, tipo_tasa, convencion, tasa_cupon, dias_cupon, cupones_anuales, n_cupon, n_total):
    
    flujo = 0
    
    # Cálculo de flujos para instrumentos con tasa fija tomando en cuenta
    # diferentes convenciones de cuenta de días.
    
    if tipo_tasa == 'fija':
        
        if convencion == 'actual/360':
            
            if n_cupon == n_total:
                
                flujo = (vn * dias_cupon * tasa_cupon / 360) + vn
            
            elif n_cupon < n_total:
                
                flujo = vn * dias_cupon * tasa_cupon / 360
                
            else:
                
                pass
                
        elif convencion in ['actual/actual', '30/360']:
            
            if n_cupon == n_total:
                
                flujo = (vn * tasa_cupon / cupones_anuales) + vn
            
            elif n_cupon < n_total:
                
                flujo = vn * tasa_cupon / cupones_anuales
                
            else:
                
                pass
                
        elif convencion == 'actual/365':
            
            if n_cupon == n_total:
                
                flujo = (vn * dias_cupon * tasa_cupon / 365) + vn
            
            elif n_cupon < n_total:
                
                flujo = vn * dias_cupon * tasa_cupon / 365
                
            else:
                
                pass
            
    elif tipo_tasa == 'variable':
        
        pass
                
    else:
        pass
                
    
    return flujo


    
# ---- Valor Presente del Flujo i ---- 

def vp_flujo_euro(vn, tipo_tasa, convencion, tasa_cupon, cupones_anuales, n_cupon, n_total, periodo_cupon, t_rend, dias_cupon, plazo):
    
    # Cálculo de flujo para el cupón i
    
    flujo = calcula_flujo_euro(vn = vn,
                               tipo_tasa = tipo_tasa,
                               convencion = convencion,
                               tasa_cupon = tasa_cupon,
                               dias_cupon = dias_cupon,
                               cupones_anuales = cupones_anuales,
                               n_cupon = n_cupon,
                               n_total = n_total)
    
    # Cálculo del factor de descuento dependiendo del tipo de tasa 
    # y el tipo de convención.
    
    if tipo_tasa == 'fija':
        
        if convencion == 'actual/360':
            
            factor_descuento = 1 / (1 + (t_rend * periodo_cupon / 360)) ** (plazo / periodo_cupon)
            
        elif convencion in ['actual/actual', '30/360']:
            
            factor_descuento = 1 / (1 + (t_rend / cupones_anuales)) ** (plazo / periodo_cupon)
            
        elif convencion == 'actual/365':
            
            factor_descuento = 1 / (1 + (t_rend * periodo_cupon / 365)) ** (plazo / periodo_cupon)
        
        else:
            
            factor_descuento = 0
        
    else:
        
        pass
    
    # Cálculo del vp del flujo i
    
    vp = flujo * factor_descuento
    
    
    return vp


def valua_eurobono(fecha_valuacion, fecha_vencimiento, calendario, periodo_cupon, convencion, dia_fijo, vn, tv, tasa_cupon, t_rend, tipo_tasa):
    
    # Obtenemos cuantos cupones paga al año el instrumento.
    
    cupones_anuales = mapea_cupones_anuales(periodo_cupon)
    
    
    # Fechas cupón, plazos y días cupón.
    
    df_fechas, fecha_c_previo = genera_fechas_cupon(fecha_valuacion = fecha_valuacion,
                                                    fecha_vencimiento = fecha_vencimiento,
                                                    calendario = calendario,
                                                    periodo_cupon = periodo_cupon,
                                                    convencion = convencion,
                                                    dia_fijo = dia_fijo)
    
    # Flujos restantes.
    n_restantes = len(df_fechas)
    
    # Vectores auxiliares.
    vp_flujos = []
    plazos_next = []
    
    # Iteramos sobre todos los cupones restantes.
    
    for i in range(1, n_restantes + 1):
        
        # Valor presente del flujo i
        
        vp = vp_flujo_euro(vn = vn,
                           tipo_tasa = tipo_tasa,
                           convencion = convencion,
                           tasa_cupon = tasa_cupon,
                           cupones_anuales = cupones_anuales,
                           n_cupon = i,
                           n_total = n_restantes,
                           periodo_cupon = periodo_cupon,
                           t_rend = t_rend,
                           dias_cupon = df_fechas['dias_cupon'][i - 1],
                           plazo = df_fechas['plazo'][i - 1])
        
        
        
        
        # Plazo siguiente: se utiliza para el cálculo de la duración y convexidad.
        plazo_next = (df_fechas['plazo'][i - 1] / 365) * (df_fechas['plazo'][i - 1] / 365 + 1)
        
        # Asignamos resultados
        vp_flujos.append(vp)
        plazos_next.append(plazo_next)
        
    df_fechas['vp_flujo'] = vp_flujos
    df_fechas['plazo_next'] = plazos_next
    
    
    return df_fechas, fecha_c_previo
        
def intereses_devengados_eurobono(vn, convencion, tasa_cupon, dias_devengado, periodo_cupon):
    
    # Obtenemos cuantos cupones paga al año el instrumento.
    
    cupones_anuales = mapea_cupones_anuales(periodo_cupon)
    
    # Calculamos intereses devengados dependiendo de la convención en la 
    # cuenta de días.
    
    if convencion == 'actual/360':
        
        int_dev = vn * tasa_cupon * dias_devengado / 360
        
    elif convencion in ['actual/actual', '30/360']:
        
        int_dev = vn * tasa_cupon * dias_devengado / (periodo_cupon * cupones_anuales)
        
    elif convencion == 'actual/365':
        
        int_dev = vn * tasa_cupon * dias_devengado / 365
        
    else:
        
        pass
     
    return int_dev
    





