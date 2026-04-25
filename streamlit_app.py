import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Gestor MERY", layout="wide")
st.title("📊 Asistente de Optimización Fiscal")

uploaded_files = st.file_uploader("Sube tus archivos", accept_multiple_files=True)

if uploaded_files:
    data_list = []
    
    for file in uploaded_files:
        try:
            # FORZAMOS: Saltamos las 2 filas de texto inicial y leemos desde la fila 3 (header=2)
            df = pd.read_csv(file, header=2)
            
            # Limpieza: Aseguramos que COP sea número
            df['COP'] = pd.to_numeric(df['COP'], errors='coerce')
            
            # Eliminamos filas donde ITEM o COP estén vacíos
            temp_df = df.dropna(subset=['ITEM', 'COP']).copy()
            
            # Asignamos el mes según el nombre del archivo
            temp_df['Mes'] = file.name.split(' - ')[-1].replace('.csv', '').replace('.xlsx', '')
            data_list.append(temp_df)
            
        except Exception as e:
            st.error(f"Error en {file.name}: {e}")

    if data_list:
        df_final = pd.concat(data_list, ignore_index=True)
        
        # Agrupación para el gráfico
        resumen = df_final.groupby('Mes')['COP'].sum().reset_index()
        
        # Mostrar tabla
        st.subheader("Datos consolidados")
        st.dataframe(resumen, use_container_width=True)
        
        # Gráfico OBLIGATORIO
        if not resumen.empty:
            st.subheader("Gráfico de Costos")
            fig = px.bar(resumen, x='Mes', y='COP', title="Total COP por Mes")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Los archivos se cargaron pero no tienen datos numéricos válidos en la columna COP.")
    else:
        st.error("No se pudo extraer información.")
else:
    st.info("Sube tus archivos para comenzar.")
                
            with tab3:
                fig_pie = px.pie(resumen, values='COP', names='Mes', title='Distribución Porcentual Anual')
                st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.error("No se pudo extraer información válida de los archivos CSV.")
else:
    st.info("👈 Por favor, sube los archivos CSV desde la barra lateral para comenzar el análisis.")
