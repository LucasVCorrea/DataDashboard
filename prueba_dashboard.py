import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from pygments.styles.dracula import background

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

#st.dataframe(df_seleccionado)

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

# Top
left, middle, right = st.columns(3)
with left:
    st.subheader(f"Total audiciones del mes: {int(auditado_total_del_mes)}")
with middle:
    st.subheader(f"Total del auditor: {int(infracciones_auditor)}")
with right:
    st.subheader(f"Porcentaje: {porcentaje_audiciones_sobre_total_del_mes:.1f}%")

#Plot del total auditado en el/los mes/meses
sns.set_style(rc = {'axes.facecolor': '#00172B'})

fig_totales, ax_totales = plt.subplots(figsize=(12, 8))
data_filtrada_por_mes_totales = data_filtrada_por_mes.groupby("Nombre").agg({"Totales":["sum"]}).reset_index()
data_filtrada_por_mes_totales.columns = ["Nombre", "Total auditado"]
fig_totales.patch.set_facecolor("#00172B")
sns.barplot(
    data=data_filtrada_por_mes_totales.sort_values(by="Total auditado", ascending=False),
    y="Nombre",
    x="Total auditado",
    color="RoyalBlue",
    edgecolor="white",
    linewidth=0.5,
    ax=ax_totales
)


for container in ax_totales.containers:
    ax_totales.bar_label(container, fontsize=12, color='white', label_type="center")

for text in ax_totales.texts:
    valor = float(text.get_text())
    text.set_text(f' {valor:.0f}')

meses_seleccionados = ', '.join(data_filtrada_por_mes["Mes"].unique())
ax_totales.set_title(f"Total auditado en {meses_seleccionados}", fontsize=20, color = "white")
sns.despine(ax=ax_totales, top=True, right=True, left=False, bottom=False)
plt.ylabel("Nombre",color = "white")
plt.xlabel("Total auditado", color = "white")
plt.xticks(color = "white")
plt.yticks(color = "white")

# Plot de porcentajes
auditado_total_del_mes_plot = data_filtrada_por_mes_totales["Total auditado"].sum()
fig_porcentajes, ax_porcentajes = plt.subplots(figsize=(12, 8))
fig_porcentajes.patch.set_facecolor("#00172B")

data_filtrada_por_mes_totales["Porcentaje"] = (data_filtrada_por_mes_totales["Total auditado"] / auditado_total_del_mes_plot) * 100

sns.barplot(
    data=data_filtrada_por_mes_totales.sort_values(by="Porcentaje", ascending=False),
    y="Nombre",
    x="Porcentaje",
    color="RoyalBlue",
    edgecolor="white",
    linewidth=0.5,
    ax=ax_porcentajes
)
for container in ax_porcentajes.containers:
    ax_porcentajes.bar_label(container, fontsize=12, color='white', label_type="center")

for text in ax_porcentajes.texts:
    valor = float(text.get_text())
    text.set_text(f' {valor:.2f}%')

ax_porcentajes.set_title(f"Porcentaje auditado en {meses_seleccionados}",fontsize=20, color = "white")
sns.despine(ax=ax_porcentajes, top=True, right=True, left=False, bottom=False)
plt.ylabel("Nombre",color = "white")
plt.xlabel("Porcentaje", color = "white")
plt.xticks(color = "white")
plt.yticks(color = "white")

left_col, right_col = st.columns(2)
left_col.pyplot(fig_totales, use_container_width=True)
right_col.pyplot(fig_porcentajes, use_container_width=True)

left_col, right_col = st.columns(2)
total_aprobado_luces = data_filtrada_por_mes["Aprobado luces"].sum()
total_aprobado_semaforo = data_filtrada_por_mes["Aprobado semáforo"].sum()
total_rechazo_luces = data_filtrada_por_mes["Rechazo luces"].sum()
total_rechazo_semaforo = data_filtrada_por_mes["Rechazo semáforo"].sum()


data = [total_aprobado_luces, total_aprobado_semaforo, total_rechazo_semaforo, total_rechazo_luces]
keys = ['Aprobado de luces', 'Aprobado de semáforo', "Rechazo de semáforo", "Rechazo de luces"]
palette_color = sns.light_palette('RoyalBlue')
fig, ax = plt.subplots(figsize = (2,4))
ax.pie(data, labels=keys, colors=palette_color, autopct='%.1f%%',textprops={'fontsize': 5, 'color' : "white"})
fig.patch.set_facecolor("#00172B")
plt.title(f"Porcentaje de auditorias en {meses_seleccionados}", fontsize=6, color = "white")

# Mostrar la figura en Streamlit
left_col.pyplot(fig, use_container_width=True)

if mes and fecha:

    data_filtrada_por_fecha_totales = data_filtrada_por_mes.query("Fecha == @fecha").groupby("Nombre").agg({"Totales":["sum"]}).reset_index()
    data_filtrada_por_fecha_totales.columns = ["Nombre", "Total auditado"]
    # Plot del total auditado en el/los mes/meses
    fig_totales, ax_totales = plt.subplots(figsize=(10, 6))

    sns.barplot(
        data=data_filtrada_por_fecha_totales.sort_values(by="Total auditado", ascending=False),
        y="Nombre",
        x="Total auditado",
        color="RoyalBlue",
        edgecolor="black",
        linewidth=0.5,
        ax=ax_totales
    )

    for container in ax_totales.containers:
        ax_totales.bar_label(container, fontsize=11, color='black', label_type="center")

    for text in ax_totales.texts:
        valor = float(text.get_text())
        text.set_text(f' {valor:.0f}')

    dias_seleccionados = ', '.join(data_filtrada_por_mes.query("Fecha == @fecha")["Fecha"].unique())
    ax_totales.set_title(f"Total auditado el {dias_seleccionados}")
    sns.despine(ax=ax_totales, top=True, right=True, left=False, bottom=False)

    # Plot de porcentajes
    auditado_total_del_mes_plot = data_filtrada_por_fecha_totales["Total auditado"].sum()
    fig_porcentajes, ax_porcentajes = plt.subplots(figsize=(10, 6))
    data_filtrada_por_fecha_totales["Porcentaje"] = (data_filtrada_por_fecha_totales["Total auditado"] / auditado_total_del_mes_plot) * 100

    sns.barplot(
        data=data_filtrada_por_fecha_totales.sort_values(by="Porcentaje", ascending=False),
        y="Nombre",
        x="Porcentaje",
        color="RoyalBlue",
        edgecolor="black",
        linewidth=0.5,
        ax=ax_porcentajes
    )

    for container in ax_porcentajes.containers:
        ax_porcentajes.bar_label(container, fontsize=11, color='black', label_type="center")

    for text in ax_porcentajes.texts:
        valor = float(text.get_text())
        text.set_text(f' {valor:.2f}%')

    ax_porcentajes.set_title(f"Porcentaje auditado en {dias_seleccionados}")
    sns.despine(ax=ax_porcentajes, top=True, right=True, left=False, bottom=False)
# Mostrar los gráficos en columnas separadas en Streamlit
    left_col, right_col = st.columns(2)
    left_col.pyplot(fig_totales, use_container_width=True)
    right_col.pyplot(fig_porcentajes, use_container_width=True)
