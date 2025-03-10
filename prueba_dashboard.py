import pandas as pd
import streamlit as st
import plotly.express as px
import seaborn as sns
#import streamlit_extras.metric_cards

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
    data_auditores = pd.read_csv("files/merged_para_dashboard (1).csv")
    return data_auditores

@st.cache_data
def get_data_vulcan_csv():
    data_vulcan = pd.read_csv("files/resultados_vulcan (4).csv")
    return data_vulcan

data_auditores = get_data_from_csv()
data_vulcan = get_data_vulcan_csv()

# --- SIDEBAR ----
st.sidebar.header("Filtra acá:")

# Filtro de Mes
mes = st.sidebar.multiselect("Selecciona el mes: ", options=data_auditores["Mes"].unique())

# Filtrar por Mes
data_filtrada_por_mes = data_auditores.query("Mes == @mes") if mes else data_auditores
vulcan_filtrado_por_mes = data_vulcan.query("Periodo == @mes") if mes else data_vulcan
# Total auditado del mes seleccionado
auditado_total_del_mes = data_filtrada_por_mes["Totales"].sum()

# Filtro de Auditor
auditor = st.sidebar.multiselect("Selecciona el auditor: ", options=data_filtrada_por_mes["Nombre"].unique())

# Filtrar por Auditor y Mes
data_filtrada_por_auditor = data_filtrada_por_mes.query("Nombre == @auditor") if auditor else data_filtrada_por_mes
data_vulcan_por_auditor = vulcan_filtrado_por_mes.query("Auditor == @auditor") if auditor else vulcan_filtrado_por_mes
# Filtro de Fecha
fecha = st.sidebar.multiselect("Selecciona la fecha: ", options=data_filtrada_por_auditor["Fecha"].unique())

# Filtrado con mes, auditor y fecha
df_seleccionado = data_filtrada_por_auditor.query("Fecha == @fecha") if fecha else data_filtrada_por_auditor
#df_seleccionado_vulcan = data_vulcan_por_auditor.query("Fecha de Auditoría == @fecha") if fecha else data_vulcan_por_auditor
# --- Main_page ----
st.title(":bar_chart: Datos de Auditores :chart_with_upwards_trend:")

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
    left, middle, right,border = st.columns(4)
    left.metric("Total auditado del mes",value = int(auditado_total_del_mes))
    middle.metric("Total del auditor", value = int(infracciones_auditor))
    right.metric("Porcentaje",value = round(porcentaje_audiciones_sobre_total_del_mes,2))
    resultados_por_mes = data_vulcan.groupby("Periodo").agg({"Total de rechazadas":["sum"], "Auditorías desaprobadas":["sum"]}).reset_index()
    resultados_por_mes["Porcentaje"] = (resultados_por_mes["Auditorías desaprobadas"] / resultados_por_mes["Total de rechazadas"])*100
    valor = round(((resultados_por_mes.iloc[1,3] - resultados_por_mes.iloc[0,3]) / resultados_por_mes.iloc[1,3])*100,1)
    if valor >= 0:
        delta = f"+{valor}%"
    else:
        delta = f"{valor}%"
    border.metric(
    "Resultados Octubre a Noviembre",
    value=f"{valor}%",
    delta=delta)

    style_metric_cards(background_color = "black", border_left_color="Aquamarine")
metrics()


div1, div2 = st.columns([5, 7])
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
        fig = px.bar(df_melted, y = "Nombre", x = "Valor",text_auto = ".2s", color = "Tipo", color_discrete_sequence=["LightSkyBlue", "LightPink", "LightGreen", "LightSalmon"])
        fig.update_traces(textfont_size = 18, textposition = "inside",marker=dict(line=dict(color='black', width=.5)))
        st.plotly_chart(fig, use_container_width=True)

barchar()
a,b = st.columns(2)

with a:
    #if not mes:
        #fig = px.line(data_vulcan_por_auditor, x="Fecha de Auditoría", y="Porcentaje de auditorías desaprobadas")
        #fig.update_traces(line=dict(color='Aquamarine'))
    auditorias_desaprobadas_por_mes = data_vulcan_por_auditor.groupby(["Auditor","Periodo"]).agg({"Total de rechazadas":["sum"], "Auditorías desaprobadas":["sum"]}).reset_index()
    auditorias_desaprobadas_por_mes.columns = ["Auditor", "Periodo","Total de rechazadas","Auditorias desaprobadas"]
    auditorias_desaprobadas_por_mes["Porcentaje mal rechazadas"] = (auditorias_desaprobadas_por_mes["Auditorias desaprobadas"] / auditorias_desaprobadas_por_mes["Total de rechazadas"])*100
    
    auditorias_desaprobadas_por_mes = auditorias_desaprobadas_por_mes.loc[(auditorias_desaprobadas_por_mes["Auditor"] != "Yanina Ybarra") & (auditorias_desaprobadas_por_mes["Auditor"] != "Stephani Ledesma")]
    auditorias_desaprobadas_por_mes["Porcentaje mal rechazadas (%)"] = auditorias_desaprobadas_por_mes["Porcentaje mal rechazadas"].apply(lambda x: f"{x:.2f}%")

    fig = px.bar(auditorias_desaprobadas_por_mes.sort_values(by="Porcentaje mal rechazadas", ascending=True), 
             x="Porcentaje mal rechazadas", y="Auditor", color="Periodo", 
             text="Porcentaje mal rechazadas (%)")
    fig.update_traces(textfont_size = 24, textposition = "inside",marker=dict(line=dict(color='black', width=.5)))


    #if mes and auditor:
    #    fig = px.line(data_vulcan_por_auditor, x="Fecha de Auditoría", y="Porcentaje de auditorías desaprobadas", color = "Auditor")

    #if not mes:
    #    agrupado = vulcan_filtrado_por_mes.groupby("Fecha de Auditoría").agg({"Total de rechazadas":["sum"], "Auditorías desaprobadas":["sum"]}).reset_index()
    #    agrupado.columns = ["Fecha de Auditoría", "Rechazadas", "Desaprobadas"]
    #    agrupado["Porcentaje de auditorías desaprobadas"] = round((agrupado["Desaprobadas"] / agrupado["Rechazadas"])*100,2)

    #    fig = px.line(agrupado, x="Fecha de Auditoría", y="Porcentaje de auditorías desaprobadas")
    #    fig.update_traces(line=dict(color='Aquamarine'))
    st.plotly_chart(fig, use_container_width=True)
with b:
    from streamlit_extras.metric_cards import style_metric_cards
    st.dataframe(auditorias_desaprobadas_por_mes.nsmallest(5, "Porcentaje mal rechazadas").drop(columns = "Porcentaje mal rechazadas"))
    resultados_por_mes = data_vulcan.groupby("Periodo").agg({"Total de rechazadas":["sum"], "Auditorías desaprobadas":["sum"]}).reset_index()
    resultados_por_mes["Porcentaje"] = (resultados_por_mes["Auditorías desaprobadas"] / resultados_por_mes["Total de rechazadas"])*100
    valor = round(((resultados_por_mes.iloc[1,3] - resultados_por_mes.iloc[0,3]) / resultados_por_mes.iloc[1,3])*100,1)
    if valor >= 0:
        delta = f"+{valor}%"
    else:
        delta = f"{valor}%"
    left, right = st.columns(2)
    if auditor and not mes and not fecha:
        desaprobados_total = data_vulcan.query("Auditor == @auditor").groupby(["Auditor","Periodo"]).agg({"Total de rechazadas":["sum"], "Auditorías desaprobadas":["sum"]}).unstack().reset_index()
        if desaprobados_total.shape[1] <=3:
            desaprobados_total.columns = ["Auditor", "Rechazadas", "Desaprobadas"]
            desaprobados_total["Porcentaje mal rechazadas"] = round((desaprobados_total["Desaprobadas"] / desaprobados_total["Rechazadas"])*100,2)
            desaprobados_total["Mejora"] = desaprobados_total["Porcentaje mal rechazadas"]
        else:
            desaprobados_total.columns = ["Auditor","Total rechazadas noviembre","Total rechazadas octubre", "Auditorías desaprobadas noviembre","Auditorías desaprobadas octubre"]
            desaprobados_total["Porcentaje mal rechazadas octubre"] = round((desaprobados_total["Auditorías desaprobadas octubre"] / desaprobados_total["Total rechazadas octubre"])*100,1)
            desaprobados_total["Porcentaje mal rechazadas octubre"] = desaprobados_total["Porcentaje mal rechazadas octubre"].fillna(0)
            desaprobados_total["Porcentaje mal rechazadas noviembre"] = round((desaprobados_total["Auditorías desaprobadas noviembre"] / desaprobados_total["Total rechazadas noviembre"])*100,1)
            desaprobados_total["Porcentaje mal rechazadas noviembre"] = desaprobados_total["Porcentaje mal rechazadas noviembre"].fillna(desaprobados_total["Porcentaje mal rechazadas octubre"])
            desaprobados_total = desaprobados_total[["Auditor","Porcentaje mal rechazadas octubre", "Porcentaje mal rechazadas noviembre"]]
            desaprobados_total["Mejora"] = round(((desaprobados_total["Porcentaje mal rechazadas octubre"] - desaprobados_total["Porcentaje mal rechazadas noviembre"])/desaprobados_total["Porcentaje mal rechazadas octubre"])*100,1)

        valor = round(desaprobados_total['Mejora'].iloc[0], 2)
        
        if valor >= 0:
            delta = f"+{valor}%"  # Flecha verde hacia arriba
        else:
            delta = f"{valor}%"  # Flecha roja hacia abajo
    
        left.metric(
            "Resultado respecto al mes\n pasado",
            value=f"{valor}%",
            delta=delta
        )
    style_metric_cards(background_color = "black", border_left_color="Aquamarine")
