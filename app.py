
import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================
# CONFIGURACIÓN INICIAL
# ==========================
st.set_page_config(page_title="Fan Value Engine", layout="wide", page_icon="⚽")

# Estilo oscuro básico
st.markdown("""
    <style>
    body {
        background-color: #0D1117;
        color: white;
    }
    .stApp {
        background-color: #0D1117;
    }
    .stSelectbox, .stNumberInput, .stTextInput {
        background-color: #161B22;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================
# CARGA DE DATOS
# ==========================
df_fans = pd.read_csv("fan_data.csv")
df_resumen = pd.read_csv("resumen_clusters.csv")

# ==========================
# SIDEBAR
# ==========================
st.sidebar.title("📊 Fan Value Engine")
seccion = seccion = st.sidebar.radio("Ir a sección:", [
    "Resumen General",
    "Segmentación por Clusters",
    "Detalle Individual",
    "Análisis Avanzado"
])


# ==========================
# RESUMEN GENERAL
# ==========================
if seccion == "Resumen General":
    st.title("📈 Overview General de la Afición")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Fans", f"{len(df_fans):,}")
    col2.metric("Fan Score Medio", f"{df_fans['Fan_Score'].mean():.1f}")
    premium_pct = (df_fans[df_fans['Nivel_Fan'] == 'Premium'].shape[0] / len(df_fans)) * 100
    col3.metric("% Fans Premium", f"{premium_pct:.1f}%")

    st.subheader("📊 Distribución del Fan Score")
    fig_hist = px.histogram(df_fans, x="Fan_Score", nbins=20, title="Histograma del Fan Score", color_discrete_sequence=["#00F5A0"])
    st.plotly_chart(fig_hist, use_container_width=True)

    st.subheader("🧩 Reparto por Nivel de Fan")
    fig_pie = px.pie(df_fans, names="Nivel_Fan", title="Distribución de Niveles", color_discrete_sequence=px.colors.sequential.Teal)
    st.plotly_chart(fig_pie, use_container_width=True)

# ==========================
# SEGMENTACIÓN POR CLUSTERS
# ==========================
elif seccion == "Segmentación por Clusters":
    st.title("🔍 Análisis de Clusters")

    st.subheader("📋 Resumen por Cluster")
    st.dataframe(df_resumen)

    st.subheader("📊 Fan Score medio por Cluster")
    fig_bar = px.bar(df_resumen, x="Cluster", y="Fan_Score", color="Cluster", color_discrete_sequence=px.colors.sequential.Teal)
    st.plotly_chart(fig_bar, use_container_width=True)

    
    
    niveles = ["Alto", "Medio", "Bajo", "Dormido"]
    st.subheader("📊 Distribución % por Nivel de Fan")

    # Asegurarse de que las columnas estén presentes
    niveles_validos = [col for col in ['Alto', 'Medio', 'Bajo', 'Dormido'] if col in df_resumen.columns]

    # Si hay columnas disponibles, hacer melt y graficar
    if niveles_validos:
        df_largo = df_resumen[["Cluster"] + niveles_validos].melt(id_vars="Cluster",
                                                                   var_name="Nivel_Fan",
                                                                   value_name="Porcentaje")
        fig_grouped = px.bar(df_largo, x="Cluster", y="Porcentaje", color="Nivel_Fan",
                             barmode="group", title="Distribución por Nivel de Fan",
                             color_discrete_sequence=px.colors.sequential.Teal)
        st.plotly_chart(fig_grouped, use_container_width=True)
    else:
        st.warning("No hay columnas de nivel válidas para graficar.")





# ==========================
# DETALLE INDIVIDUAL
# ==========================
elif seccion == "Detalle Individual":
    st.title("👤 Perfil del Aficionado")

    fan_id = st.selectbox("Selecciona un Fan ID", df_fans["Fan_ID"].unique())
    fan = df_fans[df_fans["Fan_ID"] == fan_id].iloc[0]

    col1, col2 = st.columns(2)
    col1.metric("Fan Score", round(fan["Fan_Score"], 1))
    col2.metric("Nivel", fan["Nivel_Fan"])

    st.subheader("📊 Comportamiento Individual")
    variables = ["Frecuencia_Visitas_Web", "Interacciones_RRSS", "Compras_Ecommerce", "Gasto_Total_€", "Asistencias_Estadio"]
    valores = [fan[var] for var in variables]
    df_comp = pd.DataFrame({"Variable": variables, "Valor": valores})
    fig_comp = px.bar(df_comp, x="Variable", y="Valor", color="Variable", color_discrete_sequence=px.colors.sequential.Teal)
    st.plotly_chart(fig_comp, use_container_width=True)





elif seccion == "Análisis Avanzado":
    st.title("📈 Análisis Avanzado de Fans")

    # ===============================
    # 🔘 Radar Reescalado de Comportamiento Digital
    # ===============================
    st.subheader("🔘 Radar Reescalado por Cluster")

    from sklearn.preprocessing import MinMaxScaler
    columnas_radar = ['Frecuencia_Visitas_Web', 'Interacciones_RRSS', 'Compras_Ecommerce',
                      'Participacion_Encuestas', 'Seguimiento_App_Oficial', 'Newsletter_ClickRate']
    df_radar = df_fans.groupby("Cluster")[columnas_radar].mean()
    scaler = MinMaxScaler()
    df_radar_scaled = pd.DataFrame(scaler.fit_transform(df_radar), columns=columnas_radar, index=df_radar.index)

    import plotly.graph_objects as go
    fig_radar = go.Figure()
    for cluster in df_radar_scaled.index:
        fig_radar.add_trace(go.Scatterpolar(
            r=df_radar_scaled.loc[cluster].values,
            theta=columnas_radar,
            fill='toself',
            name=f"Cluster {cluster}"
        ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=True,
        title="🔘 Radar Normalizado de Comportamiento Digital"
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # ===============================
    # 🔥 Heatmap por Cluster
    # ===============================
    st.subheader("🔥 Heatmap de Variables Digitales por Cluster")

    import plotly.express as px
    df_heatmap = df_radar_scaled.reset_index().melt(id_vars="Cluster", var_name="Variable", value_name="Valor_Normalizado")
    fig_heatmap = px.density_heatmap(df_heatmap, x="Variable", y="Cluster", z="Valor_Normalizado", 
                                     color_continuous_scale="Teal", title="Heatmap de Comportamiento Digital")
    st.plotly_chart(fig_heatmap, use_container_width=True)
