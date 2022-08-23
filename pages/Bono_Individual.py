# ---- Libraries ------

import pandas as pd
import streamlit as st
import os


# ---- [] Gubs, Euros, Corps y Fechas

from modules.generales import *

from modules.corpos import *
from modules.eurobonos import *
from modules.gubernamentales import *
from modules.generales import *

# ---- Helpers ---------

# ---- [] TVs
gubernamentales_cuponados = ['M', 'S','2U','PI', 'IM', 'IQ', 'IS', 'LD', 'LF']
gubernamentales_cupon_cero = ['BI','MC','MP', 'SC', 'SP']

euros_cuponados = ['D1', 'D1SP', 'D4', 'D4SP', 'D5', 'D5SP', 'D6', 'D6SP']
euros_cupon_cero = ['D2', 'D2SP', 'D3', 'D3SP', 'D7', 'D7SP', 'D8', 'D8SP']

corpos_completo = ['2','71','73','75','90','91','91SP','92','93','93SP','94','94SP',
                   '95','97','98','CD','D','F','FSP','G','I','IL',
                   'JE','J', 'JI','JSP','Q','QSP','R1']

all_tv = gubernamentales_cuponados + gubernamentales_cupon_cero + euros_cuponados + euros_cupon_cero + corpos_completo
all_tv = list(set(all_tv))

# ---- [] Periodos Cupón

cupon_period_list = [28, 30, 60, 90, 91, 180, 182, 360, 365]

# ---- [] Convenciones Cuenta Días

daycount_list = ['30/360', '30/360E', 'actual/360', 'actual/365', 'actual/actual']


# ----  Main Interface -------

st.write("# Calculadora COAP")
st.markdown("En la siguiente sección se pueden realizar valuaciones de bonos individuales."
            " Es necesario configurar el instrumento a valuar en el menú de la izquierda.")


with st.sidebar.form(key = 'yield_data'):
    
    select_type_yield = st.radio(label = "Tipo Tasa",
                         options = ['Fija', 'Variable', 'Cero'],
                         index = 0,
                         help = 'La opción tasa cero aplica para los bonos corporativos que son valuados como un CETE.',
                         horizontal = True)
    
    select_type_yield = select_type_yield.lower()
    
    submit_button_yield = st.form_submit_button(label="Seleccione Tipo Tasa")


with st.sidebar.form(key = 'btn_data'):
    
    st.title("Configuración:")
    st.write("Información de instrumento a valuar")
    
    # Initialize Values
    select_yield_spread = 0
    select_coupon_spread = 0
    

    # Fecha Valuación
    valuation_date = st.date_input("📅 Fecha Valuación:")
    valuation_date = str(valuation_date)
    valuation_date = valuation_date.split("-")
    
    # Fecha Vencimiento    
    end_date = st.date_input("📅 Fecha Vencimiento:")
    end_date = str(end_date)
    end_date = end_date.split('-')
    
    # === Todos Comparten ===
    
    # TV y VN
    c1, c2 = st.columns(2)
    
    with c1:
        select_tv = st.selectbox(label = "TV:", 
                                 options = all_tv,
                                 index = 18,
                                 help = 'Se encuentran listados todos los tipos valor documentados en los manuales de Valmer para eurobonos,gubernamentales y corporativos')
        
    with c2:
        face_value = st.text_input(label = "Nominal: ",
                                   value = "0.00")
        face_value = float(face_value)
        
    # Convencion Días y Tipo de cambio
    c3, c4 = st.columns(2)
    
    with c3:
        select_daycount_convention = st.selectbox(label = "Convención Días: ",
                                                  options = daycount_list,
                                                  index = 2)
        
    with c4:
        exchange_rate = st.text_input(label = "Tipo de Cambio",
                                      value = "1.00")
        exchange_rate = float(exchange_rate)
        
    
        
    # Tasa de rendimiento
    
    select_yield = st.text_input(label = "Tasa Rendimiento: ",
                                 value = "0.00",
                                 help = "Tasa en %")
    
    select_yield = float(select_yield) / 100

    
    # === Tasa Fija ====
    
    if select_type_yield == 'fija':
        
        cupon_period = st.selectbox(label = "Periodo Cupón: ",
                                    options = cupon_period_list,
                                    index = 5)
            
        c7, c8 = st.columns(2)
        
        with c7:
            select_coupon_rate = st.text_input(label = "Tasa Cupón: ",
                                               value = "0.00",
                                               help = "Tasa en %")
            
            select_coupon_rate = float(select_coupon_rate) / 100
        
        with c8:
            select_fixed_day = st.selectbox(label = "Cupón en Día Fijo:",
                                            options = ['Si', 'No'])
            
            select_fixed_day = select_fixed_day.lower()
            
        market_yield = 0
        select_coupon_spread = 0
        rate_yield = select_yield
                
    
        
        
    # Si es tasa variable...
    elif select_type_yield == 'variable':
    
        cupon_period = st.selectbox(label = "Periodo Cupón: ",
                                    options = cupon_period_list,
                                    index = 5)
            
        c7, c8 = st.columns(2)
        
        
        with c7:
            select_coupon_rate = st.text_input(label = "Tasa Cupón: ",
                                               value = "0.00",
                                               help = "Tasa en %")
            
            select_coupon_rate = float(select_coupon_rate) / 100
        
        with c8:
            select_fixed_day = st.selectbox(label = "Cupón en Día Fijo:",
                                            options = ['Si', 'No'])
            
            select_fixed_day = select_fixed_day.lower()
        
        
        # Sobretasa Mercado y Sobretasa Cupón
        c9, c10 = st.columns(2)
        
        with c9:
            select_yield_spread = st.text_input(label = "Sobre Tasa:",
                                                value = "0.00",
                                                help = "Tasa en %")
            
            select_yield_spread = float(select_yield_spread) / 100
            
        with c10:
            select_coupon_spread = st.text_input(label = "Sobre Tasa Cupón:",
                                                value = "0.00",
                                                help = "Tasa en %")
            
            select_coupon_spread = float(select_coupon_spread) / 100
            
        market_yield =  select_yield
        rate_yield = 0
        
    # === Cupón Cero ====
    else:
        
        select_fixed_day = 'no'
        select_coupon_rate = 0
        cupon_period = 0
        
        select_yield_spread = 0
        select_coupon_spread = 0
        
        market_yield = 0
        select_coupon_spread = 0
        rate_yield = select_yield
        
        
          
    submit_button = st.form_submit_button(label="✨ Ingresar datos!")

# ---- Valuation Process ------------

# ---- [] New Data

df = pd.DataFrame({'id_bono':['sin_identificar'],
                    'fecha_valuacion':valuation_date[2] + '/' + valuation_date[1] + '/' + valuation_date[0],
                    'fecha_vencimiento':end_date[2] + '/' + end_date[1] + '/' + end_date[0],
                    'periodo_cupon':cupon_period,
                    'calendario':['MXN'],
                    'convencion':select_daycount_convention,
                    'tv':select_tv,
                    'vn':face_value,
                    'tipo_cambio':exchange_rate,
                    'tasa_cupon':select_coupon_rate,
                    't_rend':rate_yield,
                    'tasa_mercado':market_yield,
                    'sobre_tasa':select_yield_spread,
                    'dia_fijo':select_fixed_day,
                    'tipo_tasa':select_type_yield,
                    'sobre_tasa_cupon': select_coupon_spread},
                  index=[0])

st.write("Los datos ingresados fueron los siguientes:")

with st.expander("Información Instrumento", expanded = True):
    st.write(df
             .drop(columns = ['id_bono', 'calendario'])
             .rename(columns = {'fecha_valuacion':'Fecha Valuacion',
                                'fecha_vencimiento':'Fecha Vencimiento',
                                'periodo_cupon':'Periodo Cupon',
                                'convencion':'Convencion',
                                'tv':'Tipo Valor',
                                'vn':'Valor Nominal',
                                'tipo_cambio':'Tipo de Cambio',
                                'tasa_cupon':'Tasa Cupon',
                                't_rend':'Tasa Rendimiento',
                                'tasa_mercado':'Tasa Mercado (Variables)',
                                'sobre_tasa':'Sobre Tasa Mercado',
                                'dia_fijo':'Dia Fijo',
                                'tipo_tasa':'Tipo Tasa',
                                'sobre_tasa_cupon': 'Sobre Tasa Cupon'})
    )
    
    
_, c11, _ = st.columns(3)


# ---- [] Valuation 

with c11:
    btn_val = st.button("Realiza Valuación")
    
    
if btn_val:
    
    try:
    
        results = list(
            map(
                genera_resultados,
                df["id_bono"],
                df["id_bono"],
                df["fecha_valuacion"],
                df["fecha_vencimiento"],
                df["periodo_cupon"],
                df["calendario"],
                df["convencion"],
                df["tv"],
                df["vn"],
                df["tipo_cambio"],
                df["tasa_cupon"],
                df["t_rend"],
                df["tasa_mercado"],
                df["sobre_tasa"],
                df["dia_fijo"],
                df["tipo_tasa"],
                df["sobre_tasa_cupon"]
            )
        )
        
        # Since the results are in a list of lists we need to retreive each component
        # of the output.
        
        lista_val = [output[0] for output in results]
        lista_flujos = [output[1] for output in results]
        
        
        df_valuacion = pd.DataFrame(
            lista_val,
            columns=["id_bono", "isin", "px_sucio", "cupon_dev", "px_limpio", "duracion", "convexidad"],
        )
        df_flujos = pd.concat(lista_flujos, axis = 0, ignore_index = True)
        
        # ---- [] Results
        
        with st.expander("Valuación"):
            st.write(df_valuacion
                      .drop(columns = ['id_bono', 'isin'])
                      .rename(columns = {'px_sucio':'Precio Sucio',
                                        'cupon_dev':'Interes Devengado',
                                        'px_limpio':'Precio Limpio',
                                        'duracion':'Duracion',
                                        'convexidad':'Convexidad'})
                      .style
                      .format("{:.6f}")
            )
            
        with st.expander("Flujos Restantes"):
            st.write(df_flujos
                      .drop(columns = ['id_bono', 'plazo_next'])
                      .rename(columns = {'fecha_cupon':'Fecha Cupon',
                                        'plazo':'Plazo',
                                        'dias_cupon':'Dias Cupon',
                                        'factor_descuento':'Factor Descuento',
                                        'vp_flujo':'VP Flujo'})
                      )
            
    except:
        
        st.error("Se configuró de forma erronea el instrumento a valuar. Por favor revise los inputs nuevamente.")
    

    
        