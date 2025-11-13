import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import ConnectionPatch
import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score


# Configuración de la página
st.set_page_config(page_title="Ingresos y Egresos", page_icon="💵", layout="wide")
st.title("💵 Ingresos y Egresos de los hogares de México")

# --- Cargar archivos de datos ---
local_file_gastos = "gastosUnificados.csv"
local_file_ingresos = "ingresosUnificados.csv"

if os.path.exists(local_file_gastos) and os.path.exists(local_file_ingresos):
    df_gastos = pd.read_csv(local_file_gastos)
    df_ingresos = pd.read_csv(local_file_ingresos)
    #st.success("Archivos cargados correctamente")
else:
    st.error("No se encontraron los archivos locales. Verifica los nombres o rutas.")
    st.stop()

# --- Limpieza inicial ---
# Convertir columnas numéricas
df_gastos['gasto_tri'] = pd.to_numeric(df_gastos['gasto_tri'], errors='coerce')
df_ingresos['ing_tri'] = pd.to_numeric(df_ingresos['ing_tri'], errors='coerce')

# Eliminar filas con valores NaN
df_gastos = df_gastos.dropna(subset=['gasto_tri'])
df_ingresos = df_ingresos.dropna(subset=['ing_tri'])

# --- Sidebar de Filtros ---
st.sidebar.header("Filtros")

# Obtener listas únicas de regiones y años
regiones = df_gastos['region'].unique()
anios = df_gastos['anio'].unique()

# Widgets de selección múltiple
region_seleccionada = st.sidebar.multiselect("Selecciona Región:", regiones, default=regiones)
anio_seleccionado = st.sidebar.multiselect("Selecciona Año:", anios, default=anios)

# --- Aplicar filtros a los DataFrames ---
df_gastos_filtrado = df_gastos[
    (df_gastos['region'].isin(region_seleccionada)) &
    (df_gastos['anio'].isin(anio_seleccionado))
]

df_ingresos_filtrado = df_ingresos[
    (df_ingresos['region'].isin(region_seleccionada)) &
    (df_ingresos['anio'].isin(anio_seleccionado))
]

# --- Gráfica 1: Total de Egresos por Entidad ---
st.subheader("📊 Egresos Totales por Entidad")

egresos_por_entidad = df_gastos_filtrado.groupby(["nombreEntidad2", "categoria"])['gasto_tri'].sum().reset_index()

fig_egresos = px.bar(
    egresos_por_entidad,
    x="nombreEntidad2",
    y="gasto_tri",
    title="Egresos Totales por Entidad",
    labels={"nombreEntidad2": "Entidad", "gasto_tri": "Egresos Totales"},
    color="categoria",
    barmode="stack"
)

st.plotly_chart(fig_egresos, use_container_width=True)

#####################
# --- Métricas de egresos ---
# Agrupar por entidad para obtener el total de egresos
totales_por_entidad_eg = df_gastos_filtrado.groupby("nombreEntidad2")['gasto_tri'].sum().reset_index()

# Identificar entidad con mayor y menor egreso
entidad_max_eg = totales_por_entidad_eg.loc[totales_por_entidad_eg['gasto_tri'].idxmax()]
entidad_min_eg = totales_por_entidad_eg.loc[totales_por_entidad_eg['gasto_tri'].idxmin()]

# Filtrar datos para entidad con mayor egreso
df_max_eg = df_gastos_filtrado[df_gastos_filtrado['nombreEntidad2'] == entidad_max_eg['nombreEntidad2']]
categoria_max_eg = df_max_eg.groupby("categoria")['gasto_tri'].sum().reset_index()
categoria_max_eg['porcentaje'] = (categoria_max_eg['gasto_tri'] / categoria_max_eg['gasto_tri'].sum()) * 100
categoria_mayor_max_eg = categoria_max_eg.loc[categoria_max_eg['gasto_tri'].idxmax()]
categoria_menor_max_eg = categoria_max_eg.loc[categoria_max_eg['gasto_tri'].idxmin()]

# Filtrar datos para entidad con menor egreso
df_min_eg = df_gastos_filtrado[df_gastos_filtrado['nombreEntidad2'] == entidad_min_eg['nombreEntidad2']]
categoria_min_eg = df_min_eg.groupby("categoria")['gasto_tri'].sum().reset_index()
categoria_min_eg['porcentaje'] = (categoria_min_eg['gasto_tri'] / categoria_min_eg['gasto_tri'].sum()) * 100
categoria_mayor_min_eg = categoria_min_eg.loc[categoria_min_eg['gasto_tri'].idxmax()]
categoria_menor_min_eg = categoria_min_eg.loc[categoria_min_eg['gasto_tri'].idxmin()]

# --- Mostrar las métricas en dos columnas ---
col1, col2 = st.columns(2)

# Columna 1: Entidad con mayor egreso
with col1:
    st.metric("🟢", entidad_max_eg['nombreEntidad2'], f"${entidad_max_eg['gasto_tri']:.2f}")
    st.markdown(
        f"<div style='font-size: 22px; color:#0A97B0;'>"
        f"{categoria_mayor_max_eg['categoria']}: {categoria_mayor_max_eg['porcentaje']:.2f} %"
        f"</div>", unsafe_allow_html=True
    )
    st.markdown(
        f"<div style='font-size: 22px; color:#F5004F;'>"
        f"{categoria_menor_max_eg['categoria']}: {categoria_menor_max_eg['porcentaje']:.2f} %"
        f"</div>", unsafe_allow_html=True
    )

# Columna 2: Entidad con menor egreso
with col2:
    st.metric("🔴", entidad_min_eg['nombreEntidad2'], f"${entidad_min_eg['gasto_tri']:.2f}")
    st.markdown(
        f"<div style='font-size: 22px; color:#0A97B0;'>"
        f"{categoria_mayor_min_eg['categoria']}: {categoria_mayor_min_eg['porcentaje']:.2f} %"
        f"</div>", unsafe_allow_html=True
    )
    st.markdown(
        f"<div style='font-size: 22px; color:#F5004F;'>"
        f"{categoria_menor_min_eg['categoria']}: {categoria_menor_min_eg['porcentaje']:.2f} %"
        f"</div>", unsafe_allow_html=True
        
    )

print("\n")

#####################

# --- Gráfica 2: Total de Ingresos por Entidad ---
st.subheader("📊 Ingresos Totales por Entidad")

ingresos_por_entidad = df_ingresos_filtrado.groupby(["nombreEntidad2", "descripcion"])['ing_tri'].sum().reset_index()

fig_ingresos = px.bar(
    ingresos_por_entidad,
    x="nombreEntidad2",
    y="ing_tri",
    title="Ingresos Totales por Entidad y Descripción",
    labels={"nombreEntidad2": "Entidad", "ing_tri": "Ingresos Totales"},
    color="descripcion",
    barmode="stack"
)

st.plotly_chart(fig_ingresos, use_container_width=True)

##################
# --- Métricas de ingresos ---
# Agrupar por entidad para obtener el total de ingresos
totales_por_entidad_ing = df_ingresos_filtrado.groupby("nombreEntidad2")['ing_tri'].sum().reset_index()

# Identificar entidad con mayor y menor ingreso
entidad_max_ing = totales_por_entidad_ing.loc[totales_por_entidad_ing['ing_tri'].idxmax()]
entidad_min_ing = totales_por_entidad_ing.loc[totales_por_entidad_ing['ing_tri'].idxmin()]

# Filtrar datos para entidad con mayor ingreso
df_max_ing = df_ingresos_filtrado[df_ingresos_filtrado['nombreEntidad2'] == entidad_max_ing['nombreEntidad2']]
categoria_max_ing = df_max_ing.groupby("descripcion")['ing_tri'].sum().reset_index()
categoria_max_ing['porcentaje'] = (categoria_max_ing['ing_tri'] / categoria_max_ing['ing_tri'].sum()) * 100
categoria_mayor_max_ing = categoria_max_ing.loc[categoria_max_ing['ing_tri'].idxmax()]
categoria_menor_max_ing = categoria_max_ing.loc[categoria_max_ing['ing_tri'].idxmin()]

# Filtrar datos para entidad con menor ingreso
df_min_ing = df_ingresos_filtrado[df_ingresos_filtrado['nombreEntidad2'] == entidad_min_ing['nombreEntidad2']]
categoria_min_ing = df_min_ing.groupby("descripcion")['ing_tri'].sum().reset_index()
categoria_min_ing['porcentaje'] = (categoria_min_ing['ing_tri'] / categoria_min_ing['ing_tri'].sum()) * 100
categoria_mayor_min_ing = categoria_min_ing.loc[categoria_min_ing['ing_tri'].idxmax()]
categoria_menor_min_ing = categoria_min_ing.loc[categoria_min_ing['ing_tri'].idxmin()]

# --- Mostrar las métricas en dos columnas ---
col1, col2 = st.columns(2)

# Columna 1: Entidad con mayor ingreso
with col1:
    st.metric("Entidad con Mayor Ingreso", entidad_max_ing['nombreEntidad2'], f"${entidad_max_ing['ing_tri']:.2f}")


# Columna 2: Entidad con menor ingreso
with col2:
    st.metric("Entidad con Menor Ingreso", entidad_min_ing['nombreEntidad2'], f"${entidad_min_ing['ing_tri']:.2f}")

##################

st.subheader("💹 Análisis de Utilidad")

# --- Selector de Año ---
anio_utilidad = st.selectbox("Selecciona un año:", anios)

# Filtrar DataFrames por el año seleccionado
df_gastos_anio = df_gastos[df_gastos['anio'] == anio_utilidad]
df_ingresos_anio = df_ingresos[df_ingresos['anio'] == anio_utilidad]

# Calcular utilidad por entidad (ingresos totales - egresos totales)
utilidad_por_entidad = (
    df_ingresos_anio.groupby("nombreEntidad2")['ing_tri'].sum() -
    df_gastos_anio.groupby("nombreEntidad2")['gasto_tri'].sum()
).reset_index(name="utilidad")

# Eliminar valores NaN (entidades sin datos completos en ingresos o egresos)
utilidad_por_entidad = utilidad_por_entidad.dropna()

# Identificar entidad con mayor y menor utilidad
entidad_max_utilidad = utilidad_por_entidad.loc[utilidad_por_entidad['utilidad'].idxmax()]
entidad_min_utilidad = utilidad_por_entidad.loc[utilidad_por_entidad['utilidad'].idxmin()]

# Obtener totales de ingresos y egresos para la entidad con mayor utilidad
ingresos_max_utilidad = df_ingresos_anio[df_ingresos_anio['nombreEntidad2'] == entidad_max_utilidad['nombreEntidad2']]['ing_tri'].sum()
egresos_max_utilidad = df_gastos_anio[df_gastos_anio['nombreEntidad2'] == entidad_max_utilidad['nombreEntidad2']]['gasto_tri'].sum()

# Obtener totales de ingresos y egresos para la entidad con menor utilidad
ingresos_min_utilidad = df_ingresos_anio[df_ingresos_anio['nombreEntidad2'] == entidad_min_utilidad['nombreEntidad2']]['ing_tri'].sum()
egresos_min_utilidad = df_gastos_anio[df_gastos_anio['nombreEntidad2'] == entidad_min_utilidad['nombreEntidad2']]['gasto_tri'].sum()

# --- Diseño en Tres Columnas ---
col1, col2, col3 = st.columns(3)

# --- Columna 1: Métrica de Utilidad ---
with col1:
    #st.markdown("### Utilidad por entidad")
    st.metric("🟢", entidad_max_utilidad['nombreEntidad2'], f"${entidad_max_utilidad['utilidad']:.2f}")
    st.metric("🔴", entidad_min_utilidad['nombreEntidad2'], f"${entidad_min_utilidad['utilidad']:.2f}")

# --- Columna 2: Gráfica para Entidad con Mayor Utilidad ---
with col2:
    #st.markdown(f"### 🟢 {entidad_max_utilidad['nombreEntidad2']}")
    fig_max_utilidad = px.bar(
        x=["Ingresos Totales", "Egresos Totales"],
        y=[ingresos_max_utilidad, egresos_max_utilidad],
        color=["Ingresos", "Egresos"],
        #title=f"Totales de Ingresos y Egresos - {entidad_max_utilidad['nombreEntidad2']}",
        labels={"x": "Tipo", "y": "Total ($)"}
    )
    st.plotly_chart(fig_max_utilidad, use_container_width=True)

# --- Columna 3: Gráfica para Entidad con Menor Utilidad ---
with col3:
    #st.markdown(f"### 🔴 {entidad_min_utilidad['nombreEntidad2']}")
    fig_min_utilidad = px.bar(
        x=["Ingresos Totales", "Egresos Totales"],
        y=[ingresos_min_utilidad, egresos_min_utilidad],
        color=["Ingresos", "Egresos"],
        #title=f"Totales de Ingresos y Egresos - {entidad_min_utilidad['nombreEntidad2']}",
        labels={"x": "Tipo", "y": "Total ($)"}
    )
    st.plotly_chart(fig_min_utilidad, use_container_width=True)

################

################
# Asegurarnos de que "gasto_tri" es numérico y manejar valores no convertibles
df_gastos["gasto_tri"] = pd.to_numeric(df_gastos["gasto_tri"], errors="coerce")

# --- Selección de Año ---
anios_disponibles = df_gastos["anio"].unique()
anio_elegido = st.selectbox("Selecciona un año para analizar:", sorted(anios_disponibles))

# Filtrar los datos por el año seleccionado
df_gastos_anio = df_gastos[df_gastos["anio"] == anio_elegido]

# --- Selección de Entidad ---
entidades_disponibles = df_gastos_anio["nombreEntidad2"].unique()
entidad_elegida = st.selectbox("Selecciona una entidad para analizar:", entidades_disponibles)

# Filtrar por la entidad seleccionada
datos_entidad = df_gastos_anio[df_gastos_anio["nombreEntidad2"] == entidad_elegida]

# --- Gráfico de Pastel: Distribución del gasto por categoría ---
gastos_por_categoria = (
    datos_entidad.groupby("categoria")["gasto_tri"].sum().reset_index()
)
fig_pie = px.pie(
    gastos_por_categoria,
    names="categoria",
    values="gasto_tri",
    title=f"Distribución del Gasto por Categoría en {entidad_elegida} ({anio_elegido})",
    color_discrete_sequence=px.colors.sequential.Plasma,
    hole=0.5
)

# --- Selección de Categoría para el Treemap ---
categorias_disponibles = gastos_por_categoria["categoria"].unique()
categoria_elegida = st.selectbox("Selecciona una categoría de egresos:", categorias_disponibles)

# Filtrar por la categoría seleccionada
datos_categoria = datos_entidad[datos_entidad["categoria"] == categoria_elegida]

# --- Gráfico de Treemap: Distribución del gasto por descripción dentro de la categoría ---
gastos_por_descripcion = (
    datos_categoria.groupby("descripcion")["gasto_tri"].sum().reset_index()
)
fig_treemap = px.treemap(
    gastos_por_descripcion,
    path=["descripcion"],
    values="gasto_tri",
    title=f"Gasto por Subcategorías en '{categoria_elegida}' ({anio_elegido})",
    color="gasto_tri",
    color_continuous_scale=px.colors.sequential.Viridis,
)

# --- Mostrar ambos gráficos lado a lado ---
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_pie, use_container_width=True)
with col2:
    st.plotly_chart(fig_treemap, use_container_width=True)

##############
# --- Filtrado de Ingresos por Año y Entidad ---
df_ingresos["ing_tri"] = pd.to_numeric(df_ingresos["ing_tri"], errors="coerce")

# Filtrar ingresos por año y entidad seleccionada
df_ingresos_anio = df_ingresos[df_ingresos["anio"] == anio_elegido]
datos_ingresos_entidad = df_ingresos_anio[df_ingresos_anio["nombreEntidad2"] == entidad_elegida]

# --- Gráfico de Pastel: Distribución del ingreso por descripción ---
ingresos_por_descripcion = (
    datos_ingresos_entidad.groupby("descripcion")["ing_tri"].sum().reset_index()
)
fig_pie_ingresos = px.pie(
    ingresos_por_descripcion,
    names="descripcion",
    values="ing_tri",
    title=f"Distribución del Ingreso por Descripción en {entidad_elegida} ({anio_elegido})",
    color_discrete_sequence=px.colors.sequential.Sunset,
    hole=0.5
)

# --- Filtrar el DataFrame de gastos por año y entidad seleccionados ---
df_gastos_filtrado = df_gastos[
    (df_gastos["nombreEntidad2"] == entidad_elegida) &
    (df_gastos["anio"] == anio_elegido)
]

# --- Gráfico de pastel: Distribución por "lugar_comp" ---
gastos_por_lugar = (
    df_gastos_filtrado.groupby("lugar_comp")["gasto_tri"].sum().reset_index()
)

fig_lugar_comp = px.pie(
    gastos_por_lugar,
    names="lugar_comp",
    values="gasto_tri",
    title="📍 Distribución del Gasto por Lugar de Compra",
    color_discrete_sequence=px.colors.sequential.Agsunset,
    hole=0.4
)

# --- Gráfico de pastel: Distribución por "forma_pag1" ---
gastos_por_forma_pago = (
    df_gastos_filtrado.groupby("forma_pag1")["gasto_tri"].sum().reset_index()
)

fig_forma_pago = px.pie(
    gastos_por_forma_pago,
    names="forma_pag1",
    values="gasto_tri",
    title="💳 Distribución del Gasto por Forma de Pago",
    color_discrete_sequence=px.colors.sequential.Agsunset,
    hole=0.4
)

# --- Mostrar ambos gráficos en columnas (uno debajo del otro) ---
#st.subheader("📊 Análisis de Lugar de Compra y Forma de Pago")
col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(fig_lugar_comp, use_container_width=True)
with col4:
    st.plotly_chart(fig_forma_pago, use_container_width=True)

##################

# Filtrar los datos por entidad y año seleccionados

df_filtrado = df_ingresos[
    (df_ingresos["nombreEntidad2"] == entidad_elegida) &
    (df_ingresos["anio"] == anio_elegido)
]
# Definir la relación entre los meses y las columnas de ingresos
meses = ["abril", "mayo", "junio", "julio", "agosto", "septiembre"]
columnas_ingresos = ["ing_6", "ing_5", "ing_4", "ing_3", "ing_2", "ing_1"]  # Invertir orden

# Calcular el total de ingresos por mes
totales_ingresos = []
for columna in columnas_ingresos:
    total_mes = df_filtrado[columna].sum()
    totales_ingresos.append(total_mes)

# Crear DataFrame auxiliar para el gráfico
df_ingresos_mensuales = pd.DataFrame({
    "Mes": meses,
    "Total Ingresos": totales_ingresos
})

# Gráfico de barras
st.subheader("📊 Total de Ingresos por Mes")
fig_ingresos_mensuales = px.bar(
    df_ingresos_mensuales,
    x="Mes",
    y="Total Ingresos",
    title=f"Total de Ingresos Mensuales en {entidad_elegida} - {anio_seleccionado}",
    labels={"Mes": "Mes", "Total Ingresos": "Ingresos Totales"},
    color="Total Ingresos",
    color_continuous_scale=px.colors.sequential.Sunset
)

# Mostrar el gráfico
st.plotly_chart(fig_ingresos_mensuales, use_container_width=True)


##################

# --- Cálculo de Métricas de Porcentajes ---
# Principal categoría de egresos
categoria_egresos_principal = gastos_por_categoria.sort_values(by="gasto_tri", ascending=False).iloc[0]
categoria_egresos_nombre = categoria_egresos_principal["categoria"]
categoria_egresos_valor = categoria_egresos_principal["gasto_tri"]
categoria_egresos_porcentaje = (categoria_egresos_valor / gastos_por_categoria["gasto_tri"].sum()) * 100

# Principal categoría de ingresos
categoria_ingresos_principal = ingresos_por_descripcion.sort_values(by="ing_tri", ascending=False).iloc[0]
categoria_ingresos_nombre = categoria_ingresos_principal["descripcion"]
categoria_ingresos_valor = categoria_ingresos_principal["ing_tri"]
categoria_ingresos_porcentaje = (categoria_ingresos_valor / ingresos_por_descripcion["ing_tri"].sum()) * 100

# utilidad
df_gastos_filtrado = df_gastos[
    (df_gastos["nombreEntidad2"] == entidad_elegida) &
    (df_gastos["anio"] == anio_elegido)
]
df_ingresos_filtrado = df_ingresos[
    (df_ingresos["nombreEntidad2"] == entidad_elegida) &
    (df_ingresos["anio"] == anio_elegido)
]
############ EGRESOS POR CATEGORÍA
# Filtro de categorías de egresos
categorias_disponibles = df_gastos['categoria'].unique()
categoria_seleccionada = st.selectbox("Selecciona una categoría de egresos:", categorias_disponibles)

# Filtrar los datos por año y categoría seleccionada
df_gastos_filtrado_categoria = df_gastos[
    (df_gastos['anio'] == anio_elegido) &
    (df_gastos['categoria'] == categoria_seleccionada)
]

# Agrupar por entidad y sumar los gastos
gastos_por_entidad = df_gastos_filtrado_categoria.groupby('nombreEntidad2')['gasto_tri'].sum().reset_index()

# Crear un gráfico de barras
fig_barras = px.bar(
    gastos_por_entidad,
    x='nombreEntidad2',
    y='gasto_tri',
    title=f"Total de Egresos por Entidad en '{categoria_seleccionada}' - Año {anio_seleccionado}",
    labels={'gasto_tri': 'Total de Egresos', 'nombreEntidad2': 'Entidad'},
    color='gasto_tri',
    color_continuous_scale='Viridis'
)

# Mostrar el gráfico
st.plotly_chart(fig_barras, use_container_width=True)

############
# --- Calcular totales de ingresos y egresos ---
total_ingresos = df_ingresos_filtrado["ing_tri"].sum()
total_egresos = df_gastos_filtrado["gasto_tri"].sum()

# --- Calcular la utilidad ---
utilidad = total_ingresos - total_egresos


# --- Mostrar Gráficos y Métricas ---
#col1, col2 = st.columns(2)
    # Gráfico de pastel para ingresos
st.plotly_chart(fig_pie_ingresos, use_container_width=True)
col1, col2, col3 = st.columns(3)
with col1:
    # Métrica principal de egresos
    st.markdown(f"""
        ### 🟦 Principal categoría de Ingresos  
        **{categoria_ingresos_nombre}**  
        # {categoria_ingresos_porcentaje:.2f}%
    """)
with col2:
    # Métrica principal de ingresos
    st.markdown(f"""
    ### 🟧 Principal categoría de Egresos  
    **{categoria_egresos_nombre}**  
    # {categoria_egresos_porcentaje:.2f}%
    """)
with col3:
    # Métrica de utilidad
    st.markdown(f"""
    ### 🏦 Utilidad de la Entidad  
    La **utilidad** de **{entidad_elegida}** en el año **{anio_elegido}** es:  
    # {utilidad:,.2f} 💵  
    """)

#### PATRONES DE CONSUMO

# Filtrado del DataFrame por año
df_gastos_filtrado = df_gastos[df_gastos["anio"] == anio_elegido]

# Obtener la categoría con mayor y menor gasto por entidad
resultado = []

for entidad in df_gastos_filtrado["nombreEntidad2"].unique():
    datos_entidad = df_gastos_filtrado[df_gastos_filtrado["nombreEntidad2"] == entidad]
    
    # Agrupar por categoría y calcular el gasto total
    gasto_por_categoria = datos_entidad.groupby("categoria")["gasto_tri"].sum().reset_index()
    
    # Encontrar la categoría con mayor y menor gasto
    categoria_max = gasto_por_categoria.loc[gasto_por_categoria["gasto_tri"].idxmax()]
    categoria_min = gasto_por_categoria.loc[gasto_por_categoria["gasto_tri"].idxmin()]
    
    # Guardar los resultados
    resultado.append({
        "Entidad": entidad,
        "Categoría Mayor": categoria_max["categoria"],
        "Categoría Menor": categoria_min["categoria"]
    })

# Convertir a DataFrame
df_resultado = pd.DataFrame(resultado)

# Eliminar columnas de totales
df_resultado = df_resultado.drop(columns=["Total Mayor", "Total Menor"], errors="ignore")

# Transponer la tabla
df_resultado_transpuesta = df_resultado.set_index("Entidad").T

# Categorías más repetidas
categoria_mas_repetida_mayor = df_resultado["Categoría Mayor"].mode()[0]
categoria_mas_repetida_menor = df_resultado["Categoría Menor"].mode()[0]

# Función para destacar entidades que coinciden con la categoría más repetida
def destacar_patron(s):
    return ["background-color: #8BD8E3" if val == categoria_mas_repetida_mayor or val == categoria_mas_repetida_menor else "" for val in s]

# Aplicar formato a la tabla
st.subheader("Patrones de consumo por entidad")
st.dataframe(df_resultado_transpuesta.style.apply(destacar_patron, axis=1))

# Mostrar las categorías más repetidas
st.subheader("Categorías más repetidas")
st.write(f"**Mayor gasto:** {categoria_mas_repetida_mayor}")
st.write(f"**Menor gasto:** {categoria_mas_repetida_menor}")



############### REGRESIÓN
####### prueba regresión
# Combinar datos de ingresos y gastos por entidad
merged_data = df_ingresos.groupby("nombreEntidad2")["ing_tri"].sum().reset_index().merge(
    df_gastos.groupby("nombreEntidad2")["gasto_tri"].sum().reset_index(), 
    on="nombreEntidad2", 
    how="inner"
)

    # Renombrar columnas para mayor claridad
merged_data.columns = ["Entidad", "Ingreso total", "Egreso total"]

    # Visualizar datos en un scatter plot
fig_scatter = px.scatter(
        merged_data, x="Ingreso total", y="Egreso total",
        title="Relación entre Ingresos y Egresos totales",
        labels={"Ingreso total": "Ingreso total", "Egreso total": "Egreso total"},
        trendline="ols"  # Agrega una línea de tendencia
)
st.plotly_chart(fig_scatter, use_container_width=True)

    # Preparar datos para el modelo
X = merged_data[["Ingreso total"]].values  # Variable independiente
y = merged_data["Egreso total"].values  # Variable dependiente

    # Dividir en datos de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Crear el modelo y entrenarlo
model = LinearRegression()
model.fit(X_train, y_train)

    # Predicciones
y_pred = model.predict(X_test)

    # Evaluar el modelo
r2 = r2_score(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)

    # Mostrar resultados del modelo
st.write(f"Correlación (R²): {r2}")
#st.write(f"Correlación (R²): #{r2:.2f}")
st.write(f"Error cuadrático medio (MSE): {mse:.2f}")

############ MAPAS
local_geojson_file = "mexico.json"

# Cargar archivos si existen
if not (local_file_gastos and local_file_ingresos and local_geojson_file):
    st.error("No se encontraron los archivos necesarios. Verifica los nombres o rutas.")
    st.stop()

# Asegurarnos de que las columnas son numéricas
df_gastos["gasto_tri"] = pd.to_numeric(df_gastos["gasto_tri"], errors="coerce")
df_ingresos["ing_tri"] = pd.to_numeric(df_ingresos["ing_tri"], errors="coerce")

# Agrupar por entidad
gasto_por_entidad = df_gastos.groupby("nombreEntidad2")["gasto_tri"].sum().reset_index()
gasto_por_entidad = gasto_por_entidad.rename(columns={"nombreEntidad2": "Estado", "gasto_tri": "Gasto Total"})

ingresos_por_entidad = df_ingresos.groupby("nombreEntidad2")["ing_tri"].sum().reset_index()
ingresos_por_entidad = ingresos_por_entidad.rename(columns={"nombreEntidad2": "Estado", "ing_tri": "Ingreso Total"})

# Cargar coordenadas del archivo JSON
with open(local_geojson_file, "r") as f:
    geojson_data = json.load(f)

# Crear DataFrame con coordenadas
estados = [item["label"] for item in geojson_data]
latitudes = [item["lat"] for item in geojson_data]
longitudes = [item["lng"] for item in geojson_data]

df_coords = pd.DataFrame({
    "Estado": estados,
    "Latitud": latitudes,
    "Longitud": longitudes
})

# --- Combinar los datos con las coordenadas ---
mapa_gastos = pd.merge(df_coords, gasto_por_entidad, on="Estado", how="left")
mapa_gastos["Gasto Total"].fillna(0, inplace=True)

mapa_ingresos = pd.merge(df_coords, ingresos_por_entidad, on="Estado", how="left")
mapa_ingresos["Ingreso Total"].fillna(0, inplace=True)

# --- Mostrar Mapas en Streamlit ---

fig_gastos = px.scatter_geo(
    mapa_gastos,
    lat="Latitud",
    lon="Longitud",
    hover_name="Estado",
    size="Gasto Total",
    color="Gasto Total",
    color_continuous_scale="Plasma",
    #title="Gasto Total Trimestral por Estado en México",
    scope="north america"
)
fig_gastos.update_geos(center={"lat": 23.6345, "lon": -102.5528}, projection_scale=5)


fig_ingresos = px.scatter_geo(
    mapa_ingresos,
    lat="Latitud",
    lon="Longitud",
    hover_name="Estado",
    size="Ingreso Total",
    color="Ingreso Total",
    color_continuous_scale="Viridis",
    #title="Ingreso Total Trimestral por Estado en México",
    scope="north america"
)
fig_ingresos.update_geos(center={"lat": 23.6345, "lon": -102.5528}, projection_scale=5)


col1, col2= st.columns(2)

with col1:
    st.subheader("💰 Gastos totales por entidad")
    st.plotly_chart(fig_gastos, use_container_width=True)
with col2:
    st.subheader("💵 Ingresos totales por entidad")
    st.plotly_chart(fig_ingresos, use_container_width=True)