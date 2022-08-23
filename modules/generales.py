# ---- Libraries ----
import numpy as np
import pandas as pd
import datetime
from bizdays import Calendar

from modules.fechas import *
from modules.gubernamentales import *
from modules.eurobonos import *
from modules.corpos import *

# ---- Calendarios ----

# Sección donde se cargan los calendarios necesarios en el proceso de generación
# de fechas cupón

mx_cal = Calendar.load(name = 'mx_calendar', filename = 'Data/df_holidays_mx.cal')

# ---- Funciones ----

# ---- Duración ----

def duracion_bono(v_plazos, v_vp_flujos, px_sucio):
    """
    Función que calcula la duración de un bono.

    Parameters
    ----------
    v_plazos : array
        Vector que contiene los plazos de los flujos restantes.
    v_vp_flujos : array
        Vector que contiene los vp de los flujos restantes.
    px_sucio : float
        Precio sucio del instrumento.

    Returns
    -------
    duration : float
        Duración del instrumento.
    """
    
    aux1 = np.dot(v_plazos, v_vp_flujos)
    aux2 = px_sucio * 365
    
    duration = aux1 / aux2
    
    return duration


# ---- Convexidad ----



def convexidad_bono(tipo_tasa, v_plazos, v_vp_flujos, px_sucio, t_ref, periodo_c, tasa_mercado, sobre_tasa):
    
    if tipo_tasa in ['fija','cero']:
        
        t_rend = t_ref
        
    elif tipo_tasa =='variable':
        
        t_rend = tasa_mercado + sobre_tasa
        
    else:
        pass
    
    aux2 = np.dot(v_plazos, v_vp_flujos)
    aux1 = px_sucio * (1 + t_rend * periodo_c / 360) ** 2
    
    convexity = aux2 / aux1
    
    return convexity




# ---- Genera Resultados ----

def genera_resultados(id_bono, isin, fecha_valuacion, fecha_vencimiento, periodo_cupon, calendario, convencion, tv, vn, tipo_cambio, tasa_cupon, t_rend, tasa_mercado, sobre_tasa, dia_fijo, tipo_tasa, sobre_tasa_cupon):
    
    date_format = "%d/%m/%Y"
    
    # ==== Lista TVs ===============
    
    gubernamentales_cuponados = ['M', 'S','2U','PI', 'IM', 'IQ', 'IS', 'LD', 'LF']
    gubernamentales_cupon_cero = ['BI','MC','MP', 'SC', 'SP']
    
    euros_cuponados = ['D1', 'D1SP', 'D4', 'D4SP', 'D5', 'D5SP', 'D6', 'D6SP']
    euros_cupon_cero = ['D2', 'D2SP', 'D3', 'D3SP', 'D7', 'D7SP', 'D8', 'D8SP']
    
    corpos_completo = ['2','71','73','75','90','91','91SP','92','93','93SP','94','94SP',
                       '95','97','98','CD','D','F','FSP','G','I','IL',
                       'JE','J', 'JI','JSP','Q','QSP','R1']
    
    
    # ==== Gubernamentales Mx ====
    
    if tv in gubernamentales_cuponados:
        
        # Valuación
        df_val, fecha_c_prev = valua_bono_gubernamental(fecha_valuacion = fecha_valuacion,
                                                        fecha_vencimiento = fecha_vencimiento,
                                                        periodo_cupon = periodo_cupon,
                                                        calendario = calendario,
                                                        convencion = convencion,
                                                        tv = tv,
                                                        vn = vn,
                                                        tipo_cambio = tipo_cambio,
                                                        tasa_cupon = tasa_cupon,
                                                        t_rend = t_rend,
                                                        tasa_mercado = tasa_mercado,
                                                        sobre_tasa = sobre_tasa,
                                                        dia_fijo = dia_fijo)
        
        px_sucio = sum(df_val['vp_flujo'])
        
        # Cupón devengado - Intereses
        aux1 = datetime.datetime.strptime(fecha_valuacion, date_format)
        aux2 = fecha_c_prev
        dias_dev = aux1 - aux2
        
        int_dev = int_devengados_gubernamental(vn = vn,
                                 tasa_cupon = tasa_cupon,
                                 dias_devengado = dias_dev.days,
                                 tv = tv,
                                 tipo_cambio = tipo_cambio)
        
        # Precio limpio
        px_limpio = px_sucio - int_dev
        
    elif tv in gubernamentales_cupon_cero:
        
        # Valuación
        df_val, px_sucio = valua_cupon_cero(id_bono = id_bono,
                                            fecha_valuacion = fecha_valuacion,
                                            fecha_vencimiento = fecha_vencimiento,
                                            vn = vn,
                                            tv = tv,
                                            tipo_cambio = tipo_cambio,
                                            t_rend = t_rend)
        
        df_val['vp_flujo'] = px_sucio
        df_val['plazo_next'] = (df_val['plazo'][0] / 365) * (df_val['plazo'][0] / 365 + 1)
        
        # Precio limpio
        int_dev = 0
        px_limpio = px_sucio
        
        
    # ==== Eurobonos =====
        
        
    elif tv in euros_cuponados:
        
        # Valuación
        
        df_val, fecha_c_prev = valua_eurobono(fecha_valuacion = fecha_valuacion,
                                              fecha_vencimiento = fecha_vencimiento,
                                              calendario = calendario,
                                              periodo_cupon = periodo_cupon,
                                              convencion = convencion,
                                              dia_fijo = dia_fijo,
                                              vn = vn,
                                              tv = tv,
                                              tasa_cupon = tasa_cupon,
                                              t_rend = t_rend,
                                              tipo_tasa = tipo_tasa)
        
        
        
        px_sucio = sum(df_val['vp_flujo']) * tipo_cambio
        
        # Cupón devengado - Intereses
        aux1 = datetime.datetime.strptime(fecha_valuacion, date_format)
        aux2 = fecha_c_prev
        dias_dev = calcula_plazo(convention = convencion, date1 = aux2, date2 = aux1)
        
        int_dev = intereses_devengados_eurobono(vn = vn,
                                                convencion = convencion,
                                                tasa_cupon = tasa_cupon,
                                                dias_devengado = dias_dev,
                                                periodo_cupon = periodo_cupon)
        
        
        int_dev = int_dev * tipo_cambio
        
        # Precio limpio.
        px_limpio = px_sucio - int_dev
        
    
    # ==== Corporativos ====
        
        
    elif tv in corpos_completo:
        
        if tipo_tasa in ['fija', 'variable']:
            
            # Valuacion
        
            df_val, fecha_c_prev = valua_bono_corporativo(fecha_valuacion = fecha_valuacion,
                                                          fecha_vencimiento = fecha_vencimiento,
                                                          periodo_cupon = periodo_cupon,
                                                          calendario = calendario,
                                                          convencion = convencion,
                                                          tipo_tasa = tipo_tasa, 
                                                          vn = vn,
                                                          tasa_cupon = tasa_cupon,
                                                          t_rend = t_rend,
                                                          tasa_mercado = tasa_mercado, 
                                                          sobre_tasa = sobre_tasa,
                                                          dia_fijo = dia_fijo,
                                                          sobre_tasa_cupon = sobre_tasa_cupon)
            
            px_sucio = sum(df_val['vp_flujo'])
            
            # Cupón devengado - Intereses
            aux1 = datetime.datetime.strptime(fecha_valuacion, date_format)
            aux2 = fecha_c_prev
            dias_dev = calcula_plazo(convention = convencion, date1 = aux2, date2 = aux1)
            
            int_dev = intereses_devengados_eurobono(vn = vn,
                                                    convencion = convencion,
                                                    tasa_cupon = tasa_cupon,
                                                    dias_devengado = dias_dev,
                                                    periodo_cupon = periodo_cupon)
            
            # Precio limpio.
            px_limpio = px_sucio - int_dev
            
        elif tipo_tasa == 'cero':
            
            # Valuacion
            
            df_val, px_sucio = valua_cupon_cero_corpo(id_bono = id_bono,
                                                      fecha_valuacion = fecha_valuacion,
                                                      fecha_vencimiento = fecha_vencimiento,
                                                      vn = vn,
                                                      t_rend = t_rend)
            
            df_val['vp_flujo'] = px_sucio
            df_val['plazo_next'] = (df_val['plazo'][0] / 365) * (df_val['plazo'][0] / 365 + 1)
            
            
            # Precio limpio
            int_dev = 0
            px_limpio = px_sucio
            
        
    else:
        pass
    
    # Px sucio auxiliar para el cálculo de la duración y convexidad.
    
    px_sucio_aux = px_sucio / tipo_cambio if tv in euros_cuponados + euros_cupon_cero else px_sucio
    
    # Duración
    duration = duracion_bono(v_plazos = df_val['plazo'],
                             v_vp_flujos = df_val['vp_flujo'],
                             px_sucio = px_sucio_aux)
    
    # Convexidad    
    convexity = convexidad_bono(tipo_tasa = tipo_tasa,
                                v_plazos = df_val['plazo_next'],
                                v_vp_flujos = df_val['vp_flujo'],
                                px_sucio = px_sucio_aux,
                                t_ref = t_rend,
                                periodo_c = periodo_cupon,
                                tasa_mercado = tasa_mercado,
                                sobre_tasa = sobre_tasa)
    
    
    # Salida
    list_out = [id_bono, isin, px_sucio, int_dev, px_limpio, duration, convexity]
    df_val.insert(0, 'id_bono', id_bono)
    
    
    return list_out, df_val

