# ---- Libraries ------

import pandas as pd
import streamlit as st
import os


# ---- [] Gubs, Euros, Corps y Fechas

from modules.generales import *

# ---- Input Data ------


@st.cache
def read_csv(path):
    return pd.read_csv(path)

@st.cache
def convert_df_to_csv(df):
    out = df.to_csv().encode('utf-8')
    return out


# df = read_csv(
#     "C:/Users/MI12584/Documents/Calculadora COAP/Calculadora/Calculadora_FI/Data/prueba_A.csv"
# )

# ---- Add sidebar to the app ------

# st.sidebar.markdown("# Configuración")
# st.sidebar.markdown(
#     "En esta sección se deben de seleccionar las configuraciones iniciales relevantes para la valuación:"
# )

# ---- [] Dates, Filters, Yields

# valuation_date = st.sidebar.date_input("Fecha de Valuación")
# yield_bpa = st.sidebar.number_input("Tasa BPAs")
# yield_ld = st.sidebar.number_input("Tasa LDs")


# ----  Main Interface -------

st.write("# Calculadora COAP")
st.markdown("En esta sección se realiza la valuación de un conjunto de bonos.")
st.markdown("######")
st.markdown("Para que se realice el proceso basta con cargar el archivo con las posiciones y el vector de Valmer.")

# ---- [] Upload files


df_cartera_in = st.file_uploader("Cartera COAP", type = ".csv")


if df_cartera_in:
    
    df = pd.read_csv(df_cartera_in)

    # ---- [] Data preview, Valuation of the entire portfolio
    
    
    st.markdown("## Preview Cartera")
    st.markdown(
        "A continuación se muestran los primeros 5 instrumentos que componen la cartera:"
    )
    
    with st.expander("Posiciones"):
        st.write(df
                 .drop(columns = ['calendario'])
                 .rename(columns = {'id_bono':'ID Bono',
                                    'isin':'ISIN',
                                    'fecha_valuacion':'Fecha Valuacion',
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
                 .head()
        )
    
    
    st.markdown("## Valuación Cartera")
    st.markdown(
        "En la siguiente sección se presentan los resultados de la valuación de los instrumentos"
        " que componen la cartera así como los flujos futuros de cada bono."
    )
    
    # ---- Valuation Process ---------

    results = list(
        map(
            genera_resultados,
            df["id_bono"],
            df["isin"],
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
    
    st.write(df_valuacion
             .rename(columns = {'id_bono':'ID Bono',
                                'isin':'ISIN',
                                'px_sucio':'Precio Sucio',
                                'cupon_dev':'Interes Devengado',
                                'px_limpio':'Precio Limpio',
                                'duracion':'Duracion',
                                'convexidad':'Convexidad'})
                           .style
                           .format("{:.6f}"))
    
    # with st.expander("Valuación"):
    #     st.write(df_valuacion
    #              .rename(columns = {'id_bono':'ID Bono',
    #                                 'isin':'ISIN',
    #                                 'px_sucio':'Precio Sucio',
    #                                 'cupon_dev':'Interes Devengado',
    #                                 'px_limpio':'Precio Limpio',
    #                                 'duracion':'Duracion',
    #                                 'convexidad':'Convexidad'})
    #              .style
    #              .format("{:.6f}")
    #     )
    
    
    # with st.expander("Flujos"):
    
    #     with st.form(key="isin_filter"):
    
    #         isin_selection = st.multiselect(
    #             label="Seleccione instrumento(s) a visualizar flujos:",
    #             options=df["id_bono"].unique(),
    #             default=df["id_bono"][0],
    #         )
            
    #         submit_button = st.form_submit_button(label="Submit")
    
    #     st.write(
    #         df_flujos[df_flujos["id_bono"].isin(isin_selection)]
    #         .drop(columns=["plazo_next"])
    #         .rename(columns = {'id_bono':'ID Bono',
    #                            'isin':'ISIN',
    #                            'fecha_cupon':'Fecha Cupon',|
    #                            'plazo':'Plazo',
    #                            'dias_cupon':'Dias Cupon',
    #                            'factor_descuento':'Factor Descuento',
    #                            'vp_flujo':'VP Flujo'})
    #     )
        
    # st.markdown("## Descarga Resultados")
    
    # with st.expander("Salida"):
        
    #     cs, c1, c2, c3, cLast = st.columns([2, 1.5, 1.5, 1.5, 2])
        
    #     with c1:
            
    #         st.download_button(label = "Valuación", 
    #                            data = convert_df_to_csv(df_valuacion),
    #                            file_name = "df_valuacion.csv"
    #                            )
            
    #     with c3:
            
    #         st.download_button(label = "Flujos", 
    #                            data = convert_df_to_csv(df_flujos),
    #                            file_name = "df_flujos.csv"
    #                            )
                