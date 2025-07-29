import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Cargar datos ---
df = pd.read_csv("demanda_historica_y_predicha.csv", parse_dates=["Fecha"])
df = df.sort_values("Fecha")

# --- Parámetros desde la interfaz ---
st.sidebar.header("🔧 Parámetros de Simulación")

H = st.sidebar.slider("Radiación Solar H (kWh/m²)", 1.0, 8.0, 4.5, step=0.1)
PR = st.sidebar.slider("Performance Ratio (PR)", 0.60, 0.95, 0.80, step=0.01)

horizonte = st.sidebar.selectbox("Horizonte de Predicción", ["7 días", "15 días", "30 días"])
dias = int(horizonte.split()[0])

st.sidebar.subheader("Escenarios de Capacidad")
escenarios = {
    "Pequeña (100 kW)": st.sidebar.checkbox("Pequeña (100 kW)", value=True),
    "Mediana (1 MW)": st.sidebar.checkbox("Mediana (1 MW)", value=True),
    "Grande (5 MW)": st.sidebar.checkbox("Grande (5 MW)", value=True)
}

kwh_por_litro = st.sidebar.number_input("kWh/L (Diesel)", value=3.0, step=0.1)
co2_por_litro = st.sidebar.number_input("CO₂/L (kg)", value=2.2, step=0.1)
cop_diesel = st.sidebar.number_input("COP/L (Precio diesel)", value=2553.59, step=10.0)

# --- Filtrar datos predichos por cantidad de días ---
df_predicha = df[df["Tipo"] == "predicha"].copy()
df_sim = df_predicha.head(dias)  # 👈 Asegura que siempre haya datos
# st.write(f"Número de registros predichos cargados: {len(df_sim)}")  # Útil para depuración

# --- Título y explicación ---
st.title("☀️ Simulación de Energía Solar - Leticia, Colombia")

st.subheader("📈 Demanda Energética Predicha (Horizonte Seleccionado)")
st.markdown(f"🗓️ Mostrando demanda energética para los próximos **30 días** predichos.")
# Asegurarse de que los tipos están normalizados (evita errores de color_discrete_map)

# --- Asegurar formato y consistencia en los tipos ---
df["Tipo"] = df["Tipo"].str.capitalize()
df = df.sort_values("Fecha")

# --- Detectar la fecha de inicio de predicción ---
if "Predicha" in df["Tipo"].unique():
    inicio_pred = df[df["Tipo"] == "Predicha"]["Fecha"].min()
else:
    inicio_pred = None

# --- Crear la gráfica de línea ---
fig = px.line(
    df,
    x="Fecha",
    y="ACTIVA",
    color="Tipo",
    color_discrete_map={
        "Histórica": "#1d7a8d",
        "Predicha": "#ff6f00",
    },
    labels={
        "Fecha": "Fecha",
        "ACTIVA": "Demanda Energética (kWh)",
        "Tipo": "Tipo"
    },
    title="Serie Temporal de Demanda Energética"
)

# --- Mejorar estética ---
fig.update_traces(mode="lines+markers")
fig.update_layout(
    template="plotly_white",
    title_font=dict(size=20, family="Arial", color="#333"),
    xaxis_title_font=dict(size=16),
    yaxis_title_font=dict(size=16),
    legend=dict(title="", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=30, r=30, t=50, b=30)
)

# --- Mostrar gráfico en Streamlit ---
st.plotly_chart(fig, use_container_width=True)

# --- Beneficios por escenario ---
st.subheader("🌞 Beneficios por Escenario Solar")
st.markdown(f"🧮 Cálculo acumulado de beneficios para un horizonte de **{dias} días**.")

resultados = []

def calcular_beneficios(capacidad_kw, label):
    energia_generada_kwh = capacidad_kw * H * PR * dias
    diesel_ahorrado_l = energia_generada_kwh / kwh_por_litro
    co2_ev_l = diesel_ahorrado_l * co2_por_litro
    ahorro_cop = diesel_ahorrado_l * cop_diesel

    resultados.append({
        "Escenario": label,
        "Energía (kWh)": energia_generada_kwh,
        "Diésel Ahorrado (L)": diesel_ahorrado_l,
        "CO₂ Evitado (kg)": co2_ev_l,
        "Ahorro Económico (COP)": ahorro_cop
    })

    st.metric(f"{label} - Energía Generada Total", f"{energia_generada_kwh:,.0f} kWh")
    st.metric(f"{label} - Diésel Ahorrado", f"{diesel_ahorrado_l:,.0f} L")
    st.metric(f"{label} - CO₂ Evitado", f"{co2_ev_l:,.0f} kg")
    st.metric(f"{label} - Ahorro Económico", f"${ahorro_cop:,.0f} COP")

for nombre, activo in escenarios.items():
    if activo:
        capacidad_kw = 100 if "Pequeña" in nombre else 1000 if "Mediana" in nombre else 5000
        with st.expander(f"🔋 Resultados para {nombre}"):
            calcular_beneficios(capacidad_kw, nombre)

# --- Gráfica de barras logarítmica para comparación ---
if resultados:
    st.subheader("📊 Comparativa de Beneficios por Escenario")
    df_resultados = pd.DataFrame(resultados)

    fig_barras = px.bar(
        df_resultados.melt(id_vars="Escenario"),
        x="variable", y="value", color="Escenario",
        barmode="group",
        labels={"variable": "Indicador", "value": "Valor"},
        title="Comparativa de Beneficios"
    )

    fig_barras.update_layout(xaxis_title="", legend_title="Escenario")
    fig_barras.update_yaxes(type="log", title="Valor (escala logarítmica)")
    st.plotly_chart(fig_barras, use_container_width=True)

# --- Nota final ---
st.caption("Datos de demanda simulada para Leticia, Amazonas. Parámetros personalizables para análisis energético, económico y ambiental.")