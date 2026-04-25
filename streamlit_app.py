import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Gestor Fiscal MERY", layout="wide")
st.title("📊 Asistente de Optimización Fiscal")

# Definición de pestañas
tab1, tab2, tab3 = st.tabs(["Carga de Datos", "Tabla de Resultados", "Análisis Visual"])

with tab1:
    uploaded_files = st.file_uploader("Sube tus archivos de Excel/CSV", accept_multiple_files=True)
    if uploaded_files:
        st.success(f"Archivos cargados: {len(uploaded_files)}")

# Inicializamos el dataframe vacío
df_final = pd.DataFrame()

if uploaded_files:
    data_list = []
    for file in uploaded_files:
        try:
            # Intentar leer como Excel, si falla, como CSV
            try:
                df = pd.read_excel(file, header=2)
            except:
                file.seek(0)
                df = pd.read_csv(file, header=2)
            
            # Limpieza
            df['COP'] = pd.to_numeric(df['COP'], errors='coerce')
            df_clean = df.dropna(subset=['ITEM', 'COP']).copy()
            df_clean['Mes'] = file.name.split(' - ')[-1].replace('.csv', '').replace('.xlsx', '')
            data_list.append(df_clean)
        except Exception as e:
            st.error(f"Error en {file.name}: {e}")
    
    if data_list:
        df_final = pd.concat(data_list, ignore_index=True)

with tab2:
    if not df_final.empty:
        resumen = df_final.groupby('Mes')['COP'].sum().reset_index()
        st.dataframe(resumen.style.format({'COP': '{:,.0f}'}), use_container_width=True)
    else:
        st.info("Sube archivos en la Pestaña 1 para ver resultados.")

with tab3:
    if not df_final.empty:
        resumen = df_final.groupby('Mes')['COP'].sum().reset_index()
        fig = px.bar(resumen, x='Mes', y='COP', title="Total COP por Mes")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos para graficar.")
