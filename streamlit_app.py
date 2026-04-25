import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Asistente Financiero MERY", layout="wide")

st.title("📊 Asistente de Optimización Fiscal")
st.markdown("---")

# Carga de archivos
st.sidebar.header("Carga de Datos")
uploaded_files = st.sidebar.file_uploader("Sube tus archivos CSV de meses", type=["csv"], accept_multiple_files=True)

def procesar_datos(uploaded_files):
    lista_dataframes = []
    
    for file in uploaded_files:
        # Evitamos archivos de resumen o escenarios
        if "Resumen" in file.name or "Escenarios" in file.name:
            continue
            
        try:
            # Leer el archivo
            df = pd.read_csv(file)
            
            # Extraer el mes del nombre del archivo (asumiendo formato ".... - Abr.csv")
            # Ajustamos la lógica para capturar la parte del mes
            nombre = file.name
            partes = nombre.split(' - ')
            mes = partes[1].split('.')[0] if len(partes) > 1 else "Desconocido"
            
            # Validar que existan columnas requeridas
            if 'ITEM' in df.columns and 'COP' in df.columns:
                df_clean = df[['ITEM', 'COP']].copy()
                df_clean = df_clean.dropna(subset=['ITEM', 'COP'])
                df_clean['Mes'] = mes
                lista_dataframes.append(df_clean)
        except Exception:
            continue
            
    if not lista_dataframes:
        return None
        
    return pd.concat(lista_dataframes, ignore_index=True)

if uploaded_files:
    df_consolidado = procesar_datos(uploaded_files)
    
    if df_consolidado is not None:
        # Agrupar por mes
        resumen = df_consolidado.groupby('Mes')['COP'].sum().reset_index()
        
        # Ordenar meses (lógica simple de ordenamiento)
        orden = ['Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sept', 'Oct', 'Nov', 'Dic']
        resumen['Mes'] = pd.Categorical(resumen['Mes'], categories=orden, ordered=True)
        resumen = resumen.sort_values('Mes')
        
        # --- SECCIÓN DE VISUALIZACIÓN ---
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.write("### 📋 Cuadro Detallado")
            st.dataframe(resumen.style.format({'COP': '{:,.0f}'}), use_container_width=True)
            
            st.write("### 📝 Explicación")
            st.info("""
            Este tablero consolida los costos operativos.
            - **Análisis:** Visualización de carga financiera mensual.
            - **Datos:** Sumatoria total de COP por archivo procesado.
            """)

        with col2:
            st.write("### 📉 Análisis Gráfico")
            
            tab1, tab2, tab3 = st.tabs(["Barras", "Líneas", "Pastel"])
            
            with tab1:
                fig_bar = px.bar(resumen, x='Mes', y='COP', title='Total Costos por Mes', color='COP')
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with tab2:
                fig_line = px.line(resumen, x='Mes', y='COP', title='Tendencia de Costos', markers=True)
                st.plotly_chart(fig_line, use_container_width=True)
                
            with tab3:
                fig_pie = px.pie(resumen, values='COP', names='Mes', title='Distribución Porcentual Anual')
                st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.error("No se pudo extraer información válida de los archivos CSV.")
else:
    st.info("👈 Por favor, sube los archivos CSV desde la barra lateral para comenzar el análisis.")
