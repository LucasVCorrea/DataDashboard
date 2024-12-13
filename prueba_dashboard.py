import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title = "Auditores Data", page_icon=":bar_chart:", layout="wide")
@st.cache_data
def get_data_from_csv():
    data_auditores = pd.read_csv("files/merged_para_dashboard.csv")
    return data_auditores

data_auditores = get_data_from_csv()
st.dataframe(data_auditores.head())

# --- SIDEBAR ----
st.sidebar.header("Filtra acá:")

# Filtro de Mes
mes = st.sidebar.multiselect("Selecciona el mes: ", options=data_auditores["Mes"].unique())

# Filtrar por Mes
data_filtrada_por_mes = data_auditores.query("Mes == @mes") if mes else data_auditores

# Total auditado del mes seleccionado
auditado_total_del_mes = data_filtrada_por_mes["Totales"].sum()

# Filtro de Auditor
auditor = st.sidebar.multiselect("Selecciona el auditor: ", options=data_filtrada_por_mes["Nombre"].unique())

# Filtrar por Auditor y Mes
data_filtrada_por_auditor = data_filtrada_por_mes.query("Nombre == @auditor") if auditor else data_filtrada_por_mes
# Filtro de Fecha
fecha = st.sidebar.multiselect("Selecciona la fecha: ", options=data_filtrada_por_auditor["Fecha"].unique())

# Filtrar por Fecha
df_seleccionado = data_filtrada_por_auditor.query("Fecha == @fecha") if fecha else data_filtrada_por_auditor

# --- Main_page ----
st.title(":bar_chart: Datos de Auditores")

# Total de infracciones del auditor seleccionado dentro del mes y/o fecha
if mes and auditor and fecha:
    infracciones_auditor = df_seleccionado["Totales"].sum()
elif mes and auditor:
    infracciones_auditor = data_filtrada_por_auditor["Totales"].sum()
else:
    infracciones_auditor = 0

# Porcentaje de audiciones del dataframe seleccionado sobre el total del mes
if mes and auditor:
    porcentaje_audiciones_sobre_total_del_mes = (
        df_seleccionado["Totales"].sum() * 100 / auditado_total_del_mes
    )
elif mes:
    porcentaje_audiciones_sobre_total_del_mes = (
        0
    ) if auditado_total_del_mes > 0 else 0
else:
    auditado_total_del_mes = 0
    porcentaje_audiciones_sobre_total_del_mes = 0

# Top
left, middle, right = st.columns(3)
with left:
    st.subheader(f"Total audiciones del mes: {int(auditado_total_del_mes)}")
with middle:
    st.subheader(f"Total del auditor: {int(infracciones_auditor)}")
with right:
    st.subheader(f"Porcentaje: {porcentaje_audiciones_sobre_total_del_mes:.1f}%")


#with middle:
#    st.subheader(f"Infracciones promedio: {infracciones_promedio}")

##    agrupado_camara = seleccion.groupby("Tipo de cámara").agg({"Infracciones Por Mes":["sum"]}).reset_index()
##   agrupado_camara.columns = ["Tipo de cámara", "Infracciones Por Mes"]
##    plot = sns.barplot(agrupado_camara, x = "Tipo de cámara", y = "Infracciones Por Mes", color = "RoyalBlue", edgecolor = "black", linewidth=.5)
##    sns.despine(top=False, right=True, left=True, bottom=False)
##    for container in plt.gca().containers:
##        plt.gca().bar_label(container, fontsize=10, color='black')

##    for text in plt.gca().texts:
##        valor = (float((text.get_text())))
##        text.set_text(f' {valor:.0f}')
##    plt.title(f"Cantidad de infracciones")
##    st.pyplot(plot.get_figure())