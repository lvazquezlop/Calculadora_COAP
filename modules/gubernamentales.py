# ---- Libraries ----
import numpy as np
import pandas as pd
import datetime
from bizdays import Calendar

from modules.fechas import *
#from Code.modules.fechas import *


# ---- Calendarios ----

# Sección donde se cargan los calendarios necesarios en el proceso de generación
# de fechas cupón

mx_cal = Calendar.load(name = 'mx_calendar', filename = 'Data/df_holidays_mx.cal')

# ---- Funciones ----

# ---- Valuación Cupón Cero ----


def valua_cupon_cero(id_bono, fecha_valuacion, fecha_vencimiento, vn, tv, tipo_cambio, t_rend):
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
    tipo_cambio : float
        Tipo de cambio usado (UDI).
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
    
    if tv in ["BI","MC","MP"]:
        
        valuacion = vn * factor_descuento
        
    else:
        
        valuacion = vn * tipo_cambio * factor_descuento
        
    # Dataframe de salida, misma estructura que para los demás bonos que 
    # son cuponados.
    
    dict_temp = {'fecha_cupon':[fecha_vencimiento], 
                 'plazo':[dias_restantes],
                 'dias_cupon':[0],
                 'factor_descuento':[factor_descuento]}
    
    df_out = pd.DataFrame(dict_temp)
        
    return df_out, valuacion



# ---- Intereses Devengados ---- 

def int_devengados_gubernamental(vn, tasa_cupon, dias_devengado, tv, tipo_cambio):
    """
    Calcula los intereses devenengados del cupón a t días. Toma en cuenta
    el tipo de instrumento (TV) que se está valuando.

    Parameters
    ----------
    vn : int
        Valor nominal del instrumento.
    tasa_cupon : float
        Tasa cupón del instrumento.
    dias_devengado : int
        Número de días transcurridos del cupón vigente.
    tv : string
        Tipo valor definido para el instrumento.
    tipo_cambio : float, optional
        Valor de la UDI a la fecha de valuación. The default is 1.

    Returns
    -------
    int_dev : float
        Monto de intereses devengados..

    """
    
    if tv in ['M', 'IM', 'IQ', 'IS', 'LD', 'LF']: # M-bono
        
        int_dev = vn * tasa_cupon * dias_devengado / 360
    
    elif tv in ['S', '2U','PI']: # Udibono, CBIS, PIC's
        
        int_dev = vn * tasa_cupon * dias_devengado * tipo_cambio / 360
    
    else:
        pass
    
    return int_dev

# ---- Cálculo del Flujo i ----

def calcula_flujo_gubernamental(vn, tv, dias_cupon, tasa_cupon, tasa_mercado, n_cupon, n_total, fecha_valuacion, fecha_vencimiento, calendario, periodo_cupon, convencion, dia_fijo):
    """
    Función que calcula el flujo i para el bono correspondiente.

    Parameters
    ----------
    vn : int
        Valor nominal.
    tv: str
        Tipo valor del instrumento (Valmer).
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

    Returns
    -------
    flujo : float
        Valor del flujo i.
    """
    
    df_fechas, fecha_c_previo = genera_fechas_cupon(fecha_valuacion = fecha_valuacion,
                                                    fecha_vencimiento = fecha_vencimiento,
                                                    calendario = calendario,
                                                    periodo_cupon = periodo_cupon,
                                                    convencion = convencion,
                                                    dia_fijo = dia_fijo)
    
    date_format = '%d/%m/%Y'
    fecha_valuacion = datetime.datetime.strptime(fecha_valuacion, date_format)
    fecha_c_previo = fecha_c_previo.to_pydatetime() 
    dias_transcurridos = (fecha_valuacion - fecha_c_previo).days
    dias_para_cupon = (df_fechas['dias_cupon'][0] - dias_transcurridos)
    
    flujo = 0
    
    if tv in ['M', 'S', '2U', 'PI', 'BI', 'MC', 'MP', 'SC', 'SP']: # Tasa Fija
    
        if n_cupon == n_total:
            
            flujo = (vn * dias_cupon * tasa_cupon / 360) + vn
    
        elif n_cupon < n_total:
            
            flujo = vn * dias_cupon * tasa_cupon / 360
            
        else:
            
            pass
    
    elif tv in ['IM', 'IQ', 'IS']: # Tasa Variable
    
        if n_cupon == n_total:
            
            flujo = (vn * dias_cupon * tasa_mercado / 360) + vn
        
        elif n_cupon == 1:
            
            flujo = vn * dias_cupon * tasa_cupon /360
            
        elif (n_cupon > 1 and n_cupon < n_total):
            
            flujo = vn * dias_cupon * tasa_mercado / 360
            
        else:
            
            pass
            
    elif tv in ['LD', 'LF']: # Tasa Variable
    
        if n_cupon == n_total:
            
            flujo = (vn * ((1 + tasa_mercado / 360) ** dias_cupon - 1)) + vn
        
        elif n_cupon == 1:
            
            flujo = vn * ((1 + tasa_cupon / 360 * dias_transcurridos) * (1 + tasa_mercado / 360) ** dias_para_cupon - 1)
            
        elif (n_cupon > 1 and n_cupon < n_total):
            
            flujo = vn * ((1 + tasa_mercado / 360) ** dias_cupon - 1)
            
        else:
            
            pass
            
    else:
        pass
    
    return flujo

# ---- Valor Presente del Flujo i ---- 

def vp_flujo_gubernamental(vn, tasa_cupon, dias_cupon, n_cupon, n_total, t_rend, plazo, tv, tipo_cambio, tasa_mercado, sobre_tasa, fecha_valuacion, fecha_vencimiento, calendario, periodo_cupon, convencion, dia_fijo):

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
    tv : str
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
    flujo = calcula_flujo_gubernamental(vn = vn,
                                        tv = tv,
                                        dias_cupon = dias_cupon,
                                        tasa_cupon = tasa_cupon,
                                        tasa_mercado = tasa_mercado,
                                        n_cupon = n_cupon,
                                        n_total = n_total,
                                        fecha_valuacion = fecha_valuacion,
                                        fecha_vencimiento = fecha_vencimiento,
                                        calendario = calendario,
                                        periodo_cupon = periodo_cupon,
                                        convencion = convencion,
                                        dia_fijo = dia_fijo)
    
    factor_descuento = 1 / (1 + (t_rend * periodo_cupon / 360)) ** (plazo / periodo_cupon)
    
    if tv in ['M']: # M-Bono
        
        vp = flujo * factor_descuento
    
    elif tv in ['S', '2U','PI']: # Udibono, CBIS, PIC's
        
        vp = flujo * tipo_cambio * factor_descuento 
        
    elif tv in ['IM', 'IQ', 'IS']: # BPAs
        
        r = tasa_mercado + sobre_tasa
        factor_descuento = 1 / (1 + (r * dias_cupon / 360)) ** (plazo / dias_cupon)
        
        vp = flujo * factor_descuento 
        
    elif tv in ['LD', 'LF']: # BPAs
        
        r = tasa_mercado + sobre_tasa
        factor_descuento = 1 / (1 + r / 360) ** plazo
        
        vp = flujo * factor_descuento
        
    else:
        pass

    return vp, factor_descuento

# ---- Valuación Bonos Gubernamentales Mx ----

def valua_bono_gubernamental(fecha_valuacion, fecha_vencimiento, periodo_cupon, calendario, convencion, tv, vn, tipo_cambio, tasa_cupon, t_rend, tasa_mercado, sobre_tasa, dia_fijo):
    
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
    tipo_cambio : float
        Tipo de cambio MXN/MonedaExtranjera utilizada para la valuación (FIX o SPOT).
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
    factores_descuento = []
    
    for i in range(1, n_restantes + 1):
        
        # Valor presente del flujo i.
        vp, factor_descuento = vp_flujo_gubernamental(vn = vn,
                                                      tasa_cupon = tasa_cupon,
                                                      dias_cupon = df_fechas['dias_cupon'][i - 1],
                                                      n_cupon = i,
                                                      n_total = n_restantes,
                                                      t_rend = t_rend, 
                                                      plazo = df_fechas['plazo'][i - 1],
                                                      tv = tv,
                                                      tipo_cambio = tipo_cambio,
                                                      tasa_mercado = tasa_mercado,
                                                      sobre_tasa = sobre_tasa,
                                                      fecha_valuacion = fecha_valuacion,
                                                      fecha_vencimiento = fecha_vencimiento,
                                                      calendario = calendario,
                                                      periodo_cupon = periodo_cupon,
                                                      convencion = convencion,
                                                      dia_fijo = dia_fijo)
        
        # Plazo siguiente - se utiliza para el cálculo de la duración y convexidad.
        plazo_next = (df_fechas['plazo'][i - 1] / 365) * (df_fechas['plazo'][i - 1] / 365 + 1)
        
        vp_flujos.append(vp)
        plazos_next.append(plazo_next)
        factores_descuento.append(factor_descuento)
        
    
    df_fechas['factor_descuento'] = factores_descuento
    df_fechas['vp_flujo'] = vp_flujos
    df_fechas['plazo_next'] = plazos_next
    
    
    return df_fechas, fecha_c_previo






#----
# valua_bono_gubernamental(fecha_valuacion = '16/02/2022',
#                          fecha_vencimiento = '05/09/2024',
#                          periodo_cupon = 182, 
#                          calendario = 'MXN',
#                          convencion = 'actual/360',
#                          tv = 'M',
#                          vn = 100,
#                          tipo_cambio = 1,
#                          tasa_cupon = 0.08,
#                          t_rend = 0.056496266,
#                          tasa_mercado = 0,
#                          sobre_tasa = 0,
#                          dia_fijo = 'no')


