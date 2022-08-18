# ---- Libraries ----
import numpy as np
import pandas as pd
import datetime
from bizdays import Calendar

from fechas import *


# ---- Calendarios ----

# Sección donde se cargan los calendarios necesarios en el proceso de generación
# de fechas cupón

mx_cal = Calendar.load(name = 'mx_calendar', filename = 'Data/df_holidays_mx.cal')

# ---- Funciones ----

def valua_cupon_cero_corpo(id_bono, fecha_valuacion, fecha_vencimiento, vn, t_rend):
    """
    Obtiene la valuación de un bono cupón cero. Puede ser de tipo:
        - CETE
        - Segregado UDI

    Parameters
    ----------
    id_bono : str
        Identificador único del instrumento.
    fecha_valuacion : str
        Fecha de valuación en formato dd/mm/yyyy.
    fecha_vencimiento : str
        Fecha de vencimiento del instrumento en formato dd/mm/yyyy.
    vn : int
        Valor nominal del instrumento.
    tv : str
        Tipo Valor del instrumento, es la clasificación que le asigna Valmer 
        al instrumento.
    t_rend : float
        Tasa de rendimiento del instrumento.

    Returns
    -------
    df_out : pd.DataFrame
        Dataframe con fecha cupón, plazo y días cupón.
    valuacion : float
        Valuación del instrumento a la fecha de valuación.
    """
    
    date_format = "%d/%m/%Y"
    
    # Obtenemos cuantos cupones faltan
    
    fecha_valuacion = datetime.datetime.strptime(fecha_valuacion, date_format)
    fecha_vencimiento = datetime.datetime.strptime(fecha_vencimiento, date_format)
    
    dias_restantes = fecha_vencimiento - fecha_valuacion
    dias_restantes = dias_restantes.days
    
    # Factor de descuento para traer a valor presente.
    
    factor_descuento = 1 / (1 + (t_rend * dias_restantes / 360))     
    valuacion = vn * factor_descuento
        
    # Dataframe de salida, misma estructura que para los demás bonos que 
    # son cuponados.
    
    dict_temp = {'fecha_cupon':[fecha_vencimiento], 
                 'plazo':[dias_restantes],
                 'dias_cupon':[0]}
    
    df_out = pd.DataFrame(dict_temp)
        
    return df_out, valuacion



# ---- Cálculo del Flujo i ----

def calcula_flujo_corpo(vn, tipo_tasa, dias_cupon, tasa_cupon, tasa_mercado, n_cupon, n_total, sobre_tasa_cupon, convencion, cupones_anuales):
    """
    Función que calcula el flujo i para el bono correspondiente.

    Parameters
    ----------
    vn : int
        Valor nominal.
    dias_cupon : int
        Número de días del cupón i (es igual a 182 si es un cupón regular, pero puede variar si 
                                    el corte del cupón es en día inhábil).
    tasa_cupon : float
        Tasa cupón del instrumento.
    tasa_mercado : float
        Máximo de las 2 tasas de referencia para el cálculo de cupones (BPAs).
    n_cupon : int
        Número de cupón.
    n_total : int
        Número total de cupones.
    tasa_fija: str
        Indicador de tasa variable o fija

    Returns
    -------
    flujo : float
        Valor del flujo i.
    """
    flujo = 0
    
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
                
        else:
            pass
        
    elif tipo_tasa == 'variable':
        
        if convencion == 'actual/360':
            
            if n_cupon == n_total:
                
                flujo = (vn * dias_cupon * (tasa_mercado + sobre_tasa_cupon) / 360) + vn
            
            elif n_cupon == 1:

                flujo = vn * dias_cupon * tasa_cupon /360

            elif (n_cupon > 1 and n_cupon < n_total):

                flujo = vn * dias_cupon * (tasa_mercado + sobre_tasa_cupon) / 360

            else:

                pass
                
        elif convencion in ['actual/actual', '30/360']:
            
            pass
        
        elif convencion == 'actual/365':
            
            if n_cupon == n_total:
                
                flujo = (vn * dias_cupon * (tasa_mercado + sobre_tasa_cupon) / 365) + vn
            
            elif n_cupon == 1:

                flujo = vn * dias_cupon * tasa_cupon /365

            elif (n_cupon > 1 and n_cupon < n_total):

                flujo = vn * dias_cupon * (tasa_mercado + sobre_tasa_cupon) / 365

            else:

                pass
                
    else:
        pass
    
    
    
    return flujo



# ---- Valor Presente del Flujo i ---- 

def vp_flujo_corpo(vn, tasa_cupon, dias_cupon, n_cupon, n_total, t_rend, plazo, tipo_tasa, tasa_mercado, sobre_tasa, sobre_tasa_cupon, convencion, cupones_anuales, periodo_cupon):
    """
    Función que calcula el valor presente del flujo i.

    Parameters
    ----------
    vn : int
        Valor nominal.
    tasa_cupon : float
        Tasa cupón.
    dias_cupon : int
        Número de días del cupón i (es igual a 182 si es un cupón regular, pero puede variar si
                                    el corte del cupón es en día inhabil).
    n_cupon : int
        Número de cupón i.
    n_total : int
        Número total de cupones.
    t_rend : float
        Tasa de rendimiento utilizada para descontar los flujos.
    plazo : int
        Número de días por devengar del cupón i (fecha en la que vence el cupón i menor la fecha de
                                                 valuación).
    tasa_fija : str
        Tipo valor del instrumento (identificador del instrumento de Valmer).
    tasa_mercado : float
        Máximo de las 2 tasas de referencia, se utiliza para el descuento de los instrumentos
        de tasa variable.
    sobre_tasa : float
        Sobretasa de mercado asociada al bono (IPAB).

    Returns
    -------
    vp : float
        Valor presente del flujo i.
    """
    flujo = calcula_flujo_corpo(vn = vn,
                                tipo_tasa = tipo_tasa,
                                dias_cupon = dias_cupon,
                                tasa_cupon = tasa_cupon,
                                tasa_mercado = tasa_mercado,
                                n_cupon = n_cupon,
                                n_total = n_total,
                                sobre_tasa_cupon = sobre_tasa_cupon,
                                convencion = convencion,
                                cupones_anuales = cupones_anuales)
    
    if tipo_tasa == 'fija':
        
        if convencion == 'actual/360':
            
            r = t_rend
            factor_descuento = 1 / (1 + (r * dias_cupon / 360)) 

            vp = flujo * (factor_descuento ** (plazo / dias_cupon))
            
        elif convencion in ['actual/actual', '30/360']:
            
            factor_descuento = 1 / (1 + (t_rend / cupones_anuales)) ** (plazo / periodo_cupon)        
            vp = flujo * factor_descuento
            
        elif convencion == 'actual/365':
            
            r = t_rend
            factor_descuento = 1 / (1 + (r * dias_cupon / 365)) 

            vp = flujo * (factor_descuento ** (plazo / dias_cupon))
            
        else:
            
            pass
        
    elif tipo_tasa == 'variable':
        
        if convencion == 'actual/360':
            
            r = tasa_mercado + sobre_tasa
            factor_descuento = 1 / (1 + (r * dias_cupon / 360)) 

            vp = flujo * (factor_descuento ** (plazo / dias_cupon))
            
        elif convencion in ['actual/actual', '30/360']:
            
            pass
        
        elif convencion == 'actual/365':
            
            r = tasa_mercado + sobre_tasa
            factor_descuento = 1 / (1 + (r * dias_cupon / 365)) 

            vp = flujo * (factor_descuento ** (plazo / dias_cupon))
            
        else:
            
            pass
        
    else:
        
        pass
    
    

    return vp


def valua_bono_corporativo(fecha_valuacion, fecha_vencimiento, periodo_cupon, calendario, convencion, tipo_tasa, vn, tasa_cupon, t_rend, tasa_mercado, sobre_tasa, dia_fijo, sobre_tasa_cupon):
    """
    Función que realiza la valuación de los instrumentos gubernamentales mexicanos de renta fija.
    Se mandan a llamar diferentes funciones definidas previamente.

    Parameters
    ----------
    fecha_valuacion : str
        Fecha de valuación en formato dd/mm/yyyy.
    fecha_vencimiento : str
        Fecha de vencimiento del instrumento en formato dd/mm/yyyy.
    periodo_cupon : int
        Días/periodo en que paga cupón el instrumento.
    calendario :  str
        calendario en la cual está referenciado el instrumento.
    convencion : str
        Convención que se utiliza para la cuenta de días (plazo).
    tv : str
        Tipo valor del instrumento (identificador del instrumento de Valmer).
    vn : float
        Valor nominal del instrumento.
    tasa_cupon : float
        Tasa cupón.
    t_rend : float
        Tasa de rendimiento utilizada para descontar los flujos (sólo se utiliza 
                                                                 para los inst tasa fija).
    tasa_mercado :  float
        Máximo de las 2 tasas de referencia, se utiliza para el descuento de los instrumentos
        de tasa variable.
    sobre_tasa :  float
        Sobretasa de mercado asociada al bono (IPAB).

    Returns
    -------
    df_fechas : pd.DataFrame
        Dataframe con la información de fechas cupón, plazos, días cupón, vp del 
        flujo correspondiente y columna de plazo_next auxiliar en el cálculo de 
        la convexidad.
    fecha_c_previo : datetime.datetime
        Fecha del cupón previo a la fecha de valuación.

    """
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
    
    for i in range(1, n_restantes + 1):
        
        # Valor presente del flujo i.
        vp = vp_flujo_corpo(vn = vn,
                      tasa_cupon = tasa_cupon,
                      dias_cupon = df_fechas['dias_cupon'][i - 1],
                      n_cupon = i,
                      n_total = n_restantes,
                      t_rend = t_rend, 
                      plazo = df_fechas['plazo'][i - 1],
                      tipo_tasa = tipo_tasa,
                      tasa_mercado = tasa_mercado,
                      sobre_tasa = sobre_tasa,
                      sobre_tasa_cupon = sobre_tasa_cupon,
                      convencion = convencion,
                      cupones_anuales = cupones_anuales,
                      periodo_cupon = periodo_cupon)

        # Plazo siguiente - se utiliza para el cálculo de la duración y convexidad.
        plazo_next = (df_fechas['plazo'][i - 1] / 365) * (df_fechas['plazo'][i - 1] / 365 + 1)
        
        vp_flujos.append(vp)
        plazos_next.append(plazo_next)
        
    df_fechas['vp_flujo'] = vp_flujos
    df_fechas['plazo_next'] = plazos_next
    
    return df_fechas, fecha_c_previo




