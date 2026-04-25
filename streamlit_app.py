import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Asistente Financiero MERY", layout="wide")

st.title("📊 Asistente de Optimización Fiscal")
st.markdown("---")

# 1. Carga de archivos
uploaded_file = st.file_uploader("Sube el archivo Excel de proyecciones", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Leer todas las hojas
        archivo_excel = pd.read_excel(uploaded_file, sheet_name=None, header=2)
        
        lista_dataframes = []
        meses_validos = ['Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        
        for nombre_hoja, df in archivo_excel.items():
            # Filtramos solo las hojas de meses
            if nombre_hoja in meses_validos:
                df_clean = df[['ITEM', 'COP', 'USD']].copy()
                df_clean = df_clean.dropna(subset=['ITEM'])
                df_clean['Mes'] = nombre_hoja
                lista_dataframes.append(df_clean)
        
        df_consolidado = pd.concat(lista_dataframes, ignore_index=True)
        
        # Procesar resumen
        resumen = df_consolidado.groupby('Mes')['COP'].sum().reset_index()
        orden_meses = meses_validos
        resumen['Mes'] = pd.Categorical(resumen['Mes'], categories=orden_meses, ordered=True)
        resumen = resumen.sort_values('Mes')
        
        # --- SECCIÓN DE VISUALIZACIÓN ---
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.write("### 📋 Cuadro Detallado")
            st.dataframe(resumen.style.format({'COP': '{:,.0f}'}), use_container_width=True)
            
            st.write("### 📝 Explicación del Reporte")
            st.info("""
            Este tablero muestra la **proyección de costos operativos** en COP para el año 2026.
            - **Análisis:** Permite visualizar los meses con mayor carga financiera.
            - **Gráficos:** Identifican tendencias de crecimiento y distribución porcentual.
            """)

        with col2:
            st.write("### 📉 Gráficos de Análisis")
            
            # Gráfico de Barras
            fig_bar = px.bar(resumen, x='Mes', y='COP', title='Total Costos por Mes (Barras)', color='COP')
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # Gráfico de Líneas
            fig_line = px.line(resumen, x='Mes', y='COP', title='Tendencia de Costos (Línea)', markers=True)
            st.plotly_chart(fig_line, use_container_width=True)
            
            # Gráfico de Pastel
            fig_pie = px.pie(resumen, values='COP', names='Mes', title='Distribución Porcentual Anual')
            st.plotly_chart(fig_pie, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
        st.write("Verifica que las pestañas del Excel tengan los nombres correctos.")
