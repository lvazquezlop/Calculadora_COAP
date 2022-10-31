# -- Libraries ---------

import pandas as pd
import numpy as np
import datetime
from bizdays import Calendar
import calendar

# ---- Calendarios ----

# Sección donde se cargan los calendarios necesarios en el proceso de generación
# de fechas cupón




mx_cal = Calendar.load(name = 'mx_calendar', filename = 'Data/df_holidays_mx.cal')


# ---- Functions -------

# ---- * Day Count Conventions * 

# ---- [] 30/360 ---------

def method_30_360(date1, date2, fraction = False):
    
    y1 = date1.year
    y2 = date2.year
    m1 = date1.month
    m2 = date2.month
    d1 = date1.day
    d2 = date2.day
    
    # Last day of february for each date.
    
    _, last_day_feb_date1 = calendar.monthrange(y1, 2)
    _, last_day_feb_date2 = calendar.monthrange(y2, 2)
    
    # Exceptions
    
    # 1. 
    
    d1 = 30 if d1 == 31 else d1
    
    # 2.
    
    d2 = 30 if (d2 == 31 and (d1 == 30 or d1 == 31)) else d2
    
    # 3.
    
    d2 = 30 if (d2 == last_day_feb_date2 and m2 == 2 and d1 == last_day_feb_date1 and m1 == 2) else d2
    
    # 4.
    
    d1 = 30 if (d1 == last_day_feb_date1 and m1 == 2) else d1
    
    # Daycount calculations
    
    numerator = (y2 - y1) * 360 + (m2 - m1) * 30 + (d2 - d1)
    
    if fraction:
        
        return numerator / 360
    
    else:
        
        return numerator
    
    
# ---- [] 30/360 E ---------

def method_30_360_E(date1, date2, fraction = False):
    
    y1 = date1.year
    y2 = date2.year
    m1 = date1.month
    m2 = date2.month
    d1 = date1.day
    d2 = date2.day
    
    # Exceptions
    
    # 1. 
    
    d1 = 30 if d1 == 31 else d1
    
    # 2.
    
    d2 = 30 if d2 == 31 else d2
    
    
    # Daycount calculations
    
    numerator = (y2 - y1) * 360 + (m2 - m1) * 30 + (d2 - d1)
    
    if fraction:
        
        return numerator / 360
    
    else:
        
        return numerator
    
    
# ---- [] Act/360 ---------

def method_act_360(date1, date2, fraction = False):
    
    days_between = date2 - date1
    days_between = days_between.days
    
    if fraction:
        
        return days_between / 360
    
    else:
        
        return days_between
    
# ---- [] Act/365 ---------
    
def method_act_365(date1, date2, fraction = False):
    
    days_between = date2 - date1
    days_between = days_between.days
    
    if fraction:
        
        return days_between / 365
    
    else:
        
        return days_between    
    

# ---- [] Act/Act ---------

def method_act_act(date1, date2, fraction = False):
    
    date_format = '%d/%m/%Y'
    
    y1 = date1.year
    y2 = date2.year
    
    last_day_y1 = '31/12/' + str(y1)
    last_day_y1 = datetime.datetime.strptime(last_day_y1, date_format)
    
    first_day_y2 = '01/01/' + str(y1 + 1)
    first_day_y2 = datetime.datetime.strptime(first_day_y2, date_format)
    
    
    days_between = date2 - date1
    days_between = days_between.days
    
    if fraction:
        
        # Check if dates are from the same year.
        
        if y1 == y2:
            
            if calendar.isleap(y1):
                
                return days_between / 366
            
            else:
                
                return days_between / 365
            
        # If not we need to check the different combinations of leap year 
        # between y1 and y2.
            
        else:
            
            if (calendar.isleap(y1) == False and calendar.isleap(y2) == False):
                
                return days_between / 365
            
            elif (calendar.isleap(y1) == True and calendar.isleap(y2) == False):
                
                days_left_y1 = last_day_y1 - date1
                days_left_y1 = days_left_y1.days
                
                days_left_y2 = date2 - first_day_y2
                days_left_y2 = days_left_y2.days
                
                fraction_aux = (days_left_y1 / 366) + (days_left_y2 / 365)
                
                return fraction_aux
            
            elif (calendar.isleap(y1) == False and calendar.isleap(y2) == True):
                
                days_left_y1 = last_day_y1 - date1
                days_left_y1 = days_left_y1.days
                
                days_left_y2 = date2 - first_day_y2
                days_left_y2 = days_left_y2.days
                
                fraction_aux = (days_left_y1 / 365) + (days_left_y2 / 366)
                
                return fraction_aux
            
            
    else:
        
        return days_between
    

# ---- Calcula Plazos ---------

def calcula_plazo(convention, date1, date2, fraction = False):
    
    plazo_out = 0
    
    if convention == '30/360':
        plazo_out = method_30_360(date1, date2, fraction)
        
    elif convention == '30/360E':
        plazo_out = method_30_360_E(date1, date2, fraction)
        
    elif convention == 'actual/360':
        plazo_out = method_act_360(date1, date2, fraction)
        
    elif convention == 'actual/365':
        plazo_out = method_act_365(date1, date2, fraction)
        
    elif convention == 'actual/actual':
        plazo_out = method_act_act(date1, date2, fraction)
        
    else:
        pass
    
    return plazo_out


# ---- * Date Construction * 

# ---- [] Valida Bizday (Back) ------

def valida_bizday(fecha, convencion, calendario_R):
    
    date_format = "%d/%m/%Y"
    
    if convencion == 'actual/360':
    
        fecha_aux = calendario_R.preceding(fecha)
        fecha_aux = datetime.datetime.strftime(fecha_aux, date_format)
        fecha_aux = datetime.datetime.strptime(fecha_aux, date_format)
        
    else:
        
        fecha_aux = calendario_R.following(fecha)
        fecha_aux = datetime.datetime.strftime(fecha_aux, date_format)
        fecha_aux = datetime.datetime.strptime(fecha_aux, date_format)
        
    
    return fecha_aux


# ---- [] Genera Fechas -----------

def genera_fechas_cupon(fecha_valuacion, fecha_vencimiento, calendario, periodo_cupon, convencion, dia_fijo):
    """
    Función que genera las fechas de pago de los cupones restantes, se calcula el plazo
    de cada cupón siguiente. Valida que las fechas de pago de cupón 

    Parameters
    ----------
    fecha_valuacion : str
        Fecha de valuación en formato dd/mm/yyyy.
    fecha_vencimiento : str
        Fecha de vencimiento del instrumento en formato dd/mm/yyyy.
    calendario : str
        calendario en la cual está referenciado el instrumento.
    periodo_cupon : int
        Días/periodo en que paga cupón el instrumento.
    convencion : str
        Convencion con la cual se va a contar el plazo de cada fecha cupón.

    Returns
    -------
    df_out : pd.DataFrame
        Dataframe que contiene las fechas cupón siguientes, plazos y días entre cada cupón.
    fecha_c_previo: datetime.timestamp
        Fecha en la que se pago el cupón inmediato anterior a la fecha de valuación.

    """
    date_format = '%d/%m/%Y'
    
    # Obtenemos cuantos cupones faltan.
    
    fecha_valuacion = datetime.datetime.strptime(fecha_valuacion, date_format)
    fecha_vencimiento = datetime.datetime.strptime(fecha_vencimiento, date_format)
    
    dias_liq = fecha_vencimiento - fecha_valuacion
    n_c_faltantes = np.ceil(dias_liq.days / periodo_cupon)
    
    # Con la fecha del cupón previo generamos fechas cupon siguientes.
    
    dias_cupon_aux = datetime.timedelta(days = periodo_cupon)
    
    # Lista vacía donde almacenaremos las fechas y plazos
    
    out = []
    out_2 = []

    # Backward ---
       
    fecha_sig = fecha_vencimiento + dias_cupon_aux
    
    for i in range(int(n_c_faltantes) + 1):
        
        if (dia_fijo == 'si'):
            
            fecha_sig = (fecha_sig - dias_cupon_aux).replace(day = fecha_vencimiento.day)
            
        elif (dia_fijo == 'no'):
            
            fecha_sig = fecha_sig - dias_cupon_aux
            
        else:
            pass
        
        plazo = fecha_sig - fecha_valuacion
        
        out.append([fecha_sig, plazo.days, dias_cupon_aux.days])
    
        
    df_out_aux = pd.DataFrame(out, columns = ['fecha_cupon', 'plazo', 'dias_cupon']).sort_values(by = ['fecha_cupon'], ascending = True)
    
    
    # Revisamos que sólo haya 1 plazo negativo.
    
    n_negativos = len(df_out_aux[df_out_aux['plazo'] < 0])
    
    if n_negativos > 1:
        
        df_negativos_aux = df_out_aux[df_out_aux['plazo'] < 0].copy()
        idx_negativos = df_negativos_aux.index[-1]
        
        df_out_aux = df_out_aux[df_out_aux.index.isin(range(idx_negativos + 1))]
        
    # En el caso que no se hayan generado fechas negativas nos aseguramos que exista una,
    # la cual es la fecha de pago cupón previa a la fecha de valuación.
    
    if n_negativos == 0:
        
        out_aux = []
        
        df_negativos_aux = df_out_aux.copy()
        
        idx_primer_fecha = df_negativos_aux.index.min() # Obtenemos la fecha con el plazo más pequeño
        
        primer_fecha = df_negativos_aux.iloc[idx_primer_fecha, 0] 
        
        if (dia_fijo == 'si'):
            
            fecha_sig = (primer_fecha - dias_cupon_aux).replace(day = fecha_vencimiento.day)
            
        elif (dia_fijo == 'no'):
            
            fecha_sig = fecha_sig - dias_cupon_aux
            
        else:
            pass
        
        plazo = fecha_sig - fecha_valuacion
        
        out_aux.append([fecha_sig, plazo.days, dias_cupon_aux.days])
        
        df_out_aux = pd.concat([pd.DataFrame(out_aux, columns = ['fecha_cupon', 'plazo', 'dias_cupon']),
                                df_out_aux],
                               ignore_index = True) # Tener cuidado aquí porque se resetea el índice, afecta eso?
        
    
    # Obtenemos la fecha del cupón previo a la fecha de valuación.
    
    fecha_c_previo_aux = df_out_aux['fecha_cupon'].iloc[0]
    
    
    # Una vez que se obtiene la fecha cupón previa a la fecha de valuación
    # se construyen las fechas cupón efectivas.
    
    # Forward ---
    
    # La forma de obtener los días cupón siguientes dependerá si es en un día fijo de
    # cada mes o no.
    
    if (dia_fijo == 'no'):
        
        fecha_c_previo = valida_bizday(fecha_c_previo_aux, convencion, mx_cal) # Se valida que sea fecha laborable
        out_2.append([fecha_c_previo_aux, fecha_c_previo])
        
    
    # Se valida que las fechas generadas sean fechas laborales, de lo contrario
    # se regresa la fecha laboral inmediata anterior o siguiente según sea el caso.
    
        for i in range(int(n_c_faltantes)):
            
            fecha_sig = fecha_c_previo + dias_cupon_aux
            fecha_c_previo = fecha_sig
            fecha_sig_val = valida_bizday(fecha_sig, convencion, mx_cal)
            
            plazo = calcula_plazo(convencion, fecha_valuacion, fecha_sig_val)
            
            out_2.append([fecha_sig, fecha_sig_val, plazo])
            
    elif (dia_fijo == 'si'):
        
        fecha_c_previo = df_out_aux['fecha_cupon'].iloc[0]
        out_2.append([fecha_c_previo_aux, fecha_c_previo])
        
        for i in range(int(n_c_faltantes)):
            
            fecha_sig = (fecha_c_previo + dias_cupon_aux).replace(day = fecha_vencimiento.day)
            fecha_c_previo = fecha_sig
            fecha_sig_val = fecha_sig
            
            plazo = calcula_plazo(convencion, fecha_valuacion, fecha_sig_val)
            
            out_2.append([fecha_sig, fecha_sig_val, plazo])
            
    else:
        pass
    
    
    # Generamos tabla de salida
            
    df_out = pd.DataFrame(out_2, columns = ['fecha_cupon_aux', 'fecha_cupon', 'plazo'])
    
    df_out['dias_cupon'] = df_out['fecha_cupon'].diff()
    
    # Nos quedamos con las fechas de pago de cupón posteriores a la 
    # fecha de valuación.
    
    df_out = df_out.iloc[1:, :].copy()
    df_out.drop('fecha_cupon_aux', axis = 1, inplace = True)
    df_out = df_out.reset_index(drop = True)
    
    df_out['dias_cupon'] = df_out['dias_cupon'].apply(lambda x:int(x.days))
        

    
    return df_out, fecha_c_previo_aux


# ---- [] Mapea Cupones Anuales -----------

def mapea_cupones_anuales(periodo_cupon):
    
    cupones_anuales = 0
    
    if periodo_cupon in [28, 30]:
        
        cupones_anuales = 12
    
    elif periodo_cupon in [180, 182]:
        
        cupones_anuales = 2
        
    elif periodo_cupon in [60, 61]:
        
        cupones_anuales = 6
        
    elif periodo_cupon in [360, 365]:
        
        cupones_anuales = 1
        
    elif periodo_cupon in [90, 91]:
        
        cupones_anuales = 4
        
    else:
        pass
    
    return cupones_anuales



# ================================


genera_fechas_cupon(fecha_valuacion = '30/06/2022',
                    fecha_vencimiento = '28/03/2027',
                    calendario = 'AAAAAA',
                    periodo_cupon = 180,
                    convencion = '30/360',
                    dia_fijo = 'si')







