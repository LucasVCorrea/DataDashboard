import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title = "Auditores Data", page_icon=":bar_chart:", layout="wide")

hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """
st.markdown(hide_st_style, unsafe_allow_html=True)
@st.cache_data
def get_data_from_csv():
    data_auditores = pd.read_csv("files/merged_para_dashboard.csv")
    return data_auditores

data_auditores = get_data_from_csv()
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
    #auditado_total_del_mes = 0
    porcentaje_audiciones_sobre_total_del_mes = 0

def metrics():
    from streamlit_extras.metric_cards import style_metric_cards
    left, middle, right = st.columns(3)
    left.metric("Total auditado del mes",value = int(auditado_total_del_mes))
    middle.metric("Total del auditor", value = int(infracciones_auditor))
    right.metric("Porcentaje",value = round(porcentaje_audiciones_sobre_total_del_mes,2))

    style_metric_cards(background_color = "black", border_left_color="pink")
metrics()


div1, div2 = st.columns(2)
def pie():
    with div1:
        thme_plotly = None
        fig = px.pie(data_filtrada_por_mes, values="Totales", names="Nombre", title = "Total auditado")
        fig.update_layout(legend_title= "Auditores", legend_y = 0.9)
        fig.update_traces(textinfo=None, textposition="inside", marker=dict(line=dict(color='black', width=.5)))
        st.plotly_chart(fig, use_container_width=True, theme = thme_plotly)
pie()

def barchar():
    with div2:
        df_agrupado = df_seleccionado.groupby("Nombre").agg({"Aprobado luces":["sum"],"Rechazo luces":["sum"],"Aprobado semáforo":["sum"],"Rechazo semáforo":["sum"]}).reset_index()
        df_agrupado.columns = ["Nombre","Aprobado luces","Rechazo luces","Aprobado semáforo","Rechazo semáforo"]
        total = df_agrupado.copy()
        total["total"] = total.sum(axis = 1, numeric_only = True)

        df_melted = df_agrupado.melt(id_vars="Nombre", var_name="Tipo", value_name="Valor")
        df_melted = pd.merge(df_melted, total, on = "Nombre")
        df_melted = df_melted.sort_values(by = "total")
        fig = px.bar(df_melted, y = "Nombre", x = "Valor",text_auto = ".2s", color = "Tipo")
        fig.update_traces(textfont_size = 18, textposition = "inside",marker=dict(line=dict(color='black', width=.5)))
        st.plotly_chart(fig, use_container_width=True)

barchar()