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



# ----  Main Interface -------

st.write("# Calculadora Renta Fija - COAP")

# st.write(
#         """     
# -   1. Su primer función es ingresar un set de datos con la siguiente información del instrumento a evaluar
# -   2. Los datos precargados pueden alterarse o bien ingresar un nuevo intrumento a valuar.
# 	    """
#     )

#st.markdown("#### La siguiente aplicación genera la valuación de instrumentos de renta fija, se tienen habilitado "
#            "realizar la valuación de manera individual o generar la valuación de una cartera completa.")

st.markdown("#")

st.markdown("#### Para continuar, seleccione el procedimiento que desee realizar en el menú del lado izquierdo.")

        
            
            
            
    
    
