import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Asistente Financiero MERY", layout="wide")

st.title("📊 Asistente de Optimización Fiscal")
st.markdown("---")

# Carga de archivos (Configurado para .xlsx)
st.sidebar.header("Carga de Datos")
uploaded_files = st.sidebar.file_uploader("Sube tus archivos Excel (.xlsx)", type=["xlsx"], accept_multiple_files=True)

def procesar_excel(uploaded_files):
    lista_dataframes = []
    
    for file in uploaded_files:
        # Ignorar archivos temporales si los hubiera
        if file.name.startswith('~$'):
            continue
            
        try:
            # LEEMOS COMO EXCEL
            df = pd.read_excel(file, header=2) # header=2 porque tus datos empiezan en la fila 3
            
            # Extraer el mes del nombre del archivo
            nombre = file.name
            partes = nombre.split(' - ')
            mes = partes[1].split('.')[0] if len(partes) > 1 else "Mes"
            
            # Validar columnas
            if 'ITEM' in df.columns and 'COP' in df.columns:
                df_clean = df[['ITEM', 'COP']].copy()
                df_clean = df_clean.dropna(subset=['ITEM', 'COP'])
                df_clean['Mes'] = mes
                lista_dataframes.append(df_clean)
        except Exception as e:
            st.error(f"Error leyendo {file.name}: {e}")
            
    if not lista_dataframes:
        return None
        
    return pd.concat(lista_dataframes, ignore_index=True)

if uploaded_files:
    df_consolidado = procesar_excel(uploaded_files)
    
    if df_consolidado is not None:
        # Agrupar datos
        resumen = df_consolidado.groupby('Mes')['COP'].sum().reset_index()
        
        # --- VISUALIZACIÓN ---
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.write("### 📋 Cuadro de Resultados")
            st.dataframe(resumen.style.format({'COP': '{:,.0f}'}), use_container_width=True)
            
        with col2:
            tab1, tab2, tab3 = st.tabs(["Barras", "Líneas", "Pastel"])
            
            with tab1:
                fig_bar = px.bar(resumen, x='Mes', y='COP', title='Costos por Mes', color='COP')
                st.plotly_chart(fig_bar, use_container_width=True)
            with tab2:
                fig_line = px.line(resumen, x='Mes', y='COP', title='Tendencia', markers=True)
                st.plotly_chart(fig_line, use_container_width=True)
            with tab3:
                fig_pie = px.pie(resumen, values='COP', names='Mes', title='Distribución')
                st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("No se pudo procesar la información de los Excel.")
else:
    st.info("👈 Sube tus archivos Excel para comenzar.")
